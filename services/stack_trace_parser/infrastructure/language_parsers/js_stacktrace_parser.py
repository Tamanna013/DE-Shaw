import re
from services.stack_trace_parser.domain.entities import ExceptionInfo, StackFrame

class JsStacktraceParser:
    def can_parse(self, raw_text: str) -> float:
        if re.search(r'^\s*at .*? \(.*?:\d+:\d+\)', raw_text, re.MULTILINE):
            return 0.9
        if "TypeError:" in raw_text or "ReferenceError:" in raw_text:
            if "at " in raw_text:
                return 0.7
        return 0.0

    def parse(self, raw_text: str) -> ExceptionInfo:
        lines = raw_text.splitlines()
        frames = []
        
        exc_type = "Error"
        exc_msg = ""
        needs_sourcemap = False
        
        if lines:
            header_parts = lines[0].split(":", 1)
            exc_type = header_parts[0].strip()
            exc_msg = header_parts[1].strip() if len(header_parts) > 1 else ""
            
        # e.g., "    at Object.<anonymous> (/app/index.js:5:10)"
        frame_pattern = re.compile(r'^\s*at (.*?)\s+\((.*?):(\d+):(\d+)\)')
        # e.g., "    at /app/index.js:5:10"
        frame_pattern_anon = re.compile(r'^\s*at (.*?):(\d+):(\d+)')
        
        last_frame = None
        
        for line in lines[1:]:
            path = None
            func = None
            lineno = None
            
            match = frame_pattern.match(line)
            if match:
                func = match.group(1)
                path = match.group(2)
                lineno = int(match.group(3))
            else:
                match_anon = frame_pattern_anon.match(line)
                if match_anon:
                    func = "<anonymous>"
                    path = match_anon.group(1)
                    lineno = int(match_anon.group(2))
                    
            if path:
                is_ext = 'node_modules' in path or path.startswith('internal/')
                
                # Check for minification (line 1, col 50000)
                col_match = re.search(r':(\d+)$', line)
                if col_match and int(col_match.group(1)) > 500 and lineno == 1:
                    needs_sourcemap = True
                
                new_frame = StackFrame(
                    file_path=path,
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
            language="js",
            needs_sourcemap=needs_sourcemap
        )
