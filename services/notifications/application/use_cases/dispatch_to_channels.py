from typing import List, Dict
from services.notifications.domain.entities import Notification
from services.notifications.application.ports import NotificationChannelPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class DispatchToChannelsUseCase:
    def __init__(self, channels: List[NotificationChannelPort]):
        # Map channel_id -> channel instance for O(1) lookup
        self.channel_map: Dict[str, NotificationChannelPort] = {c.channel_id: c for c in channels}

    async def execute(self, notifications: List[Notification]) -> None:
        for notif in notifications:
            # We don't dispatch 'in_app' through an external adapter, it's just persisted in DB
            if notif.channel == "in_app":
                continue
                
            channel_adapter = self.channel_map.get(notif.channel)
            if not channel_adapter:
                logger.error(f"No adapter found for channel: {notif.channel}")
                continue
                
            try:
                success = await channel_adapter.dispatch(notif)
                if not success:
                    logger.warning(f"Failed to dispatch notification {notif.id} via {notif.channel}")
                else:
                    logger.info(f"Dispatched notification {notif.id} via {notif.channel}")
            except Exception as e:
                logger.error(f"Error dispatching via {notif.channel}", exc_info=e)
