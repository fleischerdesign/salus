import logging
from datetime import datetime, timedelta

from salus.models.insight import Insight
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import parse_date
from salus.services.analytics.stats import (
    change_point_pelt,
    mann_kendall,
    pearson,
    sleep_debt_cumulative,
)
from salus.services.insight.providers.base import ILlmProvider
from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.services.insight")


class InsightService:
    def __init__(
        self,
        uow: IUnitOfWork,
        provider: ILlmProvider,
        model: str,
        registry: HookRegistry | None = None,
    ) -> None:
        self._uow = uow
        self._provider = provider
        self._model = model
        self._registry = registry

    def get_insight_for_date(self, user_id: str, date_str: str) -> Insight | None:
        """Retrieves a previously cached insight if it exists."""
        return self._uow.insights.find_by_user_and_date(user_id, date_str)

    def list_history(self, user_id: str, limit: int = 30) -> list[Insight]:
        """Returns recent insights for the user, newest first."""
        return self._uow.insights.list_by_user(user_id, limit=limit)

    def _build_analytics_context(
        self,
        daily_logs: dict[str, dict[str, list[float]]],
        goals,
        metric_map: dict,
    ) -> str:
        lines: list[str] = []
        all_days = sorted(daily_logs.keys())

        if len(all_days) < 3:
            return "Insufficient data for statistical analysis."

        flat: dict[str, list[float]] = {}
        for day in all_days:
            for name, vals in daily_logs[day].items():
                if name not in flat:
                    flat[name] = []
                flat[name].extend(vals)

        for name, vals in flat.items():
            if len(vals) < 3:
                continue
            mk = mann_kendall(vals)
            if mk and mk.trend != "none":
                direction = "↑" if mk.trend == "increasing" else "↓"
                lines.append(
                    f"- {name}: {direction} trend (p={mk.p_value:.4f}, tau={mk.tau:.3f}, n={mk.n})."
                )

        metric_keys = sorted(flat.keys())
        for i, ma in enumerate(metric_keys):
            for mb in metric_keys[i + 1 :]:
                xs = flat[ma]
                ys = flat[mb]
                n = min(len(xs), len(ys))
                if n < 5:
                    continue
                corr = pearson(xs[:n], ys[:n])
                if corr and abs(corr.r) > 0.3 and corr.p_value < 0.10:
                    sign = "positive" if corr.r > 0 else "negative"
                    lines.append(
                        f"- {ma} ↔ {mb}: {sign} correlation (r={corr.r:.3f}, p={corr.p_value:.4f}, n={n})."
                    )

        sleep_vals = flat.get("Sleep", [])
        if len(sleep_vals) >= 5:
            debt = sleep_debt_cumulative(sleep_vals, 30)
            last_debt = debt.debt[-1]
            direction = "deficit" if last_debt > 0 else "surplus"
            lines.append(
                f"- Cumulative sleep debt: {last_debt:+.1f}h {direction} vs. {debt.baseline_h}h baseline (n={len(sleep_vals)})."
            )

        weight_vals = flat.get("Weight", [])
        if len(weight_vals) >= 7:
            cps = change_point_pelt(weight_vals, "BIC")
            if cps and cps["indices"]:
                idx_list = cps["indices"]
                lines.append(
                    f"- Weight changepoints detected at day indices: {idx_list}."
                )

        if lines:
            lines.insert(
                0, "Pre-computed statistical findings (use as ground truth):"
            )
            lines.append(
                "Cite p-values and effect sizes where relevant. "
                "If a finding is borderline (p 0.05–0.10), "
                "present it as exploratory, not conclusive."
            )
        return "\n".join(lines) if lines else "No statistically significant patterns detected (insufficient data)."

    def generate_daily_insight(
        self, user_id: str, date_str: str, locale: str = "en"
    ) -> Insight:
        """Generates, saves, and returns a personalized health insight for the user on a specific day."""
        # 1. Return cached insight if already present
        existing = self.get_insight_for_date(user_id, date_str)
        if existing is not None:
            logger.info(
                "Returning cached daily insight for user %s on date %s",
                user_id,
                date_str,
            )
            return existing

        # 2. Parse query date
        parsed = parse_date(date_str)
        if parsed is not None:
            query_date = datetime.combine(parsed, datetime.min.time())
        else:
            query_date = datetime.today()
            date_str = query_date.strftime("%Y-%m-%d")

        # 3. Retrieve metric types, goals, and measurements
        metric_types = self._uow.metric_types.find_all(user_id=user_id)
        metric_map = {mt.id: mt for mt in metric_types if mt.id is not None}

        # Fetch last 7 days of history for context
        since = query_date - timedelta(days=7)
        until = query_date + timedelta(days=1)
        measurements = self._uow.measurements.find_all(
            user_id=user_id, since=since, until=until
        )

        goals = self._uow.goals.find_by_user(user_id=user_id)

        # 4. Format data for the prompt
        # Group measurements by date and metric name
        daily_logs: dict[str, dict[str, list[float]]] = {}
        for m in measurements:
            if m.start_time is None:
                continue
            day_key = m.start_time.strftime("%Y-%m-%d")
            metric_type = (
                metric_map.get(m.metric_type_id)
                if m.metric_type_id is not None
                else None
            )
            metric_name = metric_type.name if metric_type else m.data_type

            if day_key not in daily_logs:
                daily_logs[day_key] = {}
            if metric_name not in daily_logs[day_key]:
                daily_logs[day_key][metric_name] = []

            if m.value_numeric is not None:
                daily_logs[day_key][metric_name].append(m.value_numeric)

        # Prepare summary of logs
        history_lines = []
        for day in sorted(daily_logs.keys(), reverse=True):
            day_metrics = daily_logs[day]
            metrics_summary = []
            for name, vals in day_metrics.items():
                if vals:
                    # Calculate sum or average based on type
                    val_str = (
                        f"{sum(vals):.1f}"
                        if name.lower() in ("steps", "water", "calories")
                        else f"{sum(vals) / len(vals):.1f}"
                    )
                    metrics_summary.append(f"{name}: {val_str}")
            history_lines.append(f"- {day}: {', '.join(metrics_summary)}")

        history_context = (
            "\n".join(history_lines)
            if history_lines
            else "No measurements logged in the last 7 days."
        )

        analytics_context = self._build_analytics_context(
            daily_logs, goals, metric_map
        )

        # Format goals summary
        goals_lines = []
        for g in goals:
            mt = (
                metric_map.get(g.metric_type_id)
                if g.metric_type_id is not None
                else None
            )
            mt_name = mt.name if mt else "Unknown"
            goals_lines.append(
                f"- Target: {g.direction.value} {mt_name} to {g.target_value} ({g.frequency.value})"
            )
        goals_context = (
            "\n".join(goals_lines) if goals_lines else "No active goals configured."
        )

        # 5. Build prompts
        system_instruction = (
            "You are Salus Coach, an elite clinical health coach, sleep specialist, and metabolic researcher.\n"
            "Analyze the user's vitals, activity history, sleep patterns, nutrition, and goals.\n"
            "Write a concise, high-impact daily health insight.\n"
            "Requirements:\n"
            "- Acknowledge key achievements (e.g. target milestones, recovery peaks).\n"
            "- Analyze recovery (sleep duration/stages, resting heart rate) against training volume.\n"
            "- Provide exactly 2 actionable, science-based recommendations for tomorrow.\n"
            "- Format output using clean Markdown (headings, bold text, bullet points).\n"
            "- Do NOT write introductory filler or closing signatures.\n"
            f"- Translate your entire response to German if the language code is 'de', otherwise respond in English. Current locale: '{locale}'."
        )

        user_prompt = (
            f"Here is my biometric and health log history leading up to {date_str}:\n\n"
            f"### Active Goals:\n{goals_context}\n\n"
            f"### Pre-computed Analytics (statistically validated):\n{analytics_context}\n\n"
            f"### Measurement History (Last 7 days):\n{history_context}\n\n"
        )

        # Collect additional context from plugins
        plugin_contexts = []
        if self._registry:
            for hook in self._registry.ai_coach_contexts:
                try:
                    p_ctx = hook.get_additional_prompt_context(user_id, date_str)
                    if p_ctx:
                        plugin_contexts.append(p_ctx)
                except Exception as e:
                    logger.error(
                        "Error fetching AI Coach Context from plugin: %s",
                        str(e),
                        exc_info=True,
                    )

        if plugin_contexts:
            plugin_context_str = "\n\n".join(plugin_contexts)
            user_prompt += f"### Additional Context:\n{plugin_context_str}\n\n"

        user_prompt += "Analyze my data and generate the daily health insight."

        # 6. Generate content from provider
        try:
            logger.info(
                "Generating LLM health insight with model %s for date %s",
                self._model,
                date_str,
            )
            content = self._provider.generate_insight(
                prompt=user_prompt,
                system_instruction=system_instruction,
                model=self._model,
            )
        except Exception as e:
            logger.error("LLM Generation failed: %s", str(e), exc_info=True)
            # Fallback message
            if locale == "de":
                content = (
                    "### ⚠️ Verbindung zum Gesundheitscoach fehlgeschlagen\n"
                    "Wir konnten keine Verbindung zum KI-Modell herstellen. Bitte überprüfe deine LLM-Konfiguration in den Systemeinstellungen."
                )
            else:
                content = (
                    "### ⚠️ Connection to Health Coach Failed\n"
                    "We were unable to connect to the KI service. Please verify your LLM settings in the admin panel."
                )

        # 7. Persist and return the insight
        insight = Insight(
            user_id=user_id,
            query_date=date_str,
            content=content,
            model_used=self._model,
        )

        with self._uow:
            self._uow.insights.add(insight)

        return insight
