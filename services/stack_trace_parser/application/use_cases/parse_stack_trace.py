from typing import List
from services.stack_trace_parser.domain.entities import StackTrace, ExceptionInfo
from services.stack_trace_parser.domain.exceptions import UnrecognizedFormatError
from services.stack_trace_parser.infrastructure.normalizer import compute_normalized_signature, normalize_message
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class LanguageParserProtocol:
    def can_parse(self, raw_text: str) -> float:
        ...
    def parse(self, raw_text: str) -> ExceptionInfo:
        ...

class ParseStackTraceUseCase:
    def __init__(self, parsers: List[LanguageParserProtocol]):
        self.parsers = parsers

    def execute(self, raw_text: str) -> StackTrace:
        best_parser = None
        best_score = 0.0
        
        for parser in self.parsers:
            score = parser.can_parse(raw_text)
            if score > best_score:
                best_score = score
                best_parser = parser

        if best_score < 0.5 or not best_parser:
            logger.warning("Low confidence language detection", score=best_score)
            root = ExceptionInfo(type="Unknown", message="Unrecognized stack trace format", language="unknown")
            return StackTrace(raw_text=raw_text, root_exception=root)
            
        logger.debug("Parsed stack trace", language=best_parser.__class__.__name__, score=best_score)
        
        root_exc = best_parser.parse(raw_text)
        
        # Normalize the root exception
        root_exc.message = normalize_message(root_exc.message)
        root_exc.normalized_signature = compute_normalized_signature(root_exc)
        
        return StackTrace(raw_text=raw_text, root_exception=root_exc)
