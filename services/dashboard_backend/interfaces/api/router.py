from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import List
from redis.asyncio import Redis

from shared.db.session import get_db_session
from shared.logging_engine import get_logger
from shared.caching.cache_client import CacheClient

from services.dashboard_backend.infrastructure.db.repository import DbAnalyticsRepository
from services.dashboard_backend.application.use_cases.get_failure_trends import GetFailureTrendsUseCase
from services.dashboard_backend.application.use_cases.get_flaky_leaderboard import GetFlakyLeaderboardUseCase
from services.dashboard_backend.application.use_cases.get_team_health_summary import GetTeamHealthSummaryUseCase
from services.dashboard_backend.application.use_cases.get_repository_health import GetRepositoryHealthUseCase
from services.dashboard_backend.domain.exceptions import InvalidDateRangeError
from services.dashboard_backend.interfaces.api.schemas import (
    FailureTrendSeriesSchema, 
    FlakyLeaderboardEntrySchema,
    TeamHealthSummarySchema,
    RepositoryHealthSchema
)

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["dashboard_backend"])

# Simple dependency for Redis CacheClient
async def get_cache_client() -> CacheClient:
    redis = Redis(host="localhost", port=6379, db=0) # Should come from config in prod
    return CacheClient(redis)

@router.get("/trends/failures", response_model=FailureTrendSeriesSchema)
async def get_failure_trends(
    repository_id: str,
    from_date: datetime,
    to_date: datetime,
    granularity: str = Query("day", pattern="^(day|week|month)$"),
    session: AsyncSession = Depends(get_db_session),
    cache_client: CacheClient = Depends(get_cache_client)
):
    repo = DbAnalyticsRepository(session)
    use_case = GetFailureTrendsUseCase(repo, cache_client)
    
    try:
        result = await use_case.execute(repository_id, from_date, to_date, granularity)
        return result
    except InvalidDateRangeError as e:
        logger.warning(f"Invalid date range requested: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/leaderboard/flaky-tests", response_model=List[FlakyLeaderboardEntrySchema])
async def get_flaky_leaderboard(
    repository_id: str,
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    cache_client: CacheClient = Depends(get_cache_client)
):
    repo = DbAnalyticsRepository(session)
    use_case = GetFlakyLeaderboardUseCase(repo, cache_client)
    
    results = await use_case.execute(repository_id, limit)
    return results

@router.get("/teams/{team_id}/health-summary", response_model=TeamHealthSummarySchema)
async def get_team_health_summary(
    team_id: str,
    session: AsyncSession = Depends(get_db_session),
    cache_client: CacheClient = Depends(get_cache_client)
):
    repo = DbAnalyticsRepository(session)
    use_case = GetTeamHealthSummaryUseCase(repo, cache_client)
    
    result = await use_case.execute(team_id)
    return result

@router.get("/repositories/{repository_id}/health", response_model=RepositoryHealthSchema)
async def get_repository_health(
    repository_id: str,
    session: AsyncSession = Depends(get_db_session),
    cache_client: CacheClient = Depends(get_cache_client)
):
    repo = DbAnalyticsRepository(session)
    use_case = GetRepositoryHealthUseCase(repo, cache_client)
    
    result = await use_case.execute(repository_id)
    return result
