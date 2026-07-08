import uuid
from typing import List, Dict
from services.notifications.domain.entities import Notification, DomainEvent, DEFAULT_PREFERENCES
from services.notifications.domain.exceptions import DuplicateNotificationError
from services.notifications.application.ports import NotificationRepositoryPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class CreateNotificationFromEventUseCase:
    def __init__(self, repo: NotificationRepositoryPort):
        self.repo = repo

    async def execute(self, event: DomainEvent) -> List[Notification]:
        """
        Maps a generic domain event into targeted notifications based on user preferences.
        """
        notifications = []
        target_users = self._resolve_target_users(event)
        
        for user_id in target_users:
            prefs = await self.repo.get_user_preferences(user_id)
            channels = prefs.preferences.get(event.type, []) if prefs else DEFAULT_PREFERENCES.get(event.type, ["in_app"])
            
            for channel in channels:
                notif = Notification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    event_type=event.type,
                    event_id=event.id, # Deduplication key
                    channel=channel,
                    payload=event.payload
                )
                
                try:
                    await self.repo.save_notification(notif)
                    notifications.append(notif)
                except DuplicateNotificationError:
                    # Idempotency: Ignore if we already processed this event_id for this channel/user
                    logger.debug(f"Idempotent skip: event {event.id} already processed for {user_id} on {channel}")
                    continue
                    
        return notifications

    def _resolve_target_users(self, event: DomainEvent) -> List[str]:
        # In reality, this would query a repository's CODEOWNERS mapping.
        # Stubbed for the artifact.
        return ["user-123"]
