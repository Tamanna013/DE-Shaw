from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class StackFrame:
    file_path: str
    function_name: str
    line_number: Optional[int]
    code_context: Optional[str] = None
    is_external: bool = False
    repeated_count: int = 1

@dataclass
class ExceptionInfo:
    type: str
    message: str
    frames: List[StackFrame] = field(default_factory=list)
    cause_chain: List['ExceptionInfo'] = field(default_factory=list)
    language: str = "unknown"
    normalized_signature: Optional[str] = None
    needs_sourcemap: bool = False

@dataclass
class StackTrace:
    raw_text: str
    root_exception: ExceptionInfo
