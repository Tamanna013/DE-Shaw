import re
from services.stack_trace_parser.domain.entities import ExceptionInfo, StackFrame

class GoPanicParser:
    def can_parse(self, raw_text: str) -> float:
        if raw_text.startswith("panic: "):
            return 1.0
        if "goroutine" in raw_text and "[running]:" in raw_text:
            return 0.9
        return 0.0

    def parse(self, raw_text: str) -> ExceptionInfo:
        lines = raw_text.splitlines()
        frames = []
        
        exc_type = "panic"
        exc_msg = ""
        
        if lines and lines[0].startswith("panic: "):
            exc_msg = lines[0][7:].strip()
            
        # Go frames span two lines usually:
        # main.main()
        #         /app/main.go:10 +0x45
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("goroutine") or line.startswith("panic:"):
                i += 1
                continue
                
            func_name = line
            
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                # matching /app/main.go:10 +0x45
                match = re.search(r'^(.*?):(\d+)(?: \+0x[0-9a-f]+)?$', next_line)
                if match:
                    path = match.group(1)
                    lineno = int(match.group(2))
                    
                    is_ext = not path.startswith("/") and not path.startswith(".") # rudimentary check for stdlib
                    frames.append(StackFrame(
                        file_path=path,
                        function_name=func_name,
                        line_number=lineno,
                        is_external=is_ext
                    ))
                    i += 2
                    continue
            i += 1
            
        return ExceptionInfo(
            type=exc_type,
            message=exc_msg,
            frames=frames,
            language="go"
        )
