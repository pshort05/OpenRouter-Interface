"""
Unit tests for ConfigManager with new API parameters.

Tests the 13 new API parameters added for enhanced OpenRouter API control.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from src.openrouter_interface.config_manager import ConfigManager


class TestConfigManagerNewAPIParameters:
    """Test suite for new API parameters in ConfigManager."""

    def test_default_config_excludes_optional_parameters(self):
        """Test that optional API parameters are not included in default config."""
        config_manager = ConfigManager()

        # Core parameters should be present
        assert 'model' in config_manager.config
        assert 'temperature' in config_manager.config
        assert 'max_tokens' in config_manager.config

        # Optional parameters should not be present in defaults
        optional_params = [
            'top_p', 'top_k', 'min_p', 'seed',
            'frequency_penalty', 'presence_penalty', 'repetition_penalty',
            'stream', 'response_format', 'top_logprobs',
            'models', 'provider', 'transforms', 'usage', 'user'
        ]

        for param in optional_params:
            assert param not in config_manager.config or config_manager.config.get(param) is None

    def test_sampling_control_parameters(self, temp_dir):
        """Test advanced sampling control parameters."""
        config_file = temp_dir / "sampling_config.yaml"

        sampling_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'top_p': 0.9,
            'top_k': 50,
            'min_p': 0.02,
            'seed': 12345
        }

        with open(config_file, 'w') as f:
            yaml.dump(sampling_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('top_p') == 0.9
        assert config_manager.get('top_k') == 50
        assert config_manager.get('min_p') == 0.02
        assert config_manager.get('seed') == 12345

    def test_penalty_parameters(self, temp_dir):
        """Test penalty parameters for repetition control."""
        config_file = temp_dir / "penalty_config.yaml"

        penalty_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'frequency_penalty': 0.1,
            'presence_penalty': 0.2,
            'repetition_penalty': 1.1
        }

        with open(config_file, 'w') as f:
            yaml.dump(penalty_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('frequency_penalty') == 0.1
        assert config_manager.get('presence_penalty') == 0.2
        assert config_manager.get('repetition_penalty') == 1.1

    def test_response_control_parameters(self, temp_dir):
        """Test response control parameters."""
        config_file = temp_dir / "response_config.yaml"

        response_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'stream': True,
            'response_format': {'type': 'json_object'},
            'top_logprobs': 5
        }

        with open(config_file, 'w') as f:
            yaml.dump(response_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('stream') is True
        assert config_manager.get('response_format') == {'type': 'json_object'}
        assert config_manager.get('top_logprobs') == 5

    def test_openrouter_specific_parameters(self, temp_dir):
        """Test OpenRouter-specific features."""
        config_file = temp_dir / "openrouter_config.yaml"

        openrouter_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'models': ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo'],
            'provider': {'order': ['Anthropic', 'OpenAI']},
            'transforms': ['middle-out'],
            'usage': {'include': True}
        }

        with open(config_file, 'w') as f:
            yaml.dump(openrouter_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('models') == ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo']
        assert config_manager.get('provider') == {'order': ['Anthropic', 'OpenAI']}
        assert config_manager.get('transforms') == ['middle-out']
        assert config_manager.get('usage') == {'include': True}

    def test_utility_parameters(self, temp_dir):
        """Test utility parameters."""
        config_file = temp_dir / "utility_config.yaml"

        utility_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'user': 'test_user_123'
        }

        with open(config_file, 'w') as f:
            yaml.dump(utility_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('user') == 'test_user_123'

    def test_comprehensive_api_parameters(self, temp_dir):
        """Test all new API parameters together."""
        config_file = temp_dir / "comprehensive_config.yaml"

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
            'provider': {'order': ['Anthropic', 'OpenAI'], 'allow_fallbacks': True},
            'transforms': ['middle-out'],
            'usage': {'include': True},

            # Utility
            'user': 'comprehensive_test'
        }

        with open(config_file, 'w') as f:
            yaml.dump(comprehensive_config, f)

        config_manager = ConfigManager(str(config_file))

        # Verify all parameters are loaded correctly
        assert config_manager.get('top_p') == 0.9
        assert config_manager.get('top_k') == 40
        assert config_manager.get('min_p') == 0.01
        assert config_manager.get('seed') == 42

        assert config_manager.get('frequency_penalty') == 0.1
        assert config_manager.get('presence_penalty') == 0.15
        assert config_manager.get('repetition_penalty') == 1.05

        assert config_manager.get('stream') is False
        assert config_manager.get('response_format') == {'type': 'json_object'}
        assert config_manager.get('top_logprobs') == 3

        assert config_manager.get('models') == ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo']
        assert config_manager.get('provider') == {'order': ['Anthropic', 'OpenAI'], 'allow_fallbacks': True}
        assert config_manager.get('transforms') == ['middle-out']
        assert config_manager.get('usage') == {'include': True}

        assert config_manager.get('user') == 'comprehensive_test'

    def test_parameter_type_validation(self, temp_dir):
        """Test that parameters accept various data types correctly."""
        config_file = temp_dir / "types_config.yaml"

        types_config = {
            'model': 'test-model',
            'top_p': 0.9,          # float
            'top_k': 50,           # int
            'seed': 12345,         # int
            'stream': True,        # bool
            'models': ['model1', 'model2'],  # list
            'provider': {'key': 'value'},    # dict
            'user': 'string_value'           # string
        }

        with open(config_file, 'w') as f:
            yaml.dump(types_config, f)

        config_manager = ConfigManager(str(config_file))

        # Verify types are preserved
        assert isinstance(config_manager.get('top_p'), float)
        assert isinstance(config_manager.get('top_k'), int)
        assert isinstance(config_manager.get('seed'), int)
        assert isinstance(config_manager.get('stream'), bool)
        assert isinstance(config_manager.get('models'), list)
        assert isinstance(config_manager.get('provider'), dict)
        assert isinstance(config_manager.get('user'), str)

    def test_partial_parameter_override(self, temp_dir):
        """Test that only specified parameters override defaults."""
        config_file = temp_dir / "partial_params.yaml"

        partial_config = {
            'model': 'custom-model',
            'top_p': 0.8,
            'frequency_penalty': 0.2,
            'user': 'partial_test'
        }

        with open(config_file, 'w') as f:
            yaml.dump(partial_config, f)

        config_manager = ConfigManager(str(config_file))

        # Specified parameters should be set
        assert config_manager.get('top_p') == 0.8
        assert config_manager.get('frequency_penalty') == 0.2
        assert config_manager.get('user') == 'partial_test'

        # Unspecified optional parameters should be None
        assert config_manager.get('top_k') is None
        assert config_manager.get('seed') is None
        assert config_manager.get('stream') is None

        # Core parameters should have defaults
        assert config_manager.get('temperature') == 0.8  # default
        assert config_manager.get('max_tokens') == 25000  # default

    def test_parameter_boundary_values(self, temp_dir):
        """Test parameter boundary values according to OpenRouter specs."""
        config_file = temp_dir / "boundary_config.yaml"

        boundary_config = {
            'model': 'test-model',
            'temperature': 2.0,        # max value [0, 2]
            'top_p': 0.001,           # near min value (0, 1]
            'frequency_penalty': -2.0, # min value [-2, 2]
            'presence_penalty': 2.0,   # max value [-2, 2]
            'repetition_penalty': 0.1, # near min value (0, 2]
            'top_logprobs': 1,        # min reasonable value
            'seed': 0                 # min value
        }

        with open(config_file, 'w') as f:
            yaml.dump(boundary_config, f)

        config_manager = ConfigManager(str(config_file))

        # All boundary values should be preserved as-is
        assert config_manager.get('temperature') == 2.0
        assert config_manager.get('top_p') == 0.001
        assert config_manager.get('frequency_penalty') == -2.0
        assert config_manager.get('presence_penalty') == 2.0
        assert config_manager.get('repetition_penalty') == 0.1
        assert config_manager.get('top_logprobs') == 1
        assert config_manager.get('seed') == 0

    def test_null_and_none_parameters(self, temp_dir):
        """Test handling of null/None parameter values."""
        config_file = temp_dir / "null_config.yaml"

        null_config = {
            'model': 'test-model',
            'top_p': None,
            'seed': None,
            'stream': None,
            'user': None
        }

        with open(config_file, 'w') as f:
            yaml.dump(null_config, f)

        config_manager = ConfigManager(str(config_file))

        # None values should be preserved (indicating parameter not set)
        assert config_manager.get('top_p') is None
        assert config_manager.get('seed') is None
        assert config_manager.get('stream') is None
        assert config_manager.get('user') is None


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)