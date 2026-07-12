from fastapi import APIRouter, Depends, status

from salus.dependencies import get_current_user, get_asymmetric_share_service
from salus.models.user import User
from salus.schemas.asymmetric_share import (
    ShareRecipientCreate,
    ShareRecipientResponse,
    AsymmetricShareCreate,
    AsymmetricShareResponse,
)
from salus.services.asymmetric_share import AsymmetricShareService
from salus.services._helpers import uid

router = APIRouter(tags=["Asymmetric Sharing"])


@router.post(
    "/api/v1/shares/asymmetric/recipients",
    response_model=ShareRecipientResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipient(
    data: ShareRecipientCreate,
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    return service.create_recipient(user_id=uid(current_user), data=data)


@router.get(
    "/api/v1/shares/asymmetric/recipients", response_model=list[ShareRecipientResponse]
)
async def list_recipients(
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    return service.list_recipients(user_id=uid(current_user))


@router.delete(
    "/api/v1/shares/asymmetric/recipients/{recipient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recipient(
    recipient_id: int,
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    service.delete_recipient(user_id=uid(current_user), recipient_id=recipient_id)


@router.post(
    "/api/v1/shares/asymmetric",
    response_model=AsymmetricShareResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_share(
    data: AsymmetricShareCreate,
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    return service.create_share(user_id=uid(current_user), data=data)


@router.get("/api/v1/shares/asymmetric", response_model=list[AsymmetricShareResponse])
async def list_shares(
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    return service.list_shares(user_id=uid(current_user))


@router.get(
    "/api/v1/shares/asymmetric/{share_id}", response_model=AsymmetricShareResponse
)
async def get_share(
    share_id: int,
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    return service.get_share_secure(share_id)


@router.delete(
    "/api/v1/shares/asymmetric/{share_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    service: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    service.delete_share(user_id=uid(current_user), share_id=share_id)
