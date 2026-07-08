import re
from typing import List
from services.log_parser.domain.entities import ParsedLogEvent, TestOutcome, LogSpan
from services.log_parser.application.ports import LogParserPort

class JestLogParser(LogParserPort):
    def __init__(self):
        # PASS  src/App.test.js
        # FAIL  src/App.test.js
        self.file_pattern = re.compile(r'^(PASS|FAIL)\s+(.*?)$')
        # ✓ renders learn react link (20 ms)
        # ✕ renders learn react link (5 ms)
        self.test_pattern = re.compile(r'^\s*(✓|✕|x|✓)\s+(.*?)(?:\s+\((\d+)\s*ms\))?$')
        
    def can_parse(self, text: str) -> float:
        if 'jest' in text[:1000].lower():
            return 0.85
        if 'PASS ' in text[:1000] and 'FAIL ' in text[:1000]:
            return 0.65
        return 0.0

    def parse(self, text: str) -> List[ParsedLogEvent]:
        events = []
        lines = text.splitlines()
        
        current_file = None
        
        for i, line in enumerate(lines):
            file_match = self.file_pattern.search(line)
            if file_match:
                current_file = file_match.group(2).strip()
                continue
                
            test_match = self.test_pattern.search(line)
            if test_match:
                icon = test_match.group(1)
                test_name = test_match.group(2).strip()
                ms_str = test_match.group(3)
                
                outcome = TestOutcome.PASSED if icon in ('✓', 'v') else TestOutcome.FAILED
                duration_ms = int(ms_str) if ms_str else None
                
                events.append(ParsedLogEvent(
                    test_name=test_name,
                    file_path=current_file,
                    outcome=outcome,
                    duration_ms=duration_ms,
                    span=LogSpan(start_line=i, end_line=i, raw_text=line)
                ))
                
        return events
