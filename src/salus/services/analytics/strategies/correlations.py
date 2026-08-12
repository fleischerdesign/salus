"""Cross-metric correlation strategy with FDR correction."""
from datetime import datetime, timedelta, timezone

from salus.schemas.analytics import CorrelationMatrixResponse, CorrelationModel
from salus.services.analytics.stats import benjamini_hochberg, pearson
from salus.services.analytics.strategies._helpers import interpret_cohens
from salus.services.analytics.strategies.context import AnalyticsContext

RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


class CorrelationsStrategy:
    def compute(
        self,
        ctx: AnalyticsContext,
        user_id: str,
        range_key: str = "90d",
        min_n: int = 14,
    ) -> CorrelationMatrixResponse:
        days = RANGE_DAYS.get(range_key, 90)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        repo = ctx.uow.measurements
        records = repo.find_all(user_id=user_id, since=since)
        if not records:
            return CorrelationMatrixResponse(
                pairs=[], n_comparisons=0, correction="Benjamini-Hochberg FDR",
                min_n=min_n, range_key=range_key,
            )
        metric_defs = ctx.uow.metric_definitions.find_all()
        type_map = {md.code: md.name for md in metric_defs}
        pivot: dict[str, list[float]] = {}
        for m in records:
            if m.value_numeric is None:
                continue
            name = type_map.get(m.metric_code or "", m.data_type)
            if name not in pivot:
                pivot[name] = []
            pivot[name].append(m.value_numeric)
        metrics = [name for name, vals in pivot.items() if len(vals) >= min_n]
        pairs: list[CorrelationModel] = []
        for i, ma in enumerate(metrics):
            for mb in metrics[i + 1:]:
                xs = pivot[ma]
                ys = pivot[mb]
                pr = pearson(xs, ys)
                if pr is None:
                    continue
                pairs.append(
                    CorrelationModel(
                        metric_a=ma,
                        metric_b=mb,
                        pearson_r=round(pr.r, 4),
                        pearson_p=round(pr.p_value, 4),
                        spearman_r=0.0,
                        spearman_p=0.0,
                        p_adjusted_bh=1.0,
                        effect_size_d=round(abs(pr.r), 4),
                        ci_95_lower=round(pr.ci_lower, 4),
                        ci_95_upper=round(pr.ci_upper, 4),
                        n=pr.n,
                        interpretation="",
                    )
                )
        if pairs:
            p_values = [p.pearson_p for p in pairs]
            fdr = benjamini_hochberg(p_values)
            pairs = [
                CorrelationModel(
                    metric_a=p.metric_a,
                    metric_b=p.metric_b,
                    pearson_r=p.pearson_r,
                    pearson_p=p.pearson_p,
                    spearman_r=p.spearman_r,
                    spearman_p=p.spearman_p,
                    p_adjusted_bh=round(fdr.adjusted[i], 4),
                    effect_size_d=p.effect_size_d,
                    ci_95_lower=p.ci_95_lower,
                    ci_95_upper=p.ci_95_upper,
                    n=p.n,
                    interpretation=interpret_cohens(p.effect_size_d),
                )
                for i, p in enumerate(pairs)
            ]
        return CorrelationMatrixResponse(
            pairs=pairs,
            n_comparisons=len(pairs),
            correction="Benjamini-Hochberg FDR",
            min_n=min_n,
            range_key=range_key,
        )
