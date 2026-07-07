from typing import Optional
from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from salus.dependencies import get_current_user, get_workout_service
from salus.models.user import User
from salus.schemas.workout import (
    ExerciseCreate,
    ExerciseResponse,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutPlanExerciseCreate,
    WorkoutLogEntryCreate,
    WorkoutLogEntryResponse,
    WorkoutSessionResponse,
)
from salus.services.workout.planner import WorkoutService
from salus.services._helpers import uid

router = APIRouter(tags=["Workouts"])

# --------------------------------------------------------------------------
# HTML Page Handlers
# --------------------------------------------------------------------------


@router.get("/workouts", response_class=HTMLResponse)
async def workouts_redirect(request: Request):
    return RedirectResponse("/workouts/plans", status_code=303)


@router.get("/workouts/plans", response_class=HTMLResponse)
async def workouts_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    user_id = uid(current_user)
    plans = service.list_plans(user_id)
    exercises = service.get_exercise_catalog(user_id)
    recent_sessions = service.get_recent_sessions(user_id, limit=5)
    active_session = service.get_active_session(user_id)

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/workouts.html",
        {
            "current_user": current_user,
            "plans": plans,
            "exercises": exercises,
            "recent_sessions": recent_sessions,
            "active_session": active_session,
        },
    )


@router.get("/workouts/plans/new", response_class=HTMLResponse)
async def new_plan_modal(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    user_id = uid(current_user)
    exercises = service.get_exercise_catalog(user_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/plan_form.html",
        {
            "current_user": current_user,
            "exercises": exercises,
        },
    )


@router.post("/workouts/plans", response_class=HTMLResponse)
async def workouts_create_plan_post(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    autoreg_mode: str = Form("advisory"),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    form_data = await request.form()
    exercises = []
    
    # Extract dynamic indices from form keys (e.g. exercise_0, exercise_2)
    form_keys = form_data.keys()
    indices = []
    for k in form_keys:
        if k.startswith("exercise_"):
            try:
                indices.append(int(k.split("_")[1]))
            except ValueError:
                pass
    indices.sort()
    
    for seq, idx in enumerate(indices):
        ex_id_str = form_data.get(f"exercise_{idx}")
        if ex_id_str:
            ex_id = int(str(ex_id_str))
            sets = int(str(form_data.get(f"sets_{idx}", "3")))
            reps = int(str(form_data.get(f"reps_{idx}", "8")))
            rpe_val = form_data.get(f"rpe_{idx}")
            rpe = float(str(rpe_val)) if rpe_val else 8.0
            lock = bool(form_data.get(f"lock_{idx}"))

            exercises.append(
                WorkoutPlanExerciseCreate(
                    exercise_id=ex_id,
                    sequence=seq,
                    target_sets=sets,
                    target_reps=reps,
                    target_rpe=rpe,
                    is_autoreg_exempt=lock,
                )
            )

    plan_data = WorkoutPlanCreate(
        name=name,
        description=description,
        autoreg_mode=autoreg_mode,
        exercises=exercises,
    )
    service.create_plan(user_id=uid(current_user), data=plan_data)
    return RedirectResponse("/workouts/plans", status_code=303)


@router.get("/workouts/plans/{plan_id}/edit", response_class=HTMLResponse)
async def edit_plan_modal(
    request: Request,
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    user_id = uid(current_user)
    plan = service.get_plan(user_id, plan_id)
    exercises = service.get_exercise_catalog(user_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/plan_form.html",
        {
            "current_user": current_user,
            "exercises": exercises,
            "plan": plan,
        },
    )


@router.post("/workouts/plans/{plan_id}", response_class=HTMLResponse)
async def workouts_update_plan_post(
    request: Request,
    plan_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    autoreg_mode: str = Form("advisory"),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    form_data = await request.form()
    exercises = []
    
    # Extract dynamic indices from form keys
    form_keys = form_data.keys()
    indices = []
    for k in form_keys:
        if k.startswith("exercise_"):
            try:
                indices.append(int(k.split("_")[1]))
            except ValueError:
                pass
    indices.sort()
    
    for seq, idx in enumerate(indices):
        ex_id_str = form_data.get(f"exercise_{idx}")
        if ex_id_str:
            ex_id = int(str(ex_id_str))
            sets = int(str(form_data.get(f"sets_{idx}", "3")))
            reps = int(str(form_data.get(f"reps_{idx}", "8")))
            rpe_val = form_data.get(f"rpe_{idx}")
            rpe = float(str(rpe_val)) if rpe_val else 8.0
            lock = bool(form_data.get(f"lock_{idx}"))

            exercises.append(
                WorkoutPlanExerciseCreate(
                    exercise_id=ex_id,
                    sequence=seq,
                    target_sets=sets,
                    target_reps=reps,
                    target_rpe=rpe,
                    is_autoreg_exempt=lock,
                )
            )

    plan_data = WorkoutPlanCreate(
        name=name,
        description=description,
        autoreg_mode=autoreg_mode,
        exercises=exercises,
    )
    service.update_plan(user_id=uid(current_user), plan_id=plan_id, data=plan_data)
    return RedirectResponse("/workouts/plans", status_code=303)


@router.post("/workouts/plans/reorder")
async def reorder_plans(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    form_data = await request.form()
    ids_str = form_data.get("ids")
    if ids_str:
        ordered = [int(x) for x in str(ids_str).split(",") if x.strip()]
        service.reorder_plans(uid(current_user), ordered)
    from fastapi import Response
    return Response(status_code=204)


@router.get("/workouts/exercises", response_class=HTMLResponse)
async def list_exercises_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    user_id = uid(current_user)
    exercises = service.get_exercise_catalog(user_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/exercises.html",
        {
            "current_user": current_user,
            "exercises": exercises,
        },
    )


@router.get("/workouts/exercises/new", response_class=HTMLResponse)
async def new_exercise_modal(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return request.app.state.templates.TemplateResponse(
        request,
        "components/exercise_form.html",
        {
            "current_user": current_user,
        },
    )


@router.post("/workouts/exercises", response_class=HTMLResponse)
async def workouts_create_exercise_post(
    name: str = Form(...),
    equipment: str = Form("barbell"),
    primary_muscles: str = Form(...),
    secondary_muscles: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    instructions: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    ex_data = ExerciseCreate(
        name=name,
        equipment=equipment,
        primary_muscles=primary_muscles,
        secondary_muscles=secondary_muscles,
        description=description,
        instructions=instructions,
        video_url=video_url,
    )
    try:
        service.create_exercise(user_id=uid(current_user), data=ex_data)
    except ValueError:
        pass
    return RedirectResponse("/workouts/exercises", status_code=303)


@router.get("/workouts/exercises/{exercise_id}/edit", response_class=HTMLResponse)
async def edit_exercise_modal(
    request: Request,
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    from salus.exceptions import NotFoundError
    ex = service.get_exercise(exercise_id)
    if not ex:
        raise NotFoundError("Exercise not found.")
    if ex.user_id != uid(current_user):
        raise PermissionError("Cannot edit system default exercise.")
    
    return request.app.state.templates.TemplateResponse(
        request,
        "components/exercise_form.html",
        {
            "current_user": current_user,
            "exercise": ex,
            "is_edit": True,
        },
    )


@router.post("/workouts/exercises/{exercise_id}", response_class=HTMLResponse)
async def workouts_update_exercise_post(
    exercise_id: int,
    name: str = Form(...),
    equipment: str = Form("barbell"),
    primary_muscles: str = Form(...),
    secondary_muscles: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    instructions: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    ex_data = ExerciseCreate(
        name=name,
        equipment=equipment,
        primary_muscles=primary_muscles,
        secondary_muscles=secondary_muscles,
        description=description,
        instructions=instructions,
        video_url=video_url,
    )
    try:
        service.update_exercise(user_id=uid(current_user), exercise_id=exercise_id, data=ex_data)
    except ValueError:
        pass
    return RedirectResponse("/workouts/exercises", status_code=303)


@router.post("/workouts/sessions/start", response_class=HTMLResponse)
async def start_session_post(
    plan_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.start_session(user_id=uid(current_user), plan_id=plan_id)
    return RedirectResponse("/workouts/sessions/active", status_code=303)


@router.get("/workouts/sessions/active", response_class=HTMLResponse)
async def active_session_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    user_id = uid(current_user)
    active_session = service.get_active_session(user_id)
    if not active_session:
        return RedirectResponse("/workouts/plans", status_code=303)

    targets = []
    if active_session.plan_id:
        targets = service.get_session_targets(user_id, active_session.plan_id)

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/workout_active.html",
        {
            "current_user": current_user,
            "session": active_session,
            "targets": targets,
        },
    )


@router.post("/workouts/sessions/complete", response_class=HTMLResponse)
async def complete_session_post(
    session_id: int = Form(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.complete_session(
        user_id=uid(current_user), session_id=session_id, notes=notes
    )
    return RedirectResponse("/workouts/plans", status_code=303)


# --------------------------------------------------------------------------
# API JSON Handlers
# --------------------------------------------------------------------------


@router.get("/api/v1/workouts/exercises", response_model=list[ExerciseResponse])
async def list_exercises(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_exercise_catalog(user_id=uid(current_user))


@router.post(
    "/api/v1/workouts/exercises",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise(
    data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    try:
        return service.create_exercise(user_id=uid(current_user), data=data)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})


@router.delete(
    "/api/v1/workouts/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    try:
        service.delete_exercise(user_id=uid(current_user), exercise_id=exercise_id)
    except PermissionError as e:
        return JSONResponse(status_code=403, content={"detail": str(e)})


@router.post(
    "/api/v1/workouts/plans",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.create_plan(user_id=uid(current_user), data=data)


@router.get("/api/v1/workouts/plans", response_model=list[WorkoutPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.list_plans(user_id=uid(current_user))


@router.get("/api/v1/workouts/plans/{plan_id}", response_model=WorkoutPlanResponse)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_plan(user_id=uid(current_user), plan_id=plan_id)


@router.delete(
    "/api/v1/workouts/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_plan(user_id=uid(current_user), plan_id=plan_id)


@router.get("/api/v1/workouts/plans/{plan_id}/targets")
async def get_plan_targets(
    plan_id: int,
    date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_session_targets(
        user_id=uid(current_user), plan_id=plan_id, date_str=date
    )


@router.post("/api/v1/workouts/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(
    plan_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.start_session(user_id=uid(current_user), plan_id=plan_id)


@router.get(
    "/api/v1/workouts/sessions/active", response_model=Optional[WorkoutSessionResponse]
)
async def get_active_session(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_active_session(user_id=uid(current_user))


@router.post("/api/v1/workouts/sessions/log", response_model=WorkoutLogEntryResponse)
async def log_set(
    session_id: int,
    entry: WorkoutLogEntryCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.log_set(
        user_id=uid(current_user), session_id=session_id, entry=entry
    )


@router.post(
    "/api/v1/workouts/sessions/complete", response_model=WorkoutSessionResponse
)
async def complete_session(
    session_id: int,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.complete_session(
        user_id=uid(current_user), session_id=session_id, notes=notes
    )


@router.get(
    "/api/v1/workouts/sessions/recent", response_model=list[WorkoutSessionResponse]
)
async def list_recent_sessions(
    limit: int = Query(10, le=100),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_recent_sessions(user_id=uid(current_user), limit=limit)
