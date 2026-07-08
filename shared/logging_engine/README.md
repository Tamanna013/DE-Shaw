# TestLens Logging Engine

Shared library for structured JSON logging and sensitive data redaction.

## Installation
Add to your `requirements.txt` or install directly:
```bash
pip install -e ./shared/logging_engine
```

## Usage
Configure logging at application startup:

```python
from shared.logging_engine import configure_logging, LoggingMiddleware

# ENV controls "prod" (JSON) vs "dev" (Console)
configure_logging(env="prod", module_name="auth")

app.add_middleware(LoggingMiddleware)
```

In your modules:
```python
from shared.logging_engine import get_logger

logger = get_logger(__name__)

logger.info("Something happened", user_id="123", password="super_secret")
# Output will have `password` automatically redacted!
```
