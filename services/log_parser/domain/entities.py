from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List

class TestOutcome(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"

@dataclass
class LogSpan:
    start_line: int
    end_line: int
    raw_text: str

@dataclass
class ParsedLogEvent:
    test_name: str
    file_path: Optional[str]
    outcome: TestOutcome
    duration_ms: Optional[int]
    span: LogSpan
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    low_confidence_parse: bool = False
    truncated: bool = False
    worker_id: Optional[str] = None
