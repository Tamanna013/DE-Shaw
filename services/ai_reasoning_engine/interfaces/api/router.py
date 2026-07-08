from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from services.ai_reasoning_engine.interfaces.api.schemas import ReasonAboutFailureRequest, ReasonAboutFailureResponse, RootCauseHypothesisSchema, RecommendedActionSchema, EvidenceReferenceSchema
from services.ai_reasoning_engine.application.use_cases.build_reasoning_context import BuildReasoningContextUseCase
from services.ai_reasoning_engine.application.use_cases.reason_about_failure import ReasonAboutFailureUseCase
from services.ai_reasoning_engine.application.ports import LLMClientPort
from services.ai_reasoning_engine.domain.exceptions import MissingContextError
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/reasoning", tags=["ai_reasoning"])

# Stub LLM Client since Module 10 isn't built yet
class StubLLMClient(LLMClientPort):
    async def complete(self, prompt_template_id: str, context: dict) -> dict:
        return {
            "hypotheses": [
                {
                    "title": "Stub LLM Guess",
                    "description": "This is a mocked LLM response.",
                    "llm_confidence": 0.8,
                    "evidence_refs": [{"type": "heuristic", "ref_id": "stub"}],
                    "recommended_actions": [{"action_type": "fix", "description": "Fix it"}]
                }
            ]
        }

@router.post("/analyze", response_model=ReasonAboutFailureResponse)
async def analyze_failure(req: ReasonAboutFailureRequest):
    logger.info("Received reasoning request", execution_id=req.execution_id)
    
    context_builder = BuildReasoningContextUseCase()
    try:
        reasoning_ctx = context_builder.execute(
            execution_id=req.execution_id,
            test_case_id=req.test_case_id,
            context_bundle={
                "log_excerpt": req.log_excerpt,
                "stack_trace": req.stack_trace,
                "flaky_signal": req.flaky_signal,
                "commits": req.commits
            },
            historical_failures=[] # Stub for now
        )
    except MissingContextError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    reason_use_case = ReasonAboutFailureUseCase(StubLLMClient())
    hypotheses = await reason_use_case.execute(reasoning_ctx)
    
    return ReasonAboutFailureResponse(
        execution_id=req.execution_id,
        hypotheses=[
            RootCauseHypothesisSchema(
                title=h.title,
                description=h.description,
                confidence=h.confidence.value,
                score=h.score,
                recommended_actions=[RecommendedActionSchema(**a.__dict__) for a in h.recommended_actions],
                evidence_refs=[EvidenceReferenceSchema(**e.__dict__) for e in h.evidence_refs]
            ) for h in hypotheses
        ]
    )
