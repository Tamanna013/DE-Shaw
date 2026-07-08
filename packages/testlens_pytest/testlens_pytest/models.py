from pydantic import BaseModel, Field
from typing import Optional, Dict

class TestResultPayload(BaseModel):
    test_id: str
    outcome: str # "passed", "failed", "skipped", "error"
    duration: float
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    retry_count: int = 0
    environment: Dict[str, str] = Field(default_factory=dict)
