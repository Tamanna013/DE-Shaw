import re
from typing import Any, Dict

# Configurable patterns. In a real app these could be loaded from a config file.
REDACTION_KEYS = {"password", "token", "authorization", "api_key", "secret"}
EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*(@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")

def _mask_email(email: str) -> str:
    match = EMAIL_PATTERN.fullmatch(email)
    if match:
        return f"{match.group(1)}***{match.group(2)}"
    return email

def _redact_value(key: str, value: Any) -> Any:
    key_lower = str(key).lower()
    
    if any(redact_key in key_lower for redact_key in REDACTION_KEYS):
        return "***REDACTED***"
        
    if isinstance(value, str) and "@" in value:
        # Simple heuristic, full match on email regex
        if EMAIL_PATTERN.fullmatch(value):
            return _mask_email(value)
            
    return value

def _recursively_redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _recursively_redact(_redact_value(k, v)) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_recursively_redact(item) for item in obj]
    return obj

def redact_sensitive_data_processor(logger, method_name, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Structlog processor that recursively searches log payloads for sensitive keys/patterns
    and masks them.
    """
    return _recursively_redact(event_dict) # type: ignore
