from typing import Protocol, List
from services.log_parser.domain.entities import ParsedLogEvent

class LogSourcePort(Protocol):
    async def fetch_raw_log(self, ci_run_url: str) -> str:
        ...

class LogParserPort(Protocol):
    def can_parse(self, text: str) -> float:
        """Returns a confidence score between 0.0 and 1.0"""
        ...
        
    def parse(self, text: str) -> List[ParsedLogEvent]:
        """Parses the text and returns structured events"""
        ...
