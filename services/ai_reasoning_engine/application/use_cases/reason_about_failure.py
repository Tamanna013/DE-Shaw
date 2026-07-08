import json
from typing import List
from services.ai_reasoning_engine.domain.entities import (
    ReasoningContext, RootCauseHypothesis, RecommendedAction, 
    EvidenceReference, ConfidenceLevel
)
from services.ai_reasoning_engine.application.ports import LLMClientPort
from services.ai_reasoning_engine.domain.exceptions import LLMProviderError
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class ReasonAboutFailureUseCase:
    def __init__(self, llm_client: LLMClientPort):
        self.llm_client = llm_client
        self.min_confidence = 0.3

    async def execute(self, context: ReasoningContext) -> List[RootCauseHypothesis]:
        # Context dump for LLM
        prompt_ctx = {
            "log": context.log_excerpt,
            "stack_trace": context.stack_trace,
            "flaky_signal": context.flaky_signal,
            "commits": context.commits,
            "history": [{"id": h.id, "resolution": h.resolution_notes} for h in context.similar_historical_failures]
        }
        
        try:
            llm_response = await self.llm_client.complete("analyze_failure_v1", prompt_ctx)
        except Exception as e:
            logger.warning("LLM API failed. Falling back.", exc_info=e)
            return self._build_deterministic_fallback(context)
            
        # Parse and repair logic
        try:
            hypotheses = self._parse_llm_response(llm_response, context)
            if not hypotheses:
                return self._build_deterministic_fallback(context)
            return hypotheses
        except Exception as e:
            logger.warning("JSON parsing failed, attempting repair", exc_info=e)
            try:
                # One retry repair
                llm_response = await self.llm_client.complete("json_repair_v1", {"error": str(e), "original": llm_response})
                hypotheses = self._parse_llm_response(llm_response, context)
                if not hypotheses:
                    return self._build_deterministic_fallback(context)
                return hypotheses
            except Exception as e2:
                logger.error("JSON repair failed. Degraded fallback.", exc_info=e2)
                return self._build_deterministic_fallback(context)
                
    def _parse_llm_response(self, response_data: dict, context: ReasoningContext) -> List[RootCauseHypothesis]:
        hypotheses = []
        raw_hyps = response_data.get("hypotheses", [])
        
        for h in raw_hyps:
            # 1. Enforce schema
            evidence = h.get("evidence_refs", [])
            if not evidence:
                # Reject ungrounded hypothesis per requirements
                continue
                
            refs = []
            for ev in evidence:
                refs.append(EvidenceReference(type=ev.get("type"), ref_id=ev.get("ref_id")))
                
            actions = [RecommendedAction(a.get("action_type", "unknown"), a.get("description", "")) for a in h.get("recommended_actions", [])]
            
            # 2. Confidence Composite Score (Hallucination Mitigation)
            llm_conf = float(h.get("llm_confidence", 0.5))
            llm_conf = min(max(llm_conf, 0.0), 1.0) # Clamp
            
            # Grounding score based on retrieval
            grounding_score = 0.0
            hist_refs = [r for r in refs if r.type == "historical_failure"]
            if hist_refs and context.similar_historical_failures:
                # Give points if they actually cite a real ID we gave them
                valid_ids = {hf.id for hf in context.similar_historical_failures}
                valid_cites = sum(1 for r in hist_refs if r.ref_id in valid_ids)
                grounding_score = min(valid_cites * 0.5, 1.0)
            elif any(r.type == "heuristic" for r in refs):
                grounding_score = 0.5 # Baseline for valid heuristics
                
            # Deterministic signal agreement
            det_score = 0.0
            commit_refs = [r for r in refs if r.type == "commit"]
            if commit_refs and context.commits:
                top_commit = context.commits[0].get("sha") if context.commits else None
                if any(r.ref_id == top_commit for r in commit_refs):
                    det_score = 1.0
            elif context.flaky_signal and context.flaky_signal.get("is_flaky"):
                flaky_refs = [r for r in refs if r.type == "flaky_signal"]
                if flaky_refs:
                    det_score = 1.0
                    
            composite_score = (0.4 * llm_conf) + (0.35 * grounding_score) + (0.25 * det_score)
            
            if composite_score >= self.min_confidence:
                c_level = ConfidenceLevel.HIGH if composite_score > 0.75 else (ConfidenceLevel.MEDIUM if composite_score > 0.5 else ConfidenceLevel.LOW)
                
                hypotheses.append(RootCauseHypothesis(
                    title=h.get("title", "Unknown"),
                    description=h.get("description", ""),
                    llm_confidence=llm_conf,
                    confidence=c_level,
                    score=composite_score,
                    recommended_actions=actions,
                    evidence_refs=refs
                ))
                
        return hypotheses

    def _build_deterministic_fallback(self, context: ReasoningContext) -> List[RootCauseHypothesis]:
        hyps = []
        
        if context.flaky_signal and context.flaky_signal.get("is_flaky"):
            hyps.append(RootCauseHypothesis(
                title="Likely Flaky Test or Environment Issue",
                description="Test has failed recently with a high flip rate.",
                llm_confidence=1.0,
                confidence=ConfidenceLevel.HIGH,
                score=0.9,
                evidence_refs=[EvidenceReference(type="flaky_signal", ref_id="historical_flip_rate")],
                recommended_actions=[RecommendedAction(action_type="investigate", description="Check environment")]
            ))
            
        if context.commits:
            top_commit = context.commits[0]
            hyps.append(RootCauseHypothesis(
                title="Recent Code Change Implicated",
                description=f"Highest file-overlap commit is the primary suspect: {top_commit.get('message')}",
                llm_confidence=1.0,
                confidence=ConfidenceLevel.MEDIUM,
                score=0.7,
                evidence_refs=[EvidenceReference(type="commit", ref_id=top_commit.get("sha"))],
                recommended_actions=[RecommendedAction(action_type="review_commit", description="Review the implicated commit")]
            ))
            
        if not hyps:
            hyps.append(RootCauseHypothesis(
                title="No Code Changes Detected",
                description="This test failed but no commits occurred between the last pass and now. Check infrastructure configuration.",
                llm_confidence=1.0,
                confidence=ConfidenceLevel.MEDIUM,
                score=0.6,
                evidence_refs=[EvidenceReference(type="heuristic", ref_id="no_commits")],
                recommended_actions=[RecommendedAction(action_type="check_infra", description="Check environment/infra config changes outside of git.")]
            ))
            
        return hyps
