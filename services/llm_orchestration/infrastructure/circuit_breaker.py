import time
from typing import Dict
from services.llm_orchestration.application.ports import CircuitBreakerPort

class SlidingWindowCircuitBreaker(CircuitBreakerPort):
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        
        self.state: Dict[str, dict] = {}

    def _init_provider(self, provider: str):
        if provider not in self.state:
            self.state[provider] = {
                "failures": 0,
                "opened_at": 0.0
            }

    def record_success(self, provider_name: str) -> None:
        self._init_provider(provider_name)
        # Reset failures on success
        self.state[provider_name]["failures"] = 0
        self.state[provider_name]["opened_at"] = 0.0

    def record_failure(self, provider_name: str) -> None:
        self._init_provider(provider_name)
        self.state[provider_name]["failures"] += 1
        
        if self.state[provider_name]["failures"] >= self.failure_threshold and self.state[provider_name]["opened_at"] == 0.0:
            self.state[provider_name]["opened_at"] = time.time()

    def is_open(self, provider_name: str) -> bool:
        self._init_provider(provider_name)
        st = self.state[provider_name]
        
        if st["failures"] >= self.failure_threshold:
            time_since_open = time.time() - st["opened_at"]
            if time_since_open >= self.cooldown_seconds:
                # Half-open: let a request through to test it
                st["failures"] = self.failure_threshold - 1 
                return False
            return True
            
        return False
