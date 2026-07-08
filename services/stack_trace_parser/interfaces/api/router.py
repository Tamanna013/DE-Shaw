from fastapi import APIRouter, HTTPException
from typing import Optional
from services.stack_trace_parser.interfaces.api.schemas import ParseStackTraceRequest, ParseStackTraceResponse, ExceptionInfoSchema, StackFrameSchema
from services.stack_trace_parser.application.use_cases.parse_stack_trace import ParseStackTraceUseCase
from services.stack_trace_parser.application.use_cases.enrich_with_source_context import EnrichWithSourceContextUseCase
from services.stack_trace_parser.application.ports import SourceCodeFetcherPort
from services.stack_trace_parser.infrastructure.language_parsers.python_traceback_parser import PythonTracebackParser
from services.stack_trace_parser.infrastructure.language_parsers.java_stacktrace_parser import JavaStacktraceParser
from services.stack_trace_parser.infrastructure.language_parsers.js_stacktrace_parser import JsStacktraceParser
from services.stack_trace_parser.infrastructure.language_parsers.go_panic_parser import GoPanicParser
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/stacktraces", tags=["stack_trace_parser"])

# Stub fetcher since Module 11 (git_integration) isn't built yet
class StubSourceFetcher(SourceCodeFetcherPort):
    async def fetch_context(self, commit_sha: str, file_path: str, line_number: int, context_lines: int = 3) -> Optional[str]:
        return None

def get_parsers():
    return [
        PythonTracebackParser(),
        JavaStacktraceParser(),
        JsStacktraceParser(),
        GoPanicParser()
    ]

@router.post("/parse", response_model=ParseStackTraceResponse)
async def parse_stack_trace(req: ParseStackTraceRequest):
    parse_use_case = ParseStackTraceUseCase(get_parsers())
    enrich_use_case = EnrichWithSourceContextUseCase(StubSourceFetcher())
    
    trace = parse_use_case.execute(req.raw_text)
    
    if req.commit_sha:
        trace = await enrich_use_case.execute(trace, req.commit_sha)
        
    def map_exc(exc):
        return ExceptionInfoSchema(
            type=exc.type,
            message=exc.message,
            frames=[StackFrameSchema(**f.__dict__) for f in exc.frames],
            language=exc.language,
            normalized_signature=exc.normalized_signature,
            needs_sourcemap=exc.needs_sourcemap
        )
        
    return ParseStackTraceResponse(
        raw_text=trace.raw_text,
        root_exception=map_exc(trace.root_exception)
    )
