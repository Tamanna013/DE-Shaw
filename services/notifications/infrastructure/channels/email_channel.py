from services.notifications.application.ports import NotificationChannelPort
from services.notifications.domain.entities import Notification

class EmailChannelAdapter(NotificationChannelPort):
    @property
    def channel_id(self) -> str:
        return "email"

    async def dispatch(self, notification: Notification) -> bool:
        # Mocked integration with SendGrid/SMTP
        return True
