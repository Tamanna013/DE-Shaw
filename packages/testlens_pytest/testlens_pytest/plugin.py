import pytest
import platform
import sys
import hashlib
from typing import List, Dict, Optional
from testlens_pytest.config import config
from testlens_pytest.client import TestLensClient
from testlens_pytest.models import TestResultPayload

class TestLensPlugin:
    def __init__(self):
        self.client = TestLensClient(config.api_key, config.repo_id, config.endpoint)
        self.batch: List[TestResultPayload] = []
        self.env_fingerprint = self._generate_fingerprint()

    def _generate_fingerprint(self) -> Dict[str, str]:
        # Capture basic environment details
        return {
            "python_version": sys.version.split(" ")[0],
            "os": platform.system(),
            "os_release": platform.release(),
        }

    def _truncate(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return text
        if len(text) > config.max_output_size:
            truncated_bytes = len(text) - config.max_output_size
            return text[:config.max_output_size] + f"\n\n[...truncated {truncated_bytes} bytes...]"
        return text

    def _flush_if_needed(self, force: bool = False):
        if len(self.batch) >= config.batch_size or (force and self.batch):
            self.client.flush_batch(self.batch)
            self.batch.clear()

    @pytest.hookimpl(trylast=True)
    def pytest_runtest_logreport(self, report):
        if not config.is_enabled:
            return

        # We only care about the call phase for standard passes/fails,
        # but setup/teardown errors are also important.
        if report.when != "call" and report.outcome == "passed":
            return
            
        # Determine true outcome
        outcome = report.outcome
        if report.when in ("setup", "teardown") and report.outcome == "failed":
            outcome = "error" # Distinguish setup/teardown failures from test failures
            
        duration = getattr(report, "duration", 0.0)
        
        # Get stdout/stderr from sections
        stdout = ""
        stderr = ""
        for name, content in getattr(report, "sections", []):
            if name == "Captured stdout call":
                stdout = content
            elif name == "Captured stderr call":
                stderr = content
                
        error_message = None
        stack_trace = None
        
        if report.longrepr:
            # longrepr can be a string or an object depending on failure type
            stack_trace = str(report.longrepr)
            if hasattr(report.longrepr, "reprcrash") and report.longrepr.reprcrash:
                error_message = report.longrepr.reprcrash.message
                
        # Handle pytest-rerunfailures if present
        retry_count = getattr(report, "rerun", 0)

        payload = TestResultPayload(
            test_id=report.nodeid,
            outcome=outcome,
            duration=duration,
            stdout=self._truncate(stdout),
            stderr=self._truncate(stderr),
            error_message=self._truncate(error_message),
            stack_trace=self._truncate(stack_trace),
            retry_count=retry_count,
            environment=self.env_fingerprint
        )
        
        self.batch.append(payload)
        self._flush_if_needed()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_sessionfinish(self, session, exitstatus):
        yield
        if config.is_enabled:
            self._flush_if_needed(force=True)

    @pytest.hookimpl(trylast=True)
    def pytest_collectreport(self, report):
        if not config.is_enabled:
            return
            
        if report.failed:
            payload = TestResultPayload(
                test_id=report.nodeid,
                outcome="collection_error",
                duration=0.0,
                error_message=self._truncate(str(report.longrepr)),
                stack_trace=self._truncate(str(report.longrepr)),
                environment=self.env_fingerprint
            )
            self.batch.append(payload)
            self._flush_if_needed()

def pytest_configure(config_pytest):
    if config.is_enabled:
        plugin = TestLensPlugin()
        config_pytest.pluginmanager.register(plugin, "testlens_plugin")
    else:
        # No-op gracefully
        print("\nTestLens: API key not set (TESTLENS_API_KEY). Plugin disabled.")
