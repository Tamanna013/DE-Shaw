import re

# Optimized regex for matching ANSI escape sequences
# Covers standard colors, extended colors, and cursor movements
ANSI_ESCAPE_PATTERN = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

def strip_ansi(text: str) -> str:
    """Removes all ANSI color and formatting codes from the text."""
    if not text:
        return text
    return ANSI_ESCAPE_PATTERN.sub('', text)
