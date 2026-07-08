from fastapi import APIRouter, Depends, HTTPException
from typing import List
from services.notifications.interfaces.api.schemas import NotificationSchema, UpdatePreferencesRequest
from services.notifications.application.use_cases.mark_as_read import MarkAsReadUseCase
from services.notifications.application.use_cases.update_preferences import UpdatePreferencesUseCase
from services.notifications.domain.exceptions import InvalidChannelPreferenceError
from services.notifications.infrastructure.db.repository import MockDbNotificationRepository

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

# Shared mock repo for the artifact context to maintain state
mock_repo = MockDbNotificationRepository()

# Mock Auth User ID
def get_current_user_id():
    return "user-123"

@router.get("", response_model=List[NotificationSchema])
async def get_notifications(
    unread_only: bool = False,
    page: int = 1,
    user_id: str = Depends(get_current_user_id)
):
    notifs = await mock_repo.get_user_notifications(user_id, unread_only=unread_only)
    return [
        NotificationSchema(
            id=n.id,
            event_type=n.event_type,
            channel=n.channel,
            payload=n.payload,
            is_read=n.is_read,
            created_at=n.created_at.isoformat()
        ) for n in notifs
    ]

@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id)
):
    use_case = MarkAsReadUseCase(mock_repo)
    await use_case.execute_single(notification_id, user_id)
    return {"status": "success"}

@router.post("/read-all")
async def mark_all_read(
    user_id: str = Depends(get_current_user_id)
):
    use_case = MarkAsReadUseCase(mock_repo)
    await use_case.execute_all(user_id)
    return {"status": "success"}

@router.put("/preferences")
async def update_preferences(
    req: UpdatePreferencesRequest,
    user_id: str = Depends(get_current_user_id)
):
    use_case = UpdatePreferencesUseCase(mock_repo)
    try:
        await use_case.execute(user_id, req.preferences)
        return {"status": "success"}
    except InvalidChannelPreferenceError as e:
        raise HTTPException(status_code=422, detail=str(e))
