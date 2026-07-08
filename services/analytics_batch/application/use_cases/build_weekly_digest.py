from shared.logging_engine import get_logger
from services.analytics_batch.domain.entities import DigestSummary

logger = get_logger(__name__)

class BuildWeeklyDigestUseCase:
    def __init__(self, repo):
        self.repo = repo

    async def execute(self, team_id: str) -> DigestSummary:
        """
        Builds the weekly email/slack digest data for a specific team.
        """
        logger.info(f"Building weekly digest for team {team_id}")
        
        # Simulating logic
        summary = DigestSummary(
            team_id=team_id,
            new_flaky_tests=3,
            top_failing_tests=["test_auth", "test_billing"],
            total_failures_prevented=42
        )
        
        logger.info(f"Digest built for team {team_id}.")
        return summary
