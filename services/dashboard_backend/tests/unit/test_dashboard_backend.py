import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from services.dashboard_backend.application.use_cases.get_failure_trends import GetFailureTrendsUseCase
from services.dashboard_backend.domain.exceptions import InvalidDateRangeError
from services.dashboard_backend.domain.entities import FailureTrendSeries, TrendPoint

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo

@pytest.fixture
def mock_cache():
    # Cache get_or_set mock that just executes the callable instantly
    cache = AsyncMock()
    async def get_or_set(key, func, ttl):
        return await func()
    cache.get_or_set = get_or_set
    return cache

@pytest.mark.asyncio
async def test_date_range_validation_caps_at_one_year(mock_repo, mock_cache):
    use_case = GetFailureTrendsUseCase(mock_repo, mock_cache)
    
    from_date = datetime(2023, 1, 1)
    to_date = datetime(2024, 1, 2) # 1 year + 1 day
    
    with pytest.raises(InvalidDateRangeError) as exc_info:
        await use_case.execute("repo1", from_date, to_date, "day")
        
    assert "capped at 1 year" in str(exc_info.value)

@pytest.mark.asyncio
async def test_date_range_validation_prevents_negative_range(mock_repo, mock_cache):
    use_case = GetFailureTrendsUseCase(mock_repo, mock_cache)
    
    from_date = datetime(2023, 2, 1)
    to_date = datetime(2023, 1, 1)
    
    with pytest.raises(InvalidDateRangeError) as exc_info:
        await use_case.execute("repo1", from_date, to_date, "day")
        
    assert "cannot be earlier" in str(exc_info.value)

@pytest.mark.asyncio
async def test_invalid_granularity_raises_value_error(mock_repo, mock_cache):
    use_case = GetFailureTrendsUseCase(mock_repo, mock_cache)
    
    from_date = datetime(2023, 1, 1)
    to_date = datetime(2023, 1, 2)
    
    with pytest.raises(ValueError) as exc_info:
        await use_case.execute("repo1", from_date, to_date, "year")
        
    assert "Invalid granularity" in str(exc_info.value)

@pytest.mark.asyncio
async def test_empty_series_returned_when_no_data(mock_repo, mock_cache):
    mock_repo.get_failure_trends.return_value = FailureTrendSeries(
        repository_id="repo1",
        granularity="day",
        data_points=[]
    )
    
    use_case = GetFailureTrendsUseCase(mock_repo, mock_cache)
    
    from_date = datetime(2023, 1, 1)
    to_date = datetime(2023, 1, 2)
    
    result = await use_case.execute("repo1", from_date, to_date, "day")
    
    assert result["repository_id"] == "repo1"
    assert len(result["data_points"]) == 0 # Must be explicit empty array, not error
