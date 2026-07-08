import xml.etree.ElementTree as ET
from typing import List
from services.log_parser.domain.entities import ParsedLogEvent, TestOutcome, LogSpan
from services.log_parser.application.ports import LogParserPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class JunitXmlParser(LogParserPort):
    def can_parse(self, text: str) -> float:
        # Check if it starts like XML and contains testsuites/testsuite
        text_start = text[:500].strip()
        if text_start.startswith('<?xml') or '<testsuite' in text_start:
            return 0.98
        return 0.0

    def parse(self, text: str) -> List[ParsedLogEvent]:
        events = []
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            logger.warning("JUnit XML parse error", error=str(e))
            # Gracefully degrade by letting the registry fall back (by returning empty or partial)
            # Actually, returning empty will just yield no events. 
            # If we want fallback, we should raise or let registry handle it.
            # But the prompt says "catch XML parse errors, degrade to fallback parser".
            # By returning empty list, if we are the only parser, what happens? 
            # It's better to raise an exception here that the registry can catch.
            raise ValueError(f"Malformed XML: {e}")

        # Handle both <testsuites> and <testsuite> root
        suites = root.findall('.//testsuite')
        if root.tag == 'testsuite':
            suites = [root]

        for suite in suites:
            for case in suite.findall('testcase'):
                test_name = case.get('name', 'Unknown')
                file_path = case.get('file', case.get('classname', None))
                time_val = case.get('time')
                duration_ms = int(float(time_val) * 1000) if time_val else None
                
                outcome = TestOutcome.PASSED
                error_msg = None
                stack_trace = None
                
                failure = case.find('failure')
                error = case.find('error')
                skipped = case.find('skipped')
                
                if failure is not None:
                    outcome = TestOutcome.FAILED
                    error_msg = failure.get('message')
                    stack_trace = failure.text
                elif error is not None:
                    outcome = TestOutcome.ERROR
                    error_msg = error.get('message')
                    stack_trace = error.text
                elif skipped is not None:
                    outcome = TestOutcome.SKIPPED
                
                # We don't have line numbers for XML parsing easily, just use 0
                raw_xml = ET.tostring(case, encoding='unicode')
                span = LogSpan(start_line=0, end_line=0, raw_text=raw_xml)
                
                events.append(ParsedLogEvent(
                    test_name=test_name,
                    file_path=file_path,
                    outcome=outcome,
                    duration_ms=duration_ms,
                    span=span,
                    error_message=error_msg,
                    stack_trace=stack_trace
                ))
                
        return events
