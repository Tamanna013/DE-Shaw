import sys
from typing import List
from services.log_parser.domain.entities import ParsedLogEvent
from services.log_parser.domain.exceptions import PayloadTooLargeError
from services.log_parser.application.ports import LogSourcePort
from services.log_parser.infrastructure.parser_registry import ParserRegistry
from services.log_parser.infrastructure.ansi_stripper import strip_ansi
from shared.logging_engine import get_logger

logger = get_logger(__name__)

MAX_PAYLOAD_SIZE = 50 * 1024 * 1024 # 50MB

class ParseLogUseCase:
    def __init__(self, log_source: LogSourcePort, registry: ParserRegistry):
        self.log_source = log_source
        self.registry = registry

    async def execute(self, ci_run_url: str) -> List[ParsedLogEvent]:
        raw_text = await self.log_source.fetch_raw_log(ci_run_url)
        return self._process_text(raw_text)

    def execute_raw(self, raw_text: str) -> List[ParsedLogEvent]:
        return self._process_text(raw_text)
        
    def _process_text(self, raw_text: str) -> List[ParsedLogEvent]:
        size = sys.getsizeof(raw_text)
        if size > MAX_PAYLOAD_SIZE:
            logger.warning("Payload too large", size_bytes=size, limit_bytes=MAX_PAYLOAD_SIZE)
            raise PayloadTooLargeError(size, MAX_PAYLOAD_SIZE)
            
        clean_text = strip_ansi(raw_text)
        
        try:
            events = self.registry.detect_and_parse(clean_text)
            logger.info("Successfully parsed log", event_count=len(events))
            return events
        except Exception as e:
            sample = clean_text[:500] if clean_text else ""
            logger.error("Unrecoverable parse failure", exc_info=e, log_sample=sample)
            raise
