import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Allow pytester to load our plugin
pytest_plugins = ["pytester"]

def test_plugin_noop_when_api_key_missing(pytester):
    # Ensure env var is missing
    with patch.dict(os.environ, clear=True):
        pytester.makepyfile("""
            def test_pass():
                assert True
        """)
        
        result = pytester.runpytest()
        
        # Verify it still passed and didn't crash
        result.assert_outcomes(passed=1)
        # Verify the no-op log message is printed
        assert "TestLens: API key not set" in result.stdout.str()

@patch('testlens_pytest.client.httpx.Client.post')
def test_batched_flush_triggers_at_batch_size(mock_post, pytester):
    mock_post.return_value.status_code = 200
    
    with patch.dict(os.environ, {"TESTLENS_API_KEY": "test-key", "TESTLENS_BATCH_SIZE": "2"}):
        pytester.makepyfile("""
            def test_1(): assert True
            def test_2(): assert True
            def test_3(): assert True
        """)
        
        result = pytester.runpytest()
        result.assert_outcomes(passed=3)
        
        # 3 tests, batch size 2. Should flush at test 2, and then final flush at session finish
        assert mock_post.call_count == 2
        
        # Verify first payload had 2 items
        first_call_json = mock_post.call_args_list[0][1]['json']
        assert len(first_call_json['results']) == 2
        
        # Verify second payload had 1 item
        second_call_json = mock_post.call_args_list[1][1]['json']
        assert len(second_call_json['results']) == 1

@patch('testlens_pytest.client.httpx.Client.post')
def test_network_failure_does_not_fail_test_run(mock_post, pytester):
    # Simulate API being completely down
    mock_post.side_effect = Exception("Connection Refused")
    
    with patch.dict(os.environ, {"TESTLENS_API_KEY": "test-key", "TESTLENS_BATCH_SIZE": "1"}):
        pytester.makepyfile("""
            def test_pass():
                assert True
        """)
        
        result = pytester.runpytest()
        
        # Customer CI should STILL PASS with exit code 0
        assert result.ret == 0
        result.assert_outcomes(passed=1)

@patch('testlens_pytest.client.httpx.Client.post')
def test_output_truncation_at_configured_limit(mock_post, pytester):
    mock_post.return_value.status_code = 200
    
    # Set limit tiny (10 chars)
    with patch.dict(os.environ, {"TESTLENS_API_KEY": "test", "TESTLENS_MAX_OUTPUT_SIZE": "10"}):
        pytester.makepyfile("""
            def test_noisy():
                print("1234567890_THIS_SHOULD_BE_TRUNCATED")
                assert True
        """)
        
        result = pytester.runpytest("-s")
        
        call_json = mock_post.call_args_list[0][1]['json']
        stdout = call_json['results'][0]['stdout']
        
        assert stdout.startswith("1234567890")
        assert "[...truncated" in stdout
        assert "_THIS_SHOULD_BE_TRUNCATED" not in stdout

@patch('testlens_pytest.client.httpx.Client.post')
def test_collection_error_captured_as_distinct_event(mock_post, pytester):
    mock_post.return_value.status_code = 200
    
    with patch.dict(os.environ, {"TESTLENS_API_KEY": "test"}):
        # Create a file that fails during import (collection)
        pytester.makepyfile("""
            import non_existent_module_that_crashes
            
            def test_pass():
                assert True
        """)
        
        result = pytester.runpytest()
        assert result.ret != 0
        
        # Verify it flushed a collection_error
        assert mock_post.call_count == 1
        call_json = mock_post.call_args_list[0][1]['json']
        
        res = call_json['results'][0]
        assert res['outcome'] == 'collection_error'
        assert "ModuleNotFoundError" in res['error_message']
