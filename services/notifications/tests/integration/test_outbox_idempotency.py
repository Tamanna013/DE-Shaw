import pytest
from services.notifications.domain.entities import DomainEvent
from services.notifications.application.use_cases.create_notification_from_event import CreateNotificationFromEventUseCase
from services.notifications.infrastructure.db.repository import MockDbNotificationRepository

@pytest.mark.asyncio
async def test_outbox_consumer_idempotency_silently_skips_duplicates():
    # If the outbox consumer processes the exact same DomainEvent (same event ID) twice,
    # it must not create duplicate notifications or crash. It should silently skip.
    
    repo = MockDbNotificationRepository()
    use_case = CreateNotificationFromEventUseCase(repo)
    
    event = DomainEvent(id="unique-outbox-ev-id", type="failure.analyzed", payload={})
    
    # First delivery
    notifs_run_1 = await use_case.execute(event)
    assert len(notifs_run_1) == 1 # Assuming default 'in_app' preference
    
    # Second delivery of the exact same event (simulating outbox replay due to network error)
    notifs_run_2 = await use_case.execute(event)
    
    # Should return empty list because it was idempotently skipped internally
    assert len(notifs_run_2) == 0
    
    # Verify the database only has 1 notification total
    all_notifs = await repo.get_user_notifications("user-123")
    assert len(all_notifs) == 1
    assert all_notifs[0].event_id == "unique-outbox-ev-id"
