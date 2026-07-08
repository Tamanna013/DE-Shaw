import re
from typing import List
from services.log_parser.domain.entities import ParsedLogEvent, TestOutcome, LogSpan
from services.log_parser.application.ports import LogParserPort

class PytestLogParser(LogParserPort):
    def __init__(self):
        # Matches typical pytest line: "tests/test_file.py::test_name PASSED [ 50%]"
        # or with xdist: "[gw0] [ 50%] PASSED tests/test_file.py::test_name"
        self.header_pattern = re.compile(r'===\s*test session starts\s*===')
        self.outcome_pattern = re.compile(r'(PASSED|FAILED|SKIPPED|ERROR)')
        
        # [gw0] PASSED test.py::func
        self.xdist_pattern = re.compile(r'\[(gw\d+)\]\s+.*?(PASSED|FAILED|SKIPPED|ERROR)\s+(.*?::.*?)$')
        # test.py::func PASSED
        self.standard_pattern = re.compile(r'^(.*?::.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)')
        
    def can_parse(self, text: str) -> float:
        # Check first 5000 chars for pytest headers
        if self.header_pattern.search(text[:5000]):
            return 0.95
        if 'pytest' in text[:1000].lower():
            return 0.7
        return 0.0

    def parse(self, text: str) -> List[ParsedLogEvent]:
        events = []
        lines = text.splitlines()
        
        # State tracking for failure tracebacks
        in_failure_block = False
        current_failure_test = None
        current_failure_lines = []
        
        for i, line in enumerate(lines):
            # Try xdist first
            xdist_match = self.xdist_pattern.search(line)
            if xdist_match:
                worker_id = xdist_match.group(1)
                outcome_str = xdist_match.group(2)
                test_id = xdist_match.group(3).strip()
                events.append(self._build_event(test_id, outcome_str, i, line, worker_id))
                continue
                
            # Try standard pytest
            std_match = self.standard_pattern.search(line)
            if std_match:
                test_id = std_match.group(1).strip()
                outcome_str = std_match.group(2)
                events.append(self._build_event(test_id, outcome_str, i, line, None))
                continue
                
            # Failure block tracking (very simplified O(N) scan)
            if line.startswith('___') and line.endswith('___'):
                in_failure_block = True
                current_failure_test = line.strip('_ ')
                current_failure_lines = [line]
            elif in_failure_block:
                if line.startswith('==='): # End of failures
                    in_failure_block = False
                    self._attach_failure(events, current_failure_test, "\n".join(current_failure_lines))
                elif line.startswith('___') and line.endswith('___'): # Next failure
                    self._attach_failure(events, current_failure_test, "\n".join(current_failure_lines))
                    current_failure_test = line.strip('_ ')
                    current_failure_lines = [line]
                else:
                    current_failure_lines.append(line)
                    
        return events

    def _build_event(self, test_id: str, outcome_str: str, line_idx: int, line_text: str, worker_id: str = None) -> ParsedLogEvent:
        parts = test_id.split('::')
        file_path = parts[0] if len(parts) > 1 else None
        
        outcome_map = {
            'PASSED': TestOutcome.PASSED,
            'FAILED': TestOutcome.FAILED,
            'SKIPPED': TestOutcome.SKIPPED,
            'ERROR': TestOutcome.ERROR,
        }
        
        return ParsedLogEvent(
            test_name=test_id,
            file_path=file_path,
            outcome=outcome_map.get(outcome_str, TestOutcome.FAILED),
            duration_ms=None, # Pytest console output usually lacks per-test MS timings without plugins
            span=LogSpan(start_line=line_idx, end_line=line_idx, raw_text=line_text),
            worker_id=worker_id
        )
        
    def _attach_failure(self, events: List[ParsedLogEvent], test_name: str, stack_trace: str):
        if not test_name:
            return
        # Find the matching event and attach the trace
        for event in reversed(events): # Usually at the end
            if test_name in event.test_name:
                event.stack_trace = stack_trace
                break
