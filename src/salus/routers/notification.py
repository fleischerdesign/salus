from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import get_current_user, get_notification_service
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/count", response_class=HTMLResponse)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    unread = service.get_unread(uid(current_user))
    count = len(unread)
    if count > 0:
        return f'<span class="notifications-menu__badge-count">{count}</span>'
    return ""


@router.get("/dropdown", response_class=HTMLResponse)
async def get_dropdown_content(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    notifications = service.get_all(uid(current_user), limit=10)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/ui/notifications/dropdown_items.html",
        {"notifications": notifications},
    )


@router.post("/{notification_id}/read")
async def mark_read(
    response: Response,
    notification_id: int,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    service.mark_as_read(uid(current_user), notification_id)
    # Return custom header to trigger reload of badge and dropdown content
    response.headers["HX-Trigger"] = "refresh-notifications"
    return Response(status_code=204)


@router.post("/read-all")
async def mark_all_read(
    response: Response,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    service.mark_all_as_read(uid(current_user))
    response.headers["HX-Trigger"] = "refresh-notifications"
    return Response(status_code=204)
