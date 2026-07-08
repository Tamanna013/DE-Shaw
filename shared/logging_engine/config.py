import logging
import structlog
import os
from typing import Literal
from .redaction import redact_sensitive_data_processor
from .context import get_trace_id

def add_trace_id(logger, method_name, event_dict):
    trace_id = get_trace_id()
    if trace_id:
        event_dict["trace_id"] = trace_id
    return event_dict

def configure_logging(env: Literal["dev", "prod"] = "prod", module_name: str = "app"):
    global_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    module_level_str = os.environ.get(f"LOG_LEVEL__{module_name.upper()}", global_level_str)
    
    level = getattr(logging, module_level_str, logging.INFO)

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_trace_id,
        redact_sensitive_data_processor,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if env == "prod":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=os.sys.stdout,
        level=level,
    )

def get_logger(name: str):
    return structlog.get_logger(name)
