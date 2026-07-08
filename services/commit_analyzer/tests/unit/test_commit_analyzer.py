import pytest
from services.commit_analyzer.application.use_cases.correlate_commits_with_failure import (
    compute_file_overlap_score,
    compute_proximity_score,
    compute_composite_score,
    CandidateCommit,
    StackFrame,
    CorrelateCommitsWithFailureUseCase
)
from unittest.mock import AsyncMock

def test_file_overlap_score_weights_root_frame_higher():
    # Setup commit that touches file_a (bottom of stack)
    c_bottom = CandidateCommit("sha1", "msg", ["file_a.py"], 0)
    # Setup commit that touches file_b (top of stack)
    c_top = CandidateCommit("sha2", "msg", ["file_b.py"], 0)
    
    frames = [
        StackFrame("file_b.py", False), # Top (index 0) -> weight 1.0
        StackFrame("file_x.py", False), # Mid (index 1) -> weight 0.5
        StackFrame("file_a.py", False)  # Bot (index 2) -> weight 0.333
    ] # Total weight = 1.833
    
    score_bottom = compute_file_overlap_score(c_bottom, frames)
    score_top = compute_file_overlap_score(c_top, frames)
    
    # file_b (top) should score significantly higher than file_a (bottom)
    assert score_top > score_bottom
    assert score_top == pytest.approx(1.0 / 1.833, 0.01)
    assert score_bottom == pytest.approx(0.333 / 1.833, 0.01)

@pytest.mark.parametrize("distance, expected_score", [
    (0, 1.0),                  # HEAD = highest
    (1, 1.0 / 1.1),            # ~0.909
    (5, 1.0 / 1.5),            # ~0.666
    (10, 1.0 / 2.0)            # ~0.500
])
def test_proximity_score_decays_correctly(distance, expected_score):
    assert compute_proximity_score(distance) == pytest.approx(expected_score)

def test_composite_score_calculation():
    # W_OVERLAP = 0.5, W_PROX = 0.2, W_HIST = 0.3
    overlap = 1.0
    prox = 0.5
    hist = 0.0
    
    comp = compute_composite_score(overlap, prox, hist)
    assert comp == pytest.approx(0.5 + 0.1 + 0.0)

@pytest.mark.asyncio
async def test_empty_commit_range_returns_reason_code():
    repo = AsyncMock()
    use_case = CorrelateCommitsWithFailureUseCase(repo)
    
    results = await use_case.execute("tc-1", [], [{"file_path": "a.py", "is_external": False}])
    
    assert len(results) == 1
    assert results[0].reason_code == "no_commits_in_range"
    assert results[0].composite_score == 0.0
