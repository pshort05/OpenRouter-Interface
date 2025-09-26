"""
Shared test fixtures and utilities for OpenRouter Interface tests.

This module provides common fixtures, mock objects, and utility functions
used across the test suite.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch

import pytest
import yaml


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_config():
    """Basic configuration dictionary for testing."""
    return {
        'model': 'anthropic/claude-4-sonnet-20250522',
        'api_base_url': 'https://openrouter.ai/api/v1',
        'temperature': 0.8,
        'max_tokens': 25000,
        'log_level': 'INFO',
        'log_to_file': False
    }


@pytest.fixture
def sample_config_file(temp_dir, sample_config):
    """Create a temporary YAML config file."""
    config_file = temp_dir / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    return config_file


@pytest.fixture
def sample_prompt():
    """Basic prompt dictionary for testing."""
    return {
        "instruction": "You are a content quality evaluator. Analyze the provided text for clarity and coherence.",
        "persona": "Professional Content Analyst",
        "evaluation_directives": {
            "clarity": "Assess how clearly ideas are expressed",
            "coherence": "Evaluate how well ideas flow together"
        },
        "output_format": "Provide structured analysis with recommendations."
    }


@pytest.fixture
def sample_prompt_file(temp_dir, sample_prompt):
    """Create a temporary JSON prompt file."""
    prompt_file = temp_dir / "test_prompt.json"
    with open(prompt_file, 'w') as f:
        json.dump(sample_prompt, f, indent=2)
    return prompt_file


@pytest.fixture
def multiple_prompt_files(temp_dir):
    """Create multiple prompt files for multi-prompt testing."""
    prompts = [
        {
            "instruction": "You are a grammar checker. Fix grammatical errors.",
            "persona": "Grammar Expert",
            "output_format": "Return corrected text."
        },
        {
            "instruction": "You are a style editor. Improve writing style.",
            "persona": "Style Editor",
            "review_criteria": {
                "style": {
                    "mistake": "Poor writing style",
                    "how_to_fix": "Use consistent tone and precise words"
                }
            }
        },
        {
            "instruction": "You are a readability enhancer. Improve text clarity.",
            "persona": "Readability Expert"
        }
    ]

    prompt_files = []
    for i, prompt in enumerate(prompts):
        prompt_file = temp_dir / f"test_prompt_{i+1}.json"
        with open(prompt_file, 'w') as f:
            json.dump(prompt, f, indent=2)
        prompt_files.append(prompt_file)

    return prompt_files


@pytest.fixture
def sample_input_content():
    """Sample input text content for testing."""
    return """# Sample Content for Testing

This is some test content that we will use to demonstrate functionality.
The content has intentional issues that our prompts should identify.

## Issues in This Content

- Some grammar mistakes are present
- The flow could be improved
- Structure needs work

This sentence have a grammar error. The content quality varies throughout
this document, and their are several areas where improvement is needed.
"""


@pytest.fixture
def sample_input_file(temp_dir, sample_input_content):
    """Create a temporary input file."""
    input_file = temp_dir / "test_input.md"
    with open(input_file, 'w') as f:
        f.write(sample_input_content)
    return input_file


@pytest.fixture
def mock_api_response():
    """Mock API response data."""
    return {
        "choices": [{
            "message": {
                "content": "Here's the improved version:\n\n# Enhanced Sample Content\n\nThis is improved test content that demonstrates better structure and clarity."
            }
        }]
    }


@pytest.fixture
def mock_api_error_response():
    """Mock API error response."""
    return {
        "error": {
            "message": "Invalid API key",
            "type": "authentication_error",
            "code": "invalid_api_key"
        }
    }


@pytest.fixture
def mock_env_api_key():
    """Mock environment variable for API key."""
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-api-key-123'}):
        yield 'test-api-key-123'


@pytest.fixture
def mock_requests_post(mock_api_response):
    """Mock requests.post for API calls."""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def invalid_json_file(temp_dir):
    """Create a file with invalid JSON for error testing."""
    invalid_file = temp_dir / "invalid.json"
    with open(invalid_file, 'w') as f:
        f.write('{"invalid": json, content}')
    return invalid_file


@pytest.fixture
def empty_prompt_file(temp_dir):
    """Create an empty JSON file for error testing."""
    empty_file = temp_dir / "empty.json"
    with open(empty_file, 'w') as f:
        f.write('{}')
    return empty_file


@pytest.fixture
def chain_config():
    """Sample chain configuration for testing."""
    return {
        'input_file': 'test_input.md',
        'output_file': 'test_output.md',
        'prompts': {
            'prompt 1': 'step1_analysis.json',
            'prompt 2': {
                'name': 'grammar_check',
                'prompt_file': 'step2_grammar.json'
            },
            'prompt 3': {
                'prompt_file': 'step1_analysis.json,step2_grammar.json'
            }
        }
    }


@pytest.fixture
def chain_config_file(temp_dir, chain_config):
    """Create a temporary chain configuration file."""
    config_file = temp_dir / "test_chain.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(chain_config, f)
    return config_file


class MockLogger:
    """Mock logger for testing logging functionality."""

    def __init__(self):
        self.messages = []

    def info(self, msg):
        self.messages.append(('info', msg))

    def debug(self, msg):
        self.messages.append(('debug', msg))

    def warning(self, msg):
        self.messages.append(('warning', msg))

    def error(self, msg):
        self.messages.append(('error', msg))

    def get_messages(self, level=None):
        if level:
            return [msg for lvl, msg in self.messages if lvl == level]
        return [msg for lvl, msg in self.messages]


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    return MockLogger()


# Test markers for categorizing tests
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "web: web interface tests")
    config.addinivalue_line("markers", "slow: slow-running tests")


# Helper functions for tests
def create_test_file(path: Path, content: str) -> Path:
    """Helper to create test files with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    return path


def assert_file_exists(path: Path) -> None:
    """Helper to assert a file exists."""
    assert path.exists(), f"File {path} does not exist"


def assert_file_content(path: Path, expected_content: str) -> None:
    """Helper to assert file content matches expected."""
    assert_file_exists(path)
    with open(path, 'r') as f:
        content = f.read()
    assert content == expected_content, f"File content mismatch in {path}"


def assert_valid_json(path: Path) -> Dict[Any, Any]:
    """Helper to assert file contains valid JSON and return parsed content."""
    assert_file_exists(path)
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON in {path}: {e}")


def assert_valid_yaml(path: Path) -> Dict[Any, Any]:
    """Helper to assert file contains valid YAML and return parsed content."""
    assert_file_exists(path)
    with open(path, 'r') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in {path}: {e}")