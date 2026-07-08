import re
from typing import List
from services.log_parser.domain.entities import ParsedLogEvent, TestOutcome, LogSpan
from services.log_parser.application.ports import LogParserPort

class GenericFallbackParser(LogParserPort):
    """Heuristic line-based parser for unknown formats. Scans for PASS/FAIL/ERR keywords."""
    
    def can_parse(self, text: str) -> float:
        return 0.1 # Very low confidence, acts only as fallback
        
    def parse(self, text: str) -> List[ParsedLogEvent]:
        events = []
        lines = text.splitlines()
        
        # Super simple O(N) heuristic scan
        # E.g.: "tests/foo.py::test_bar - PASS"
        pattern = re.compile(r'^(.*?)\s*[-:]\s*(PASS|FAIL|ERROR|ERR|OK|FAILED)\b', re.IGNORECASE)
        
        for i, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                test_name = match.group(1).strip()
                status_str = match.group(2).upper()
                
                if status_str in ("PASS", "OK"):
                    outcome = TestOutcome.PASSED
                elif status_str in ("FAIL", "FAILED", "ERROR", "ERR"):
                    outcome = TestOutcome.FAILED
                else:
                    continue
                    
                # We can't reliably guess the span or stack trace in generic fallback
                events.append(ParsedLogEvent(
                    test_name=test_name,
                    file_path=None,
                    outcome=outcome,
                    duration_ms=None,
                    span=LogSpan(start_line=i, end_line=i, raw_text=line),
                    low_confidence_parse=True
                ))
                
        return events
