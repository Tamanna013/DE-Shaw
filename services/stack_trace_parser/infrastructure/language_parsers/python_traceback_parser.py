import re
from services.stack_trace_parser.domain.entities import ExceptionInfo, StackFrame

class PythonTracebackParser:
    def can_parse(self, raw_text: str) -> float:
        if "Traceback (most recent call last):" in raw_text:
            return 1.0
        if re.search(r'File ".*?", line \d+, in', raw_text):
            return 0.8
        return 0.0

    def parse(self, raw_text: str) -> ExceptionInfo:
        # Handles chained exceptions by splitting on "During handling of the above exception..."
        chains = re.split(r'During handling of the above exception, another exception occurred:|The above exception was the direct cause of the following exception:', raw_text)
        
        exceptions = []
        for chain_text in reversed(chains): # Python prints root cause at the bottom usually? Actually, the outermost is at bottom.
            # Root cause is actually at the bottom.
            exc = self._parse_single(chain_text.strip())
            exceptions.append(exc)
            
        root = exceptions[0]
        root.cause_chain = exceptions[1:]
        return root

    def _parse_single(self, text: str) -> ExceptionInfo:
        lines = text.splitlines()
        frames = []
        exc_type = "UnknownError"
        exc_msg = "Unknown error"
        
        frame_pattern = re.compile(r'File "(.*?)", line (\d+), in (.*)')
        
        last_frame = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("Traceback"):
                continue
                
            frame_match = frame_pattern.search(line)
            if frame_match:
                path = frame_match.group(1)
                lineno = int(frame_match.group(2))
                func = frame_match.group(3)
                
                is_ext = any(x in path for x in ['site-packages', 'dist-packages', 'lib/python'])
                
                new_frame = StackFrame(
                    file_path=path,
                    function_name=func,
                    line_number=lineno,
                    is_external=is_ext
                )
                
                # Collapse repeated recursive frames
                if last_frame and last_frame.file_path == new_frame.file_path and last_frame.function_name == new_frame.function_name and last_frame.line_number == new_frame.line_number:
                    last_frame.repeated_count += 1
                else:
                    frames.append(new_frame)
                    last_frame = new_frame
                    
            elif ":" in line and not line.startswith("File"):
                # Potential Exception Type: Message
                parts = line.split(":", 1)
                exc_type = parts[0].strip()
                exc_msg = parts[1].strip() if len(parts) > 1 else ""
                
        return ExceptionInfo(
            type=exc_type,
            message=exc_msg,
            frames=frames,
            language="python"
        )
