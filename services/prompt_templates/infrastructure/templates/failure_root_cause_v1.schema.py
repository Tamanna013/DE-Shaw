from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class FailureRootCauseV1Schema(BaseModel):
    execution_id: str
    test_case_id: str
    log_excerpt: Optional[str] = None
    stack_trace: Optional[Dict[str, Any]] = None
    commits: List[Dict[str, Any]] = Field(default_factory=list)
    similar_historical_failures: List[Dict[str, Any]] = Field(default_factory=list)
    flaky_signal: Optional[Dict[str, Any]] = None
    
    @classmethod
    def generate_example(cls):
        return {
            "execution_id": "exec-123",
            "test_case_id": "tc-456",
            "log_excerpt": "AssertionError: Expected 200, got 500",
            "stack_trace": {"frames": []},
            "commits": [{"sha": "abc1234", "message": "fix bug", "files_changed": ["main.py"]}],
            "similar_historical_failures": []
        }
