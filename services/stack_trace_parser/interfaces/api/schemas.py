from pydantic import BaseModel
from typing import List, Optional

class ParseStackTraceRequest(BaseModel):
    raw_text: str
    commit_sha: Optional[str] = None # For optional enrichment

class StackFrameSchema(BaseModel):
    file_path: str
    function_name: str
    line_number: Optional[int]
    code_context: Optional[str]
    is_external: bool
    repeated_count: int

class ExceptionInfoSchema(BaseModel):
    type: str
    message: str
    frames: List[StackFrameSchema]
    language: str
    normalized_signature: Optional[str]
    needs_sourcemap: bool

class ParseStackTraceResponse(BaseModel):
    raw_text: str
    root_exception: ExceptionInfoSchema
