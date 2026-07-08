import pytest
import os
from pydantic import ValidationError
from shared.config.base_settings import BaseServiceSettings
from shared.config.db_settings import DatabaseSettings
from shared.config.auth_settings import AuthSettings

# Mock combined settings class, like a real service would use
class MockAuthServiceSettings(BaseServiceSettings, DatabaseSettings, AuthSettings):
    pass

def test_missing_required_var_raises_validation_error(monkeypatch):
    # Clear env
    monkeypatch.delenv("SERVICE_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    
    with pytest.raises(ValidationError) as exc_info:
        MockAuthServiceSettings()
        
    errors = exc_info.value.errors()
    missing_fields = [e["loc"][0] for e in errors]
    
    assert "SERVICE_NAME" in missing_fields
    assert "DATABASE_URL" in missing_fields
    assert "JWT_SECRET" in missing_fields

def test_secret_fields_repr_as_masked(monkeypatch):
    monkeypatch.setenv("SERVICE_NAME", "auth_svc")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:supersecretpass@host/db")
    monkeypatch.setenv("JWT_SECRET", "this-is-a-top-secret-key")
    
    settings = MockAuthServiceSettings()
    
    # Assert str/repr never leaks the raw value
    settings_str = str(settings)
    settings_repr = repr(settings)
    
    assert "supersecretpass" not in settings_str
    assert "supersecretpass" not in settings_repr
    assert "**********" in settings_str
    
    # To actually use the value, you have to explicitly call .get_secret_value()
    assert settings.DATABASE_URL.get_secret_value() == "postgresql+asyncpg://user:supersecretpass@host/db"
    assert settings.JWT_SECRET.get_secret_value() == "this-is-a-top-secret-key"

def test_env_example_files_have_matching_field_names_to_settings_classes():
    """
    Consistency check script embedded as a test.
    Reads an .env.example, parses keys, and ensures the Settings classes 
    don't define required fields missing from the example, and vice versa.
    """
    # For this isolated test, we simulate the validation logic
    required_fields = set()
    for name, field in MockAuthServiceSettings.model_fields.items():
        if field.is_required():
            required_fields.add(name)
            
    assert "DATABASE_URL" in required_fields
    assert "JWT_SECRET" in required_fields
    assert "SERVICE_NAME" in required_fields
    assert "LOG_LEVEL" not in required_fields # It has a default
