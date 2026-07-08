from services.notifications.application.ports import NotificationChannelPort
from services.notifications.domain.entities import Notification

class SlackChannelAdapter(NotificationChannelPort):
    @property
    def channel_id(self) -> str:
        return "slack"

    async def dispatch(self, notification: Notification) -> bool:
        # Mocked integration with Slack webhooks
        return True
