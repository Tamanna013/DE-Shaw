# Analytics Batch Jobs

Scheduled batch jobs that compute expensive aggregate signals not suitable for real-time computation (flaky test scoring, commit correlation baselines).

## Architecture
- **Celery Beat**: Centralized scheduler that emits tasks based on `crontab` definitions.
- **Celery Workers**: Consume the tasks from Redis.
- **Overlap Protection**: The Celery tasks themselves (e.g., `task_compute_flaky_scores`) use the `DistributedLock` from `shared.caching` as an execution wrapper. This ensures that if the hourly compute run takes 65 minutes, the next beat tick will gracefully abort rather than causing overlapping DB writes.

## The Flaky Scoring Algorithm
The flip rate is calculated over a 30-day window.

Crucially, **raw flip rate is a bad signal on small sample sizes**. A test with 2 executions that flipped once has a 50% raw flip rate, but it is mathematically incorrect to assert it is flaky based on 1 data point.

To fix this, the algorithm applies the **Wilson Score Interval lower bound**. 
- A test with 2 executions and a 100% flip rate drops to a `0.34` confidence-adjusted score.
- A test with 50 executions and a 100% flip rate scores `0.92`.

This is implemented as an isolated pure function in `compute_flaky_scores.py` and is exhaustively tested in `test_flaky_scoring_algorithm.py` using boundary parametrized tests.
