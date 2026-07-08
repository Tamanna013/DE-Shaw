from typing import List
from services.failure_analyzer.domain.entities import RootCauseHypothesis, ConfidenceLevel, RecommendedAction
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RankHypothesesUseCase:
    def execute(self, ai_hypotheses: List[RootCauseHypothesis], flaky_signal: dict, ranked_commits: List[dict]) -> List[RootCauseHypothesis]:
        final_list = list(ai_hypotheses)
        
        # Inject deterministic signals if AI missed them
        if flaky_signal.get("is_flaky"):
            has_flaky_hyp = any("flaky" in h.title.lower() or "environment" in h.title.lower() for h in final_list)
            if not has_flaky_hyp:
                final_list.append(RootCauseHypothesis(
                    title="Likely Flaky Test or Environment Issue",
                    description=f"Test has failed {flaky_signal.get('fails')} times recently with a {flaky_signal.get('flip_rate', 0.0):.1%} flip rate.",
                    confidence=ConfidenceLevel.HIGH,
                    score=0.9,
                    recommended_actions=[
                        RecommendedAction(action_type="investigate_flakiness", description="Check environment stability and consider isolating this test or retrying.")
                    ]
                ))
                
        if not ranked_commits and not final_list:
             final_list.append(RootCauseHypothesis(
                title="No Code Changes Detected",
                description="This test failed but no commits occurred between the last pass and now. Check infrastructure configuration.",
                confidence=ConfidenceLevel.MEDIUM,
                score=0.6,
                recommended_actions=[
                    RecommendedAction(action_type="check_infra", description="Check environment/infra config changes outside of git.")
                ]
            ))
            
        final_list.sort(key=lambda h: h.score, reverse=True)
        return final_list
