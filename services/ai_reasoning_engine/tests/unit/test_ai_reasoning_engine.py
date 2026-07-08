import pytest
from unittest.mock import AsyncMock
from services.ai_reasoning_engine.application.use_cases.reason_about_failure import ReasonAboutFailureUseCase
from services.ai_reasoning_engine.domain.entities import ReasoningContext, HistoricalFailureInfo

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.complete.return_value = {
        "hypotheses": [
            {
                "title": "LLM Hypothesis 1",
                "description": "Desc",
                "llm_confidence": 0.9,
                "evidence_refs": [{"type": "historical_failure", "ref_id": "hist-1"}],
                "recommended_actions": []
            }
        ]
    }
    return client

@pytest.fixture
def base_context():
    return ReasoningContext(
        execution_id="exec-1",
        test_case_id="tc-1",
        log_excerpt="Log",
        stack_trace={"frames": []},
        flaky_signal=None,
        commits=[{"sha": "commit-1", "message": "msg"}],
        similar_historical_failures=[
            HistoricalFailureInfo(id="hist-1", test_case_id="tc-1", normalized_signature="sig", similarity_score=0.9)
        ]
    )

@pytest.mark.asyncio
async def test_confidence_score_composite_calculation(mock_llm_client, base_context):
    use_case = ReasonAboutFailureUseCase(mock_llm_client)
    hyps = await use_case.execute(base_context)
    
    assert len(hyps) == 1
    hyp = hyps[0]
    
    # LLM Conf = 0.9 * 0.4 = 0.36
    # Grounding Score = 1 valid cite * 0.5 = 0.5 * 0.35 = 0.175
    # Det Score = 0 (no commit match, no flaky) * 0.25 = 0.0
    # Total = 0.36 + 0.175 = 0.535
    assert hyp.score == pytest.approx(0.535)

@pytest.mark.asyncio
async def test_hypothesis_without_evidence_refs_rejected_by_schema(mock_llm_client, base_context):
    # LLM returns no evidence
    mock_llm_client.complete.return_value = {
        "hypotheses": [
            {
                "title": "Ungrounded LLM Hypothesis",
                "description": "Desc",
                "llm_confidence": 0.9,
                "evidence_refs": [], # Empty!
                "recommended_actions": []
            }
        ]
    }
    
    use_case = ReasonAboutFailureUseCase(mock_llm_client)
    hyps = await use_case.execute(base_context)
    
    # It should reject the LLM response and fall back to deterministic since all hyps were rejected
    assert len(hyps) > 0
    assert hyps[0].title == "Recent Code Change Implicated" # The fallback

@pytest.mark.asyncio
async def test_low_confidence_hypotheses_filtered_from_output(mock_llm_client, base_context):
    # Setup LLM response with terrible confidence and no grounding
    mock_llm_client.complete.return_value = {
        "hypotheses": [
            {
                "title": "Terrible Guess",
                "description": "Desc",
                "llm_confidence": 0.1, # 0.1 * 0.4 = 0.04
                "evidence_refs": [{"type": "heuristic", "ref_id": "none"}], # 0.5 * 0.35 = 0.175
                "recommended_actions": []
            }
        ]
    }
    
    use_case = ReasonAboutFailureUseCase(mock_llm_client)
    hyps = await use_case.execute(base_context)
    
    # 0.04 + 0.175 = 0.215 < 0.3 min_confidence
    # So it gets filtered out, triggering fallback
    assert len(hyps) > 0
    assert hyps[0].title == "Recent Code Change Implicated" # The fallback
