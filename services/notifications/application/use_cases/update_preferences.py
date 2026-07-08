from typing import Dict, List
from services.notifications.domain.entities import NotificationPreference, VALID_CHANNELS_PER_EVENT
from services.notifications.domain.exceptions import InvalidChannelPreferenceError
from services.notifications.application.ports import NotificationRepositoryPort

class UpdatePreferencesUseCase:
    def __init__(self, repo: NotificationRepositoryPort):
        self.repo = repo

    async def execute(self, user_id: str, preferences: Dict[str, List[str]]) -> None:
        # Validate against allow-list
        for event_type, channels in preferences.items():
            valid_channels = VALID_CHANNELS_PER_EVENT.get(event_type, [])
            for channel in channels:
                if channel not in valid_channels:
                    valid_str = ", ".join(valid_channels) if valid_channels else "None"
                    raise InvalidChannelPreferenceError(
                        f"Channel '{channel}' is not supported for event type '{event_type}'. Valid channels: {valid_str}"
                    )
                    
        pref = NotificationPreference(user_id=user_id, preferences=preferences)
        await self.repo.save_user_preferences(pref)
