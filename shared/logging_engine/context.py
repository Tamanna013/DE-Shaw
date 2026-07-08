import contextvars
from typing import Optional

_trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)

def bind_trace_id(trace_id: str) -> contextvars.Token:
    return _trace_id_var.set(trace_id)

def get_trace_id() -> Optional[str]:
    return _trace_id_var.get()

def clear_trace_id(token: contextvars.Token) -> None:
    _trace_id_var.reset(token)
