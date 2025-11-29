# Test Patterns and Best Practices Guide

**Date:** 2025-11-08  
**Proposal:** review-test-suite  
**Section:** 7.3 Create test patterns and best practices guide

## Overview

This document provides patterns and best practices for writing tests in the ElevenTools project, based on analysis of the existing test suite and industry best practices.

## Test Organization

### Directory Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_api/                # API function tests
│   ├── test_elevenlabs_functions.py
│   └── test_openrouter_functions.py
├── test_utils/              # Utility function tests
│   ├── test_api_keys.py
│   ├── test_security.py
│   └── test_session_manager.py
├── test_web/                # Streamlit page tests
│   └── test_streamlit_pages.py
└── ui_tests/                # Playwright UI tests
    ├── conftest.py
    └── test_*.py
```

### Naming Conventions

**Test Files:**
- Use `test_<module_name>.py` format
- Match module structure (e.g., `test_api_keys.py` for `utils/api_keys.py`)

**Test Functions:**
- Use `test_<function_name>()` for function tests
- Use `test_<function_name>_<scenario>()` for scenario tests
- Use descriptive names that explain what is being tested

**Test Classes:**
- Use `Test<ClassName>` for class tests
- Group related tests together

**Examples:**
```python
# Good
def test_get_voice_id():
def test_get_voice_id_not_found():
def test_generate_audio_with_speed():

# Bad
def test1():
def test_thing():
def test_audio():
```

## Test Structure

### Arrange-Act-Assert Pattern

All tests should follow the Arrange-Act-Assert pattern:

```python
def test_example():
    # Arrange: Set up test data and mocks
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "success"}
    
    # Act: Execute the function being tested
    result = function_under_test(mock_response)
    
    # Assert: Verify the results
    assert result == "success"
```

### Test Organization

**Single Responsibility:**
- Each test should test one thing
- Split complex tests into multiple focused tests

**Example:**
```python
# Good - Single responsibility
def test_fetch_models_success():
    # Test successful API call
    pass

def test_fetch_models_error():
    # Test error handling
    pass

# Bad - Multiple responsibilities
def test_fetch_models():
    # Test success
    # Test error
    # Test caching
    pass
```

## Mocking Patterns

### Standard Mocking Library

**Use `pytest-mock` consistently:**
```python
def test_example(mocker):
    mock_get = mocker.patch("module.requests.get")
    # Use mock_get
```

### Mock Fixtures

**Create reusable mock fixtures in `conftest.py`:**
```python
@pytest.fixture
def mock_elevenlabs_response():
    mock = MagicMock()
    mock.json.return_value = [{"model_id": "model1", "name": "Model 1"}]
    mock.ok = True
    mock.content = b"fake content"
    return mock
```

### Mock Response Patterns

**Standardize mock response structures:**
```python
# ElevenLabs API response
mock_response = MagicMock()
mock_response.json.return_value = [{"model_id": "model1", "name": "Model 1"}]
mock_response.ok = True
mock_response.content = b"fake audio content"

# OpenRouter API response
mock_response = MagicMock(
    status_code=200,
    json=lambda: {"choices": [{"message": {"content": "response"}}]},
)
```

### Error Mocking

**Mock errors consistently:**
```python
# Network error
mocker.patch("module.requests.get", side_effect=requests.exceptions.ConnectionError())

# HTTP error
mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401")
```

## Fixture Patterns

### File System Fixtures

**Use `tmp_path` for file operations:**
```python
def test_file_operation(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    # Test file operations
```

### Session State Fixtures

**Mock Streamlit session state:**
```python
@pytest.fixture
def mock_session_state(monkeypatch):
    fake_session = {"key": "value"}
    monkeypatch.setattr(streamlit, "session_state", fake_session)
    return fake_session
```

### API Key Fixtures

**Mock API keys consistently:**
```python
@pytest.fixture(autouse=True)
def mock_api_key(monkeypatch):
    monkeypatch.setattr(module, "get_api_key", lambda: "fake-key")
```

## Assertion Patterns

### Descriptive Assertions

**Use descriptive assertion messages:**
```python
# Good
assert result == expected, f"Expected {expected}, got {result}"

# Better - Use pytest's assertion introspection
assert result == expected
```

### Multiple Assertions

**Group related assertions:**
```python
def test_voice_settings():
    result = generate_audio(...)
    assert result is True
    assert mock_post.called
    assert "voice_settings" in mock_post.call_args[1]["json"]
```

### Exception Assertions

**Test exceptions properly:**
```python
# Good
with pytest.raises(ValidationError, match="Speed must be between"):
    generate_audio(..., speed=3.0)

# Bad
try:
    generate_audio(..., speed=3.0)
    assert False, "Should have raised exception"
except ValidationError:
    pass
```

## UI Test Patterns

### Playwright Test Structure

**Use page objects or helper functions:**
```python
def test_page_loads(configured_page: Page, streamlit_server: str):
    configured_page.goto(f"{streamlit_server}/Settings")
    configured_page.wait_for_load_state("networkidle")
    # Assertions
```

### Waiting Patterns

**Use explicit waits:**
```python
# Good - Wait for specific element
configured_page.wait_for_selector("button", timeout=5000)

# Bad - Fixed sleep
time.sleep(2)
```

### Test Isolation

**Each test gets fresh page context:**
```python
@pytest.fixture
def configured_page(page: Page):
    # Configure page
    yield page
    # Cleanup if needed
```

## Test Documentation

### Docstrings

**Add docstrings to all test functions:**
```python
def test_generate_audio_with_speed(mocker):
    """Test that speed parameter is included in payload for multilingual models."""
    # Test implementation
```

### Test Organization Comments

**Use comments to organize test sections:**
```python
class TestGenerateAudio:
    """Tests for audio generation."""
    
    # Success cases
    def test_generate_audio_success(self):
        """Test successful audio generation."""
        pass
    
    # Error cases
    def test_generate_audio_error(self):
        """Test error handling."""
        pass
```

## Test Data Patterns

### Test Data Fixtures

**Create reusable test data:**
```python
@pytest.fixture
def sample_voices():
    return [
        ("voice1", "Voice 1"),
        ("voice2", "Voice 2"),
    ]

@pytest.fixture
def sample_voice_settings():
    return {
        "stability": 0.5,
        "similarity_boost": 0.7,
        "style": 0.5,
        "use_speaker_boost": True,
    }
```

### Parametrized Tests

**Use parametrized tests for similar scenarios:**
```python
@pytest.mark.parametrize("model_id,expected", [
    ("eleven_multilingual_v2", True),
    ("eleven_monolingual_v1", False),
])
def test_supports_speed(model_id, expected):
    assert supports_speed(model_id) == expected
```

## Error Handling Patterns

### Test Error Paths

**Test all error scenarios:**
```python
def test_api_error_handling():
    """Test handling of API errors."""
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401")
    with pytest.raises(APIError):
        function_that_calls_api()
```

### Test Error Messages

**Verify error messages are user-friendly:**
```python
def test_error_message():
    """Test that error messages are clear."""
    with pytest.raises(ValidationError) as exc_info:
        validate_input("")
    assert "required" in str(exc_info.value).lower()
```

## Performance Test Patterns

### Test Caching

**Verify caching works:**
```python
def test_caching():
    """Test that repeated calls use cache."""
    result1 = cached_function("input")
    result2 = cached_function("input")
    assert mock_api.call_count == 1  # Should only call once
```

### Test Memory Usage

**Verify memory management:**
```python
def test_memory_cleanup():
    """Test that memory is cleaned up."""
    # Generate large dataset
    # Verify cleanup
    assert memory_usage < threshold
```

## Integration Test Patterns

### End-to-End Tests

**Test complete workflows:**
```python
def test_translation_to_tts_workflow():
    """Test complete translation to TTS workflow."""
    # Translate text
    translated = translate_text("Hello", "fr")
    # Generate audio
    audio = generate_audio(translated, voice="voice1")
    # Verify result
    assert audio is not None
```

### API Integration Tests

**Test API integration with mocks:**
```python
def test_api_integration(mocker):
    """Test integration with external API."""
    mock_api = mocker.patch("module.external_api")
    mock_api.return_value = {"result": "success"}
    result = function_that_uses_api()
    assert result == "success"
    mock_api.assert_called_once()
```

## Best Practices Summary

### Do's

✅ **Do:**
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test one thing per test
- Use fixtures for reusable setup
- Mock external dependencies
- Add docstrings to tests
- Test error paths
- Use parametrized tests for similar scenarios
- Test behavior, not implementation
- Keep tests fast and isolated

### Don'ts

❌ **Don't:**
- Test implementation details
- Share state between tests
- Use fixed sleeps in tests
- Skip error handling tests
- Write tests that depend on execution order
- Use real external APIs in tests
- Write tests that are too long
- Duplicate test code
- Test multiple things in one test
- Ignore flaky tests

## Common Patterns Reference

### API Function Test Pattern

```python
def test_api_function(mocker):
    """Test API function with mocked response."""
    # Arrange
    mock_get = mocker.patch("module.requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "success"}
    mock_get.return_value = mock_response
    
    # Act
    result = api_function("input")
    
    # Assert
    assert result == "success"
    mock_get.assert_called_once()
```

### Utility Function Test Pattern

```python
def test_utility_function():
    """Test utility function with various inputs."""
    # Test normal case
    assert utility_function("input") == "expected"
    
    # Test edge case
    assert utility_function("") == "default"
    
    # Test error case
    with pytest.raises(ValueError):
        utility_function(None)
```

### UI Test Pattern

```python
def test_ui_feature(configured_page: Page, streamlit_server: str):
    """Test UI feature with Playwright."""
    # Navigate to page
    configured_page.goto(f"{streamlit_server}/Page")
    configured_page.wait_for_load_state("networkidle")
    
    # Interact with UI
    configured_page.fill("input", "value")
    configured_page.click("button")
    
    # Verify result
    expect(configured_page.locator("result")).to_be_visible()
```

## Conclusion

Following these patterns and best practices will ensure:
- Consistent test structure
- Maintainable test code
- Reliable test execution
- Clear test documentation
- Easy test debugging

For questions or clarifications, refer to existing test files or consult the test suite review documents.

