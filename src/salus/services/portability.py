import io
import zipfile
import json
import csv
from datetime import datetime

from salus.repositories.unit_of_work import IUnitOfWork
from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models.workout import WorkoutPlan, WorkoutPlanExercise


class DataPortabilityService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def export_user_data(self, user_id: str) -> io.BytesIO:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Profile Data
            user = self.uow.users.get_by_id(user_id)
            if user:
                profile_data = {
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name,
                    "theme": user.theme,
                }
                zip_file.writestr(
                    "profile.json",
                    json.dumps(profile_data, indent=2, ensure_ascii=False)
                )

            # 2. Measurements (CSV)
            measurements = self.uow.measurements.find_all(user_id=user_id)
            
            csv_buffer = io.StringIO()
            csv_writer = csv.writer(csv_buffer)
            csv_writer.writerow([
                "source", "data_type", "metric_code", "value_numeric",
                "value_text", "value_json", "start_time", "end_time", "notes", "external_id"
            ])
            for m in measurements:
                csv_writer.writerow([
                    m.source, m.data_type, m.metric_code, m.value_numeric,
                    m.value_text or "", m.value_json or "",
                    m.start_time.isoformat(),
                    m.end_time.isoformat() if m.end_time else "",
                    m.notes or "", m.external_id or ""
                ])
            zip_file.writestr("measurements.csv", csv_buffer.getvalue())

            # 3. Workout Plans (JSON)
            plans = self.uow.workout_plans.find_by_user(user_id)
            plans_data = []
            for p in plans:
                plan_exercises = []
                for pe in p.plan_exercises:
                    plan_exercises.append({
                        "exercise_name": pe.exercise.name,
                        "sequence": pe.sequence,
                        "target_sets": pe.target_sets,
                        "target_reps": pe.target_reps,
                        "target_rpe": pe.target_rpe,
                        "is_autoreg_exempt": pe.is_autoreg_exempt,
                        "rest_seconds": pe.rest_seconds,
                    })
                plans_data.append({
                    "name": p.name,
                    "description": p.description,
                    "autoreg_mode": p.autoreg_mode,
                    "position": p.position,
                    "exercises": plan_exercises,
                })
            zip_file.writestr(
                "workout_plans.json",
                json.dumps(plans_data, indent=2, ensure_ascii=False)
            )

            # 4. Workout History (CSV)
            sessions = self.uow.workout_sessions.find_all_by_user(user_id)
            
            history_buffer = io.StringIO()
            history_writer = csv.writer(history_buffer)
            history_writer.writerow([
                "session_id", "started_at", "completed_at", "plan_name",
                "exercise_name", "set_number", "weight", "reps", "rpe"
            ])
            for s in sessions:
                plan_name = s.plan.name if s.plan else "Custom Workout"
                for entry in s.logs:
                    history_writer.writerow([
                        s.id,
                        s.started_at.isoformat(),
                        s.completed_at.isoformat() if s.completed_at else "",
                        plan_name,
                        entry.exercise.name,
                        entry.set_number,
                        entry.weight,
                        entry.reps,
                        entry.rpe or ""
                    ])
            zip_file.writestr("workout_history.csv", history_buffer.getvalue())

            # 5. Goals (JSON)
            goals = self.uow.goals.find_by_user(user_id)
            goals_data = []
            for g in goals:
                metric_def = self.uow.metric_definitions.find_by_code(g.metric_code) if g.metric_code else None
                metric_name = metric_def.name if metric_def else ""
                goals_data.append({
                    "metric_type_name": metric_name,
                    "target_value": g.target_value,
                    "direction": g.direction,
                    "frequency": g.frequency,
                    "deadline": g.deadline.isoformat() if g.deadline else None,
                    "is_active": g.is_active,
                    "created_at": g.created_at.isoformat(),
                })
            zip_file.writestr(
                "goals.json",
                json.dumps(goals_data, indent=2, ensure_ascii=False)
            )

        zip_buffer.seek(0)
        return zip_buffer

    def import_user_data(self, user_id: str, zip_bytes: bytes) -> dict:
        results = {
            "measurements_imported": 0,
            "plans_imported": 0,
            "goals_imported": 0,
            "errors": []
        }
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_file:
                # 1. Profile Data Import
                if "profile.json" in zip_file.namelist():
                    try:
                        profile_data = json.loads(zip_file.read("profile.json").decode("utf-8"))
                        user = self.uow.users.get_by_id(user_id)
                        if user:
                            if "theme" in profile_data:
                                user.theme = profile_data["theme"]
                            self.uow.session.add(user)
                    except Exception as e:
                        results["errors"].append(f"Failed to import profile: {str(e)}")

                # 2. Measurements Import
                if "measurements.csv" in zip_file.namelist():
                    try:
                        csv_data = zip_file.read("measurements.csv").decode("utf-8")
                        csv_reader = csv.DictReader(io.StringIO(csv_data))
                        
                        existing_records = self.uow.measurements.find_all(user_id=user_id)
                        existing_keys = {
                            (r.start_time.isoformat(), r.metric_code, float(r.value_numeric) if r.value_numeric is not None else 0.0)
                            for r in existing_records
                        }
                        
                        for row in csv_reader:
                            start_time = datetime.fromisoformat(row["start_time"])
                            metric_code = row["metric_code"]
                            value_numeric = float(row["value_numeric"])
                            
                            key = (start_time.isoformat(), metric_code, value_numeric)
                            if key in existing_keys:
                                continue
                                
                            end_time = datetime.fromisoformat(row["end_time"]) if row.get("end_time") else None
                            m = Measurement(
                                user_id=user_id,
                                source=row["source"],
                                data_type=row["data_type"],
                                metric_code=metric_code,
                                value_numeric=value_numeric,
                                value_text=row.get("value_text") or None,
                                value_json=row.get("value_json") or None,
                                start_time=start_time,
                                end_time=end_time,
                                notes=row.get("notes") or None,
                                external_id=row.get("external_id") or None,
                            )
                            self.uow.session.add(m)
                            results["measurements_imported"] += 1
                    except Exception as e:
                        results["errors"].append(f"Failed to import measurements: {str(e)}")

                # 3. Workout Plans Import
                if "workout_plans.json" in zip_file.namelist():
                    try:
                        plans_data = json.loads(zip_file.read("workout_plans.json").decode("utf-8"))
                        
                        existing_plans = self.uow.workout_plans.find_by_user(user_id)
                        existing_plan_names = {p.name for p in existing_plans}
                        
                        for p_data in plans_data:
                            if p_data["name"] in existing_plan_names:
                                continue
                                
                            plan = WorkoutPlan(
                                name=p_data["name"],
                                description=p_data.get("description"),
                                user_id=user_id,
                                autoreg_mode=p_data.get("autoreg_mode", "advisory"),
                                position=p_data.get("position", 0),
                            )
                            self.uow.session.add(plan)
                            self.uow.session.flush()
                            
                            for ex_data in p_data.get("exercises", []):
                                exercise = self.uow.exercises.find_by_name(ex_data["exercise_name"])
                                if exercise:
                                    pe = WorkoutPlanExercise(
                                        plan_id=plan.id,  # type: ignore
                                        exercise_id=exercise.id,  # type: ignore
                                        sequence=ex_data["sequence"],
                                        target_sets=ex_data["target_sets"],
                                        target_reps=ex_data["target_reps"],
                                        target_rpe=ex_data.get("target_rpe", 8.0),
                                        is_autoreg_exempt=ex_data.get("is_autoreg_exempt", False),
                                        rest_seconds=ex_data.get("rest_seconds"),
                                    )
                                    self.uow.session.add(pe)
                            results["plans_imported"] += 1
                    except Exception as e:
                        results["errors"].append(f"Failed to import workout plans: {str(e)}")

                # 4. Goals Import
                if "goals.json" in zip_file.namelist():
                    try:
                        goals_data = json.loads(zip_file.read("goals.json").decode("utf-8"))
                        existing_goals = self.uow.goals.find_by_user(user_id)

                        metric_defs = self.uow.metric_definitions.find_all()
                        metric_type_map = {md.name: md.code for md in metric_defs}
                        
                        for g_data in goals_data:
                            metric_code = metric_type_map.get(g_data["metric_type_name"])
                            if not metric_code:
                                continue
                                
                            created_at = datetime.fromisoformat(g_data["created_at"])
                            
                            is_duplicate = any(
                                eg.metric_code == metric_code and 
                                eg.created_at.date() == created_at.date() and 
                                float(eg.target_value) == float(g_data["target_value"])
                                for eg in existing_goals
                            )
                            if is_duplicate:
                                continue
                                
                            deadline = None
                            if g_data.get("deadline"):
                                from datetime import date
                                deadline = date.fromisoformat(g_data["deadline"])
                                
                            goal = Goal(
                                user_id=user_id,
                                metric_code=metric_code,
                                target_value=float(g_data["target_value"]),
                                direction=g_data.get("direction", "increase"),
                                frequency=g_data.get("frequency", "daily"),
                                deadline=deadline,
                                is_active=g_data.get("is_active", True),
                                created_at=created_at,
                            )
                            self.uow.session.add(goal)
                            results["goals_imported"] += 1
                    except Exception as e:
                        results["errors"].append(f"Failed to import goals: {str(e)}")

                self.uow.commit()
                
        except Exception as e:
            results["errors"].append(f"Invalid ZIP file structure: {str(e)}")
            
        return results
