from typing import List, Optional
from services.log_parser.domain.entities import ParsedLogEvent
from services.log_parser.application.ports import LogParserPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class ParserRegistry:
    def __init__(self, fallback_parser: LogParserPort):
        self.parsers: List[LogParserPort] = []
        self.fallback_parser = fallback_parser
        self.threshold = 0.6

    def register(self, parser: LogParserPort) -> None:
        self.parsers.append(parser)

    def detect_and_parse(self, raw_text: str, hint: Optional[str] = None) -> List[ParsedLogEvent]:
        best_parser = None
        best_score = 0.0
        
        for parser in self.parsers:
            score = parser.can_parse(raw_text)
            logger.debug("Evaluated parser", parser=parser.__class__.__name__, score=score)
            
            if score > best_score:
                best_score = score
                best_parser = parser

        if best_score >= self.threshold and best_parser:
            logger.info("Selected parser", parser=best_parser.__class__.__name__, score=best_score)
            return best_parser.parse(raw_text)
            
        logger.warning("No high confidence parser found. Falling back to generic.", best_score=best_score)
        events = self.fallback_parser.parse(raw_text)
        
        for event in events:
            event.low_confidence_parse = True
            
        return events
