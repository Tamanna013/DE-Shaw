import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if hasattr(record, 'trace_id'):
            log_data['trace_id'] = record.trace_id # type: ignore
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id # type: ignore
        if hasattr(record, 'ip'):
            log_data['ip'] = record.ip # type: ignore
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Redact password if present in message (though we avoid logging it entirely)
        msg = log_data['message'].lower()
        if 'password' in msg:
            log_data['message'] = '*** REDACTED ***'
            
        return json.dumps(log_data)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
