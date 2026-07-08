import hashlib
import re
from services.stack_trace_parser.domain.entities import ExceptionInfo

# Config-driven regex replacements for normalization
NORMALIZATION_RULES = [
    (re.compile(r'0x[0-9a-fA-F]+'), '<HEX>'), # Memory addresses
    (re.compile(r'\b\d{10,}\b'), '<NUM>'), # Timestamps or long IDs
    (re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I), '<UUID>'),
    (re.compile(r'(/[\w\.\-]+)+'), '<PATH>'), # File paths
]

def normalize_message(message: str) -> str:
    """Strips dynamic tokens from the message."""
    if not message:
        return ""
        
    norm_msg = message
    for pattern, replacement in NORMALIZATION_RULES:
        norm_msg = pattern.sub(replacement, norm_msg)
        
    return norm_msg

def compute_normalized_signature(exc: ExceptionInfo) -> str:
    """
    Computes normalized_signature = sha256(exception_type + "|" + normalized_message + "|" + top_3_user_frames)
    """
    parts = [exc.type, exc.message]
    
    user_frames = [f for f in exc.frames if not f.is_external]
    top_frames = user_frames[:3]
    
    for f in top_frames:
        parts.append(f"{f.file_path}:{f.function_name}")
        
    signature_base = "|".join(parts)
    return hashlib.sha256(signature_base.encode('utf-8')).hexdigest()
