import pytest
from services.notifications.domain.entities import DomainEvent, NotificationPreference, DEFAULT_PREFERENCES
from services.notifications.domain.exceptions import InvalidChannelPreferenceError
from services.notifications.application.use_cases.create_notification_from_event import CreateNotificationFromEventUseCase
from services.notifications.application.use_cases.update_preferences import UpdatePreferencesUseCase
from services.notifications.infrastructure.db.repository import MockDbNotificationRepository

@pytest.fixture
def repo():
    return MockDbNotificationRepository()

@pytest.mark.asyncio
async def test_create_notification_uses_defaults_if_no_preferences(repo):
    use_case = CreateNotificationFromEventUseCase(repo)
    event = DomainEvent(id="ev-1", type="failure.analyzed", payload={"foo": "bar"})
    
    notifs = await use_case.execute(event)
    
    assert len(notifs) == len(DEFAULT_PREFERENCES["failure.analyzed"])
    assert notifs[0].channel == "in_app"
    assert notifs[0].event_type == "failure.analyzed"

@pytest.mark.asyncio
async def test_create_notification_respects_user_preferences(repo):
    pref = NotificationPreference(user_id="user-123", preferences={
        "failure.analyzed": ["in_app", "slack"]
    })
    await repo.save_user_preferences(pref)
    
    use_case = CreateNotificationFromEventUseCase(repo)
    event = DomainEvent(id="ev-2", type="failure.analyzed", payload={"foo": "bar"})
    
    notifs = await use_case.execute(event)
    
    assert len(notifs) == 2
    channels = {n.channel for n in notifs}
    assert channels == {"in_app", "slack"}

@pytest.mark.asyncio
async def test_update_preferences_validates_allow_list(repo):
    use_case = UpdatePreferencesUseCase(repo)
    
    # SMS is not in the allow-list for failure.analyzed
    with pytest.raises(InvalidChannelPreferenceError) as exc_info:
        await use_case.execute("user-123", {
            "failure.analyzed": ["sms"]
        })
        
    assert "not supported" in str(exc_info.value)
    
    # Valid update should succeed
    await use_case.execute("user-123", {
        "digest.weekly_ready": ["email"]
    })
    
    pref = await repo.get_user_preferences("user-123")
    assert pref.preferences["digest.weekly_ready"] == ["email"]
