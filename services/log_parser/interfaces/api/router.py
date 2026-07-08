import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

from services.log_parser.application.use_cases.parse_log import ParseLogUseCase
from services.log_parser.application.ports import LogSourcePort
from services.log_parser.domain.exceptions import PayloadTooLargeError
from services.log_parser.infrastructure.parser_registry import ParserRegistry
from services.log_parser.infrastructure.parsers.pytest_log_parser import PytestLogParser
from services.log_parser.infrastructure.parsers.junit_xml_parser import JunitXmlParser
from services.log_parser.infrastructure.parsers.jest_log_parser import JestLogParser
from services.log_parser.infrastructure.parsers.generic_fallback_parser import GenericFallbackParser
from shared.logging_engine import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/logs", tags=["log_parser"])

# Request / Response Schemas
class ParseLogRequest(BaseModel):
    ci_run_url: Optional[HttpUrl] = None
    raw_text: Optional[str] = None
    hint: Optional[str] = None

class ParsedEventResponse(BaseModel):
    test_name: str
    file_path: Optional[str]
    outcome: str
    duration_ms: Optional[int]
    error_message: Optional[str]
    stack_trace: Optional[str]
    low_confidence_parse: bool
    truncated: bool

class ParseLogResponse(BaseModel):
    events: List[ParsedEventResponse]
    total_found: int

# Mock LogSourcePort for standalone API
class HTTPLogSource(LogSourcePort):
    async def fetch_raw_log(self, ci_run_url: str) -> str:
        # In a real app, uses httpx to fetch. For now, raise NotImplemented if text not provided directly.
        raise NotImplementedError("Fetching by URL not fully implemented in stub")

def get_parser_registry() -> ParserRegistry:
    registry = ParserRegistry(fallback_parser=GenericFallbackParser())
    registry.register(JunitXmlParser())
    registry.register(PytestLogParser())
    registry.register(JestLogParser())
    return registry

@router.post("/parse", response_model=ParseLogResponse)
async def parse_log(req: ParseLogRequest):
    registry = get_parser_registry()
    use_case = ParseLogUseCase(HTTPLogSource(), registry)
    
    try:
        if req.raw_text:
            events = use_case.execute_raw(req.raw_text)
        elif req.ci_run_url:
            events = await use_case.execute(str(req.ci_run_url))
        else:
            raise HTTPException(status_code=400, detail="Must provide either raw_text or ci_run_url")
            
        return ParseLogResponse(
            events=[
                ParsedEventResponse(
                    test_name=e.test_name,
                    file_path=e.file_path,
                    outcome=e.outcome.value,
                    duration_ms=e.duration_ms,
                    error_message=e.error_message,
                    stack_trace=e.stack_trace,
                    low_confidence_parse=e.low_confidence_parse,
                    truncated=e.truncated
                ) for e in events
            ],
            total_found=len(events)
        )
    except PayloadTooLargeError as e:
        raise HTTPException(status_code=413, detail=str(e))
    except Exception as e:
        logger.error("Parse failed", exc_info=e)
        raise HTTPException(status_code=400, detail=str(e))
