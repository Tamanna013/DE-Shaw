from services.notifications.application.ports import NotificationRepositoryPort

class MarkAsReadUseCase:
    def __init__(self, repo: NotificationRepositoryPort):
        self.repo = repo

    async def execute_single(self, notification_id: str, user_id: str) -> None:
        await self.repo.mark_as_read(notification_id, user_id)

    async def execute_all(self, user_id: str) -> None:
        await self.repo.mark_all_as_read(user_id)
