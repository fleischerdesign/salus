from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["design_system"])


@router.get("/design-system", response_class=HTMLResponse)
async def design_system(request: Request) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/design_system.html",
        {"current_user": None, "settings": {"app_name": "Salus Design System"}},
    )
