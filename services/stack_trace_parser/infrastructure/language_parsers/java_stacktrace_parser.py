import re
from services.stack_trace_parser.domain.entities import ExceptionInfo, StackFrame

class JavaStacktraceParser:
    def can_parse(self, raw_text: str) -> float:
        if re.search(r'Exception in thread ".*?"', raw_text):
            return 1.0
        if re.search(r'^\s*at [\w\.\$]+\([\w\.\$]+:\d+\)', raw_text, re.MULTILINE):
            return 0.8
        return 0.0

    def parse(self, raw_text: str) -> ExceptionInfo:
        chains = re.split(r'^\s*Caused by:\s*', raw_text, flags=re.MULTILINE)
        
        exceptions = []
        for chain_text in chains:
            if not chain_text.strip():
                continue
            exc = self._parse_single(chain_text.strip())
            exceptions.append(exc)
            
        root = exceptions[0]
        root.cause_chain = exceptions[1:]
        return root

    def _parse_single(self, text: str) -> ExceptionInfo:
        lines = text.splitlines()
        frames = []
        
        header_pattern = re.compile(r'(?:Exception in thread ".*?"\s*)?([\w\.\$]+Exception):?(.*)')
        frame_pattern = re.compile(r'^\s*at ([\w\.\$]+)\((.*?)(?::(\d+))?\)')
        
        exc_type = "UnknownException"
        exc_msg = ""
        
        header_match = header_pattern.match(lines[0])
        if header_match:
            exc_type = header_match.group(1)
            exc_msg = header_match.group(2).strip()
            
        last_frame = None
            
        for line in lines[1:]:
            frame_match = frame_pattern.match(line)
            if frame_match:
                func = frame_match.group(1)
                file_path = frame_match.group(2)
                lineno_str = frame_match.group(3)
                
                lineno = int(lineno_str) if lineno_str else None
                
                is_ext = any(x in func for x in ['java.lang', 'java.util', 'org.springframework', 'sun.reflect'])
                
                new_frame = StackFrame(
                    file_path=file_path,
                    function_name=func,
                    line_number=lineno,
                    is_external=is_ext
                )
                
                if last_frame and last_frame.file_path == new_frame.file_path and last_frame.function_name == new_frame.function_name and last_frame.line_number == new_frame.line_number:
                    last_frame.repeated_count += 1
                else:
                    frames.append(new_frame)
                    last_frame = new_frame
                    
        return ExceptionInfo(
            type=exc_type,
            message=exc_msg,
            frames=frames,
            language="java"
        )
