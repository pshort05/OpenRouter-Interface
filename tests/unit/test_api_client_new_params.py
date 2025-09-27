"""
Unit tests for API client with new parameter handling.

Tests the enhanced API payload building and parameter inclusion logic.
"""

from unittest.mock import Mock, patch
import pytest

from src.openrouter_interface.api_client import APIClient
from src.openrouter_interface.prompt_runner_api_client import PromptAPIClient
from src.openrouter_interface.config_manager import ConfigManager


class TestAPIClientNewParameters:
    """Test suite for enhanced API client parameter handling."""

    def test_build_api_payload_core_parameters_only(self):
        """Test API payload with only core parameters."""
        # Mock config with only core parameters
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        expected_payload = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'messages': [{'role': 'user', 'content': 'Test prompt'}],
            'temperature': 0.8,
            'max_tokens': 25000
        }

        assert payload == expected_payload

    def test_build_api_payload_with_sampling_controls(self):
        """Test API payload with sampling control parameters."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'top_p': 0.9,
            'top_k': 50,
            'min_p': 0.02,
            'seed': 12345
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        assert payload['top_p'] == 0.9
        assert payload['top_k'] == 50
        assert payload['min_p'] == 0.02
        assert payload['seed'] == 12345

    def test_build_api_payload_with_penalties(self):
        """Test API payload with penalty parameters."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'frequency_penalty': 0.1,
            'presence_penalty': 0.2,
            'repetition_penalty': 1.1
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        assert payload['frequency_penalty'] == 0.1
        assert payload['presence_penalty'] == 0.2
        assert payload['repetition_penalty'] == 1.1

    def test_build_api_payload_with_response_controls(self):
        """Test API payload with response control parameters."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'stream': True,
            'response_format': {'type': 'json_object'},
            'top_logprobs': 5
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        assert payload['stream'] is True
        assert payload['response_format'] == {'type': 'json_object'}
        assert payload['top_logprobs'] == 5

    def test_build_api_payload_with_openrouter_features(self):
        """Test API payload with OpenRouter-specific features."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'models': ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo'],
            'provider': {'order': ['Anthropic', 'OpenAI']},
            'transforms': ['middle-out'],
            'usage': {'include': True}
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        assert payload['models'] == ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo']
        assert payload['provider'] == {'order': ['Anthropic', 'OpenAI']}
        assert payload['transforms'] == ['middle-out']
        assert payload['usage'] == {'include': True}

    def test_build_api_payload_with_utility_parameters(self):
        """Test API payload with utility parameters."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'user': 'test_user_123'
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        assert payload['user'] == 'test_user_123'

    def test_build_api_payload_excludes_none_values(self):
        """Test that None parameter values are excluded from payload."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'top_p': 0.9,     # Include this
            'top_k': None,    # Exclude this
            'seed': None,     # Exclude this
            'stream': False,  # Include this (explicit False)
            'user': None      # Exclude this
        }.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        # Should include explicitly set values
        assert payload['top_p'] == 0.9
        assert payload['stream'] is False

        # Should exclude None values
        assert 'top_k' not in payload
        assert 'seed' not in payload
        assert 'user' not in payload

    def test_build_api_payload_comprehensive(self):
        """Test API payload with all possible parameters."""
        mock_config = Mock(spec=ConfigManager)
        comprehensive_config = {
            # Core parameters
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.7,
            'max_tokens': 20000,

            # Sampling controls
            'top_p': 0.9,
            'top_k': 40,
            'min_p': 0.01,
            'seed': 42,

            # Penalties
            'frequency_penalty': 0.1,
            'presence_penalty': 0.15,
            'repetition_penalty': 1.05,

            # Response control
            'stream': False,
            'response_format': {'type': 'json_object'},
            'top_logprobs': 3,

            # OpenRouter features
            'models': ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo'],
            'provider': {'order': ['Anthropic', 'OpenAI']},
            'transforms': ['middle-out'],
            'usage': {'include': True},

            # Utility
            'user': 'comprehensive_test'
        }

        mock_config.get.side_effect = lambda key, default=None: comprehensive_config.get(key, default)

        client = APIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        # Verify all parameters are included
        expected_keys = {
            'model', 'messages', 'temperature', 'max_tokens',
            'top_p', 'top_k', 'min_p', 'seed',
            'frequency_penalty', 'presence_penalty', 'repetition_penalty',
            'stream', 'response_format', 'top_logprobs',
            'models', 'provider', 'transforms', 'usage', 'user'
        }

        assert set(payload.keys()) == expected_keys

        # Spot check some values
        assert payload['top_p'] == 0.9
        assert payload['seed'] == 42
        assert payload['usage'] == {'include': True}

    def test_log_api_parameters_core_only(self, caplog):
        """Test parameter logging with core parameters only."""
        mock_config = Mock(spec=ConfigManager)
        client = APIClient(mock_config)

        payload = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'messages': [{'role': 'user', 'content': 'test'}],
            'temperature': 0.8,
            'max_tokens': 25000
        }

        with caplog.at_level('INFO'):
            client._log_api_parameters(payload)

        # Check that core parameters are logged
        assert "Model: anthropic/claude-4-sonnet-20250522" in caplog.text
        assert "Temperature: 0.8" in caplog.text
        assert "Max tokens: 25000" in caplog.text

        # Should not log additional parameters
        assert "Additional parameters:" not in caplog.text

    def test_log_api_parameters_with_optionals(self, caplog):
        """Test parameter logging with optional parameters."""
        mock_config = Mock(spec=ConfigManager)
        client = APIClient(mock_config)

        payload = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'messages': [{'role': 'user', 'content': 'test'}],
            'temperature': 0.8,
            'max_tokens': 25000,
            'top_p': 0.9,
            'seed': 42,
            'frequency_penalty': 0.1,
            'user': 'test_user'
        }

        with caplog.at_level('INFO'):
            client._log_api_parameters(payload)

        # Check that additional parameters are logged
        assert "Additional parameters:" in caplog.text
        assert "top_p=0.9" in caplog.text
        assert "seed=42" in caplog.text
        assert "frequency_penalty=0.1" in caplog.text
        assert "user=test_user" in caplog.text


class TestPromptAPIClientNewParameters:
    """Test suite for PromptAPIClient parameter handling."""

    def test_prompt_api_client_same_behavior(self):
        """Test that PromptAPIClient has same parameter handling as APIClient."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8,
            'max_tokens': 25000,
            'top_p': 0.9,
            'seed': 42,
            'frequency_penalty': 0.1
        }.get(key, default)

        client = PromptAPIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        # Should have same structure as APIClient
        assert payload['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert payload['top_p'] == 0.9
        assert payload['seed'] == 42
        assert payload['frequency_penalty'] == 0.1

    def test_prompt_api_client_logging(self, caplog):
        """Test that PromptAPIClient logs parameters correctly."""
        mock_config = Mock(spec=ConfigManager)
        mock_config.get.side_effect = lambda key, default=None: {
            'model': 'test-model',
            'temperature': 0.5,
            'max_tokens': 15000,
            'top_k': 30
        }.get(key, default)

        client = PromptAPIClient(mock_config)
        payload = client._build_api_payload("Test prompt")

        with caplog.at_level('INFO'):
            client._log_api_parameters(payload)

        assert "Model: test-model" in caplog.text
        assert "Temperature: 0.5" in caplog.text
        assert "Max tokens: 15000" in caplog.text
        assert "top_k=30" in caplog.text


@pytest.mark.parametrize("param_name,param_value", [
    ('top_p', 0.9),
    ('top_k', 50),
    ('min_p', 0.02),
    ('seed', 12345),
    ('frequency_penalty', 0.1),
    ('presence_penalty', 0.2),
    ('repetition_penalty', 1.1),
    ('stream', True),
    ('response_format', {'type': 'json_object'}),
    ('top_logprobs', 5),
    ('models', ['model1', 'model2']),
    ('provider', {'order': ['Provider1']}),
    ('transforms', ['transform1']),
    ('usage', {'include': True}),
    ('user', 'test_user')
])
def test_individual_parameter_inclusion(param_name, param_value):
    """Test that each new parameter is correctly included when set."""
    mock_config = Mock(spec=ConfigManager)
    config_dict = {
        'model': 'test-model',
        'temperature': 0.8,
        'max_tokens': 25000,
        param_name: param_value
    }
    mock_config.get.side_effect = lambda key, default=None: config_dict.get(key, default)

    client = APIClient(mock_config)
    payload = client._build_api_payload("Test prompt")

    assert payload[param_name] == param_value


@pytest.mark.parametrize("param_name", [
    'top_p', 'top_k', 'min_p', 'seed', 'frequency_penalty',
    'presence_penalty', 'repetition_penalty', 'stream',
    'response_format', 'top_logprobs', 'models', 'provider',
    'transforms', 'usage', 'user'
])
def test_individual_parameter_exclusion_when_none(param_name):
    """Test that each new parameter is excluded when None."""
    mock_config = Mock(spec=ConfigManager)
    config_dict = {
        'model': 'test-model',
        'temperature': 0.8,
        'max_tokens': 25000,
        param_name: None
    }
    mock_config.get.side_effect = lambda key, default=None: config_dict.get(key, default)

    client = APIClient(mock_config)
    payload = client._build_api_payload("Test prompt")

    assert param_name not in payload