from typing import List, Optional
from services.notifications.application.ports import NotificationRepositoryPort
from services.notifications.domain.entities import Notification, NotificationPreference
from services.notifications.domain.exceptions import DuplicateNotificationError

class MockDbNotificationRepository(NotificationRepositoryPort):
    def __init__(self):
        self.notifications: List[Notification] = []
        self.preferences: dict[str, NotificationPreference] = {}
        # Simulate unique constraint: (event_id, user_id, channel)
        self.unique_keys = set()

    async def save_notification(self, notification: Notification) -> None:
        key = f"{notification.event_id}:{notification.user_id}:{notification.channel}"
        if key in self.unique_keys:
            raise DuplicateNotificationError(f"Duplicate notification for key {key}")
            
        self.unique_keys.add(key)
        self.notifications.append(notification)

    async def get_user_notifications(self, user_id: str, unread_only: bool = False, limit: int = 20, offset: int = 0) -> List[Notification]:
        return [n for n in self.notifications if n.user_id == user_id and (not unread_only or not n.is_read)]

    async def mark_as_read(self, notification_id: str, user_id: str) -> None:
        for n in self.notifications:
            if n.id == notification_id and n.user_id == user_id:
                n.is_read = True
                return

    async def mark_all_as_read(self, user_id: str) -> None:
        for n in self.notifications:
            if n.user_id == user_id:
                n.is_read = True

    async def get_user_preferences(self, user_id: str) -> Optional[NotificationPreference]:
        return self.preferences.get(user_id)

    async def save_user_preferences(self, pref: NotificationPreference) -> None:
        self.preferences[pref.user_id] = pref
