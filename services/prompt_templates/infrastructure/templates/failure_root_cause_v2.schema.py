from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class FailureRootCauseV2Schema(BaseModel):
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
            "execution_id": "exec-v2",
            "test_case_id": "tc-v2",
            "log_excerpt": "Timeout",
            "stack_trace": None,
            "commits": [],
            "similar_historical_failures": []
        }
