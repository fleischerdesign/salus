from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import get_current_user, get_insight_service
from salus.services.insight.service import InsightService

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def list_insights(
    request: Request,
    date: str | None = Query(None),
    current_user=Depends(get_current_user),
    service: InsightService = Depends(get_insight_service),
):
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")

    insight = service.get_insight_for_date(current_user.id, date)

    if request.headers.get("HX-Request"):
        return request.app.state.templates.TemplateResponse(
            request,
            "components/ai_insight_card.html",
            {
                "insight": insight,
                "display_date": date,
            },
        )

    history = service._uow.insights.list_by_user(current_user.id, limit=30)

    # Convert query date string to datetime for formatting in template if needed
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        display_date_formatted = dt.strftime("%B %d, %Y")
    except ValueError:
        display_date_formatted = date

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/insights.html",
        {
            "insight": insight,
            "display_date": date,
            "display_date_formatted": display_date_formatted,
            "history": history,
        },
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_insight(
    request: Request,
    date: str = Query(...),
    current_user=Depends(get_current_user),
    service: InsightService = Depends(get_insight_service),
):
    locale = request.cookies.get("salus_locale", "en")
    insight = service.generate_daily_insight(current_user.id, date, locale=locale)

    return request.app.state.templates.TemplateResponse(
        request,
        "components/ai_insight_card.html",
        {
            "insight": insight,
            "display_date": date,
        },
    )
