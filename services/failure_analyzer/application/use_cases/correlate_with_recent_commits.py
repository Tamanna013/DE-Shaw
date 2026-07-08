from typing import List, Dict, Any
from services.failure_analyzer.application.ports import CommitAnalyzerPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class CorrelateWithRecentCommitsUseCase:
    def __init__(self, commit_analyzer: CommitAnalyzerPort):
        self.commit_analyzer = commit_analyzer

    async def execute(self, execution_id: str, parsed_stack_trace: dict) -> List[Dict[str, Any]]:
        commits = await self.commit_analyzer.get_commits_since_last_pass(execution_id)
        if not commits:
            return []
            
        frames = parsed_stack_trace.get("frames", [])
        trace_files = {frame.get("file_path") for frame in frames if not frame.get("is_external", True) and frame.get("file_path")}
        
        ranked_commits = []
        for commit in commits:
            commit_files = set(commit.get("files_changed", []))
            
            overlap = trace_files.intersection(commit_files)
            overlap_score = len(overlap)
            
            # Simple scoring: 10 points per overlapping file + 1 point just for being recent
            score = (overlap_score * 10) + 1
            
            ranked_commits.append({
                "sha": commit.get("sha"),
                "message": commit.get("message"),
                "score": score,
                "overlap_files": list(overlap)
            })
            
        ranked_commits.sort(key=lambda x: x["score"], reverse=True)
        return ranked_commits
