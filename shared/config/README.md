# Shared Config Package

A strongly-typed, Pydantic-backed configuration layer for all TestLens services. 

## Architectural Rules
1. **No direct `os.environ` access:** No service code may read environment variables directly. All configuration must flow through a `Settings` class inheriting from this package.
2. **Fail Fast**: The settings class is instantiated in `main.py` at import time. If a required environment variable is missing, the container crashes instantly with a clear `ValidationError` rather than dying mysteriously hours later when the missing value is accessed.
3. **Secret Masking**: All sensitive fields (Passwords, DB URLs, API Keys) MUST use `pydantic.SecretStr`. This guarantees that if the `settings` object is accidentally passed to a logger, the secrets render as `**********`. To access the raw string, code must explicitly call `.get_secret_value()`.
4. **Composition**: Services use multiple inheritance to compose only the setting groups they actually need. Example:
   ```python
   class FailureAnalyzerSettings(BaseServiceSettings, DatabaseSettings, RedisSettings):
       pass
   ```
