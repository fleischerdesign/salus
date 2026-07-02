import math
import random
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.open_science import OpenScienceSynthesizeRequest

if TYPE_CHECKING:
    from salus.models.measurement import Measurement  # noqa: F401


class OpenScienceService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def sample_laplace(self, loc: float, scale: float) -> float:
        """
        Draws a sample from a Laplace distribution using Inverse Transform Sampling.
        Mathematical formula: X = loc - scale * sgn(u) * ln(1 - 2*|u|) where u in (-0.5, 0.5]
        """
        if scale <= 0.0:
            return 0.0
        u = random.random() - 0.5
        sgn = 1.0 if u >= 0 else -1.0
        return loc - scale * sgn * math.log(1.0 - 2.0 * abs(u))

    def synthesize(self, user_id: int, req: OpenScienceSynthesizeRequest) -> dict[str, Any]:
        """
        Aggregates metrics by week, applies demographic binning, and adds Laplace noise
        to implement Local Differential Privacy (LDP) for research data donation.
        """
        # Sensitivity settings (delta f) representing maximum daily change divided by 7 days
        sensitivities = {
            "steps": 2142.0,                # Max 15,000 steps per day variation / 7
            "sleep_duration": 7200.0,        # Max 14 hours sleep variation in seconds / 7
            "resting_heart_rate": 17.0,     # Max 120 bpm variation / 7
            "active_calories": 285.0,       # Max 2000 kcal variation / 7
        }

        # 1. Fetch metrics from the past N weeks
        start_date = datetime.now(timezone.utc) - timedelta(weeks=req.weeks)
        
        with self.uow:
            # Query all metric types owned by the user
            metric_types = self.uow.metric_types.find_all(user_id)
            
            # Build case-insensitive mapping: e.g., "steps" -> MetricType
            metric_map = {mt.name.lower(): mt for mt in metric_types if mt.id is not None}
            
            # Map common variants to pre-seeded metric types
            aliases = {
                "sleep_duration": "sleep",
                "resting_heart_rate": "heart rate",
                "active_calories": "exercise",
            }

            weekly_data: dict[str, dict[str, list[float]]] = {}

            for metric_name in req.metrics:
                normalized_name = aliases.get(metric_name, metric_name).lower()
                mt = metric_map.get(normalized_name)
                if not mt:
                    continue
                
                print("DEBUG: found mt = ", mt.name, "id =", mt.id)
                # Fetch raw measurements
                measurements = self.uow.measurements.find_by_metric_type(
                    metric_type_id=mt.id,  # type: ignore
                    user_id=user_id,
                )
                print("DEBUG: measurements count =", len(measurements))
                for m in measurements:
                    print("DEBUG: m id =", m.id, "m.start_time =", m.start_time, "m.value_numeric =", m.value_numeric, "m.user_id =", m.user_id, "m.metric_type_id =", m.metric_type_id)
                
                for m in measurements:
                    if m.start_time.replace(tzinfo=timezone.utc) < start_date:
                        continue
                    
                    # Group by ISO week: "YYYY-Www"
                    year, week, _ = m.start_time.isocalendar()
                    week_key = f"{year}-W{week:02d}"
                    
                    if m.value_numeric is not None:
                        weekly_data.setdefault(week_key, {}).setdefault(metric_name, []).append(float(m.value_numeric))

            # 2. Aggregate and apply Differential Privacy
            synthesized_records = []
            for week_key in sorted(weekly_data.keys()):
                record: dict[str, Any] = {"week": week_key}
                
                for metric_name in req.metrics:
                    values = weekly_data[week_key].get(metric_name, [])
                    if not values:
                        continue
                    
                    raw_average = sum(values) / len(values)
                    
                    # Calculate noise scale (b = sensitivity / epsilon)
                    sensitivity = sensitivities.get(metric_name, 1.0)
                    scale = sensitivity / req.epsilon
                    
                    # Add Laplace noise
                    noise = self.sample_laplace(0.0, scale)
                    noisy_value = raw_average + noise
                    
                    # Ensure positive bounds
                    record[metric_name] = max(0.0, noisy_value)
                    
                if len(record) > 1:  # Contains more than just the week key
                    synthesized_records.append(record)

            # 3. Demographic Binning
            demographics = {}
            if req.include_demographics:
                if req.user_birth_year:
                    current_year = datetime.now().year
                    age = current_year - req.user_birth_year
                    age_bin = f"{age // 10 * 10}-{age // 10 * 10 + 9}"
                    demographics["age_group"] = age_bin
                if req.user_weight_kg:
                    w_bin_start = int(req.user_weight_kg // 5 * 5)
                    demographics["weight_group"] = f"{w_bin_start}-{w_bin_start + 4} kg"

            return {
                "dataset_version": "1.0",
                "demographics": demographics,
                "records": synthesized_records,
                "differential_privacy": {
                    "epsilon": req.epsilon,
                    "noise_distribution": "Laplace",
                }
            }
