from typing import Protocol, List, Optional
from services.notifications.domain.entities import Notification, NotificationPreference, DomainEvent

class NotificationRepositoryPort(Protocol):
    async def save_notification(self, notification: Notification) -> None:
        ...

    async def get_user_notifications(self, user_id: str, unread_only: bool = False, limit: int = 20, offset: int = 0) -> List[Notification]:
        ...

    async def mark_as_read(self, notification_id: str, user_id: str) -> None:
        ...

    async def mark_all_as_read(self, user_id: str) -> None:
        ...

    async def get_user_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        ...

    async def save_user_preferences(self, pref: NotificationPreference) -> None:
        ...

class NotificationChannelPort(Protocol):
    @property
    def channel_id(self) -> str:
        ...
        
    async def dispatch(self, notification: Notification) -> bool:
        ...
