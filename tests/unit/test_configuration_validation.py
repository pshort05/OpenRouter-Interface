"""
Test cases for configuration validation with new API parameters.

Tests parameter validation, type checking, and boundary conditions.
"""

import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.openrouter_interface.config_manager import ConfigManager


class TestConfigurationValidation:
    """Test suite for configuration validation with new parameters."""

    def test_valid_sampling_parameter_ranges(self, temp_dir):
        """Test validation of sampling parameters within valid ranges."""
        config_file = temp_dir / "valid_sampling.yaml"

        valid_sampling_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 1.0,        # Valid range [0, 2]
            'top_p': 0.5,             # Valid range (0, 1]
            'top_k': 50,              # Valid range [1, ∞)
            'min_p': 0.05,            # Valid range [0, 1]
        }

        with open(config_file, 'w') as f:
            yaml.dump(valid_sampling_config, f)

        config_manager = ConfigManager(str(config_file))

        # All parameters should be loaded correctly
        assert config_manager.get('temperature') == 1.0
        assert config_manager.get('top_p') == 0.5
        assert config_manager.get('top_k') == 50
        assert config_manager.get('min_p') == 0.05

    def test_valid_penalty_parameter_ranges(self, temp_dir):
        """Test validation of penalty parameters within valid ranges."""
        config_file = temp_dir / "valid_penalty.yaml"

        valid_penalty_config = {
            'model': 'test-model',
            'frequency_penalty': 0.0,     # Valid range [-2, 2]
            'presence_penalty': -1.5,     # Valid range [-2, 2]
            'repetition_penalty': 1.2,    # Valid range (0, 2]
        }

        with open(config_file, 'w') as f:
            yaml.dump(valid_penalty_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('frequency_penalty') == 0.0
        assert config_manager.get('presence_penalty') == -1.5
        assert config_manager.get('repetition_penalty') == 1.2

    def test_boundary_value_parameters(self, temp_dir):
        """Test parameters at boundary values."""
        config_file = temp_dir / "boundary_values.yaml"

        boundary_config = {
            'model': 'test-model',
            'temperature': 0.0,           # Minimum boundary
            'top_p': 0.001,              # Near minimum boundary (0, 1]
            'frequency_penalty': -2.0,    # Minimum boundary [-2, 2]
            'presence_penalty': 2.0,      # Maximum boundary [-2, 2]
            'repetition_penalty': 0.001,  # Near minimum boundary (0, 2]
            'top_k': 1,                  # Minimum boundary [1, ∞)
            'min_p': 0.0,                # Minimum boundary [0, 1]
            'seed': 0,                   # Minimum reasonable value
            'top_logprobs': 1,           # Minimum reasonable value
        }

        with open(config_file, 'w') as f:
            yaml.dump(boundary_config, f)

        config_manager = ConfigManager(str(config_file))

        # All boundary values should be preserved
        assert config_manager.get('temperature') == 0.0
        assert config_manager.get('top_p') == 0.001
        assert config_manager.get('frequency_penalty') == -2.0
        assert config_manager.get('presence_penalty') == 2.0
        assert config_manager.get('repetition_penalty') == 0.001
        assert config_manager.get('top_k') == 1
        assert config_manager.get('min_p') == 0.0
        assert config_manager.get('seed') == 0
        assert config_manager.get('top_logprobs') == 1

    def test_maximum_boundary_values(self, temp_dir):
        """Test parameters at maximum boundary values."""
        config_file = temp_dir / "max_boundary.yaml"

        max_boundary_config = {
            'model': 'test-model',
            'temperature': 2.0,           # Maximum boundary [0, 2]
            'top_p': 1.0,                # Maximum boundary (0, 1] - edge case
            'repetition_penalty': 2.0,    # Maximum boundary (0, 2] - edge case
            'top_k': 1000000,            # Large value within [1, ∞)
            'min_p': 1.0,                # Maximum boundary [0, 1]
            'seed': 2147483647,          # Large seed value
            'top_logprobs': 20,          # Reasonable maximum
        }

        with open(config_file, 'w') as f:
            yaml.dump(max_boundary_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('temperature') == 2.0
        assert config_manager.get('top_p') == 1.0
        assert config_manager.get('repetition_penalty') == 2.0
        assert config_manager.get('top_k') == 1000000
        assert config_manager.get('min_p') == 1.0
        assert config_manager.get('seed') == 2147483647
        assert config_manager.get('top_logprobs') == 20

    def test_boolean_parameter_validation(self, temp_dir):
        """Test boolean parameter validation."""
        config_file = temp_dir / "boolean_params.yaml"

        boolean_config = {
            'model': 'test-model',
            'stream': True,
            'enable_feature': False,
        }

        with open(config_file, 'w') as f:
            yaml.dump(boolean_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('stream') is True
        assert config_manager.get('enable_feature') is False

        # Test type preservation
        assert isinstance(config_manager.get('stream'), bool)
        assert isinstance(config_manager.get('enable_feature'), bool)

    def test_complex_object_parameter_validation(self, temp_dir):
        """Test validation of complex object parameters."""
        config_file = temp_dir / "complex_objects.yaml"

        complex_config = {
            'model': 'test-model',
            'response_format': {
                'type': 'json_object',
                'schema': {
                    'properties': {
                        'answer': {'type': 'string'},
                        'confidence': {'type': 'number'}
                    }
                }
            },
            'provider': {
                'order': ['Anthropic', 'OpenAI'],
                'allow_fallbacks': True,
                'timeout': 30
            },
            'models': [
                'anthropic/claude-4-sonnet-20250522',
                'openai/gpt-4-turbo',
                'meta-llama/llama-3.1-405b-instruct'
            ],
            'usage': {
                'include': True,
                'detailed': False,
                'track_tokens': True
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(complex_config, f)

        config_manager = ConfigManager(str(config_file))

        # Verify complex objects are preserved correctly
        response_format = config_manager.get('response_format')
        assert response_format['type'] == 'json_object'
        assert 'schema' in response_format
        assert response_format['schema']['properties']['answer']['type'] == 'string'

        provider = config_manager.get('provider')
        assert provider['order'] == ['Anthropic', 'OpenAI']
        assert provider['allow_fallbacks'] is True
        assert provider['timeout'] == 30

        models = config_manager.get('models')
        assert len(models) == 3
        assert 'anthropic/claude-4-sonnet-20250522' in models

        usage = config_manager.get('usage')
        assert usage['include'] is True
        assert usage['detailed'] is False
        assert usage['track_tokens'] is True

    def test_array_parameter_validation(self, temp_dir):
        """Test validation of array parameters."""
        config_file = temp_dir / "array_params.yaml"

        array_config = {
            'model': 'test-model',
            'models': ['model1', 'model2', 'model3'],
            'transforms': ['transform1', 'transform2'],
            'empty_array': [],
            'mixed_array': ['string', 123, True, {'key': 'value'}]
        }

        with open(config_file, 'w') as f:
            yaml.dump(array_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('models') == ['model1', 'model2', 'model3']
        assert config_manager.get('transforms') == ['transform1', 'transform2']
        assert config_manager.get('empty_array') == []
        assert config_manager.get('mixed_array') == ['string', 123, True, {'key': 'value'}]

        # Verify types are preserved
        assert isinstance(config_manager.get('models'), list)
        assert isinstance(config_manager.get('empty_array'), list)

    def test_string_parameter_validation(self, temp_dir):
        """Test string parameter validation."""
        config_file = temp_dir / "string_params.yaml"

        string_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'user': 'test_user_123',
            'custom_string': 'custom_value',
            'empty_string': '',
            'unicode_string': 'Hello 世界 🌍',
            'numeric_string': '12345',
        }

        with open(config_file, 'w') as f:
            yaml.dump(string_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('user') == 'test_user_123'
        assert config_manager.get('custom_string') == 'custom_value'
        assert config_manager.get('empty_string') == ''
        assert config_manager.get('unicode_string') == 'Hello 世界 🌍'
        assert config_manager.get('numeric_string') == '12345'

        # Verify all are strings
        assert isinstance(config_manager.get('user'), str)
        assert isinstance(config_manager.get('numeric_string'), str)

    def test_null_and_none_parameter_handling(self, temp_dir):
        """Test handling of null/None parameters."""
        config_file = temp_dir / "null_params.yaml"

        null_config = {
            'model': 'test-model',
            'explicit_null': None,
            'yaml_null': None,  # Fixed: use None instead of undefined 'null'
            'temperature': 0.7,
            'top_p': None,
        }

        with open(config_file, 'w') as f:
            yaml.dump(null_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('explicit_null') is None
        assert config_manager.get('yaml_null') is None
        assert config_manager.get('top_p') is None
        assert config_manager.get('temperature') == 0.7

        # Verify non-existent keys also return None
        assert config_manager.get('nonexistent_key') is None

    def test_numeric_precision_preservation(self, temp_dir):
        """Test that numeric precision is preserved in configuration."""
        config_file = temp_dir / "precision_params.yaml"

        precision_config = {
            'model': 'test-model',
            'temperature': 0.123456789,
            'top_p': 0.987654321,
            'frequency_penalty': -1.234567890123456,
            'presence_penalty': 1.999999999,
            'very_small': 0.000000001,
            'scientific_notation': 1.23e-5,
            'large_number': 999999999.999999
        }

        with open(config_file, 'w') as f:
            yaml.dump(precision_config, f)

        config_manager = ConfigManager(str(config_file))

        # Test precision preservation (within reasonable limits)
        assert abs(config_manager.get('temperature') - 0.123456789) < 1e-10
        assert abs(config_manager.get('top_p') - 0.987654321) < 1e-10
        assert abs(config_manager.get('frequency_penalty') - (-1.234567890123456)) < 1e-12
        assert abs(config_manager.get('very_small') - 0.000000001) < 1e-15
        assert abs(config_manager.get('scientific_notation') - 1.23e-5) < 1e-15

    def test_integer_parameter_validation(self, temp_dir):
        """Test integer parameter validation and type preservation."""
        config_file = temp_dir / "integer_params.yaml"

        integer_config = {
            'model': 'test-model',
            'top_k': 50,
            'seed': 12345,
            'top_logprobs': 5,
            'max_tokens': 25000,
            'zero_value': 0,
            'negative_value': -100,
            'large_value': 2147483647
        }

        with open(config_file, 'w') as f:
            yaml.dump(integer_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('top_k') == 50
        assert config_manager.get('seed') == 12345
        assert config_manager.get('top_logprobs') == 5
        assert config_manager.get('max_tokens') == 25000
        assert config_manager.get('zero_value') == 0
        assert config_manager.get('negative_value') == -100
        assert config_manager.get('large_value') == 2147483647

        # Verify types are preserved as integers
        assert isinstance(config_manager.get('top_k'), int)
        assert isinstance(config_manager.get('seed'), int)
        assert isinstance(config_manager.get('zero_value'), int)
        assert isinstance(config_manager.get('negative_value'), int)

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)


class TestConfigurationEdgeCases:
    """Test edge cases and unusual configurations."""

    def test_deeply_nested_configuration(self, temp_dir):
        """Test deeply nested configuration objects."""
        config_file = temp_dir / "deep_nested.yaml"

        nested_config = {
            'model': 'test-model',
            'provider': {
                'routing': {
                    'strategy': 'round_robin',
                    'providers': {
                        'primary': {
                            'name': 'Anthropic',
                            'endpoints': ['api1.anthropic.com', 'api2.anthropic.com'],
                            'config': {
                                'timeout': 30,
                                'retries': 3,
                                'fallback': {
                                    'enabled': True,
                                    'delay': 1.5
                                }
                            }
                        },
                        'secondary': {
                            'name': 'OpenAI',
                            'endpoints': ['api.openai.com']
                        }
                    }
                }
            }
        }

        with open(config_file, 'w') as f:
            yaml.dump(nested_config, f)

        config_manager = ConfigManager(str(config_file))

        # Verify deep nesting is preserved
        provider = config_manager.get('provider')
        assert provider['routing']['strategy'] == 'round_robin'
        assert provider['routing']['providers']['primary']['name'] == 'Anthropic'
        assert provider['routing']['providers']['primary']['config']['timeout'] == 30
        assert provider['routing']['providers']['primary']['config']['fallback']['enabled'] is True
        assert provider['routing']['providers']['primary']['config']['fallback']['delay'] == 1.5

    def test_mixed_data_types_in_arrays(self, temp_dir):
        """Test arrays with mixed data types."""
        config_file = temp_dir / "mixed_arrays.yaml"

        mixed_config = {
            'model': 'test-model',
            'mixed_array': [
                'string_value',
                123,
                45.67,
                True,
                None,
                {'nested': 'object'},
                ['nested', 'array']
            ]
        }

        with open(config_file, 'w') as f:
            yaml.dump(mixed_config, f)

        config_manager = ConfigManager(str(config_file))

        mixed_array = config_manager.get('mixed_array')
        assert mixed_array[0] == 'string_value'
        assert mixed_array[1] == 123
        assert mixed_array[2] == 45.67
        assert mixed_array[3] is True
        assert mixed_array[4] is None
        assert mixed_array[5] == {'nested': 'object'}
        assert mixed_array[6] == ['nested', 'array']

    def test_unicode_and_special_characters(self, temp_dir):
        """Test configuration with Unicode and special characters."""
        config_file = temp_dir / "unicode_config.yaml"

        unicode_config = {
            'model': 'test-model',
            'user': 'user_测试_🤖',
            'special_chars': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'quotes': '"double" and \'single\' quotes',
            'unicode_model': 'モデル/test-模型',
            'emojis': '🎯🚀💡🔥⚡'
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(unicode_config, f, allow_unicode=True)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('user') == 'user_测试_🤖'
        assert config_manager.get('special_chars') == '!@#$%^&*()_+-=[]{}|;:,.<>?'
        assert config_manager.get('quotes') == '"double" and \'single\' quotes'
        assert config_manager.get('unicode_model') == 'モデル/test-模型'
        assert config_manager.get('emojis') == '🎯🚀💡🔥⚡'

    def test_very_large_parameter_values(self, temp_dir):
        """Test very large parameter values."""
        config_file = temp_dir / "large_values.yaml"

        large_config = {
            'model': 'test-model',
            'max_tokens': 1000000,
            'top_k': 999999,
            'seed': 9223372036854775807,  # Near max int64
            'large_float': 1.7976931348623157e+308,  # Near max float64
            'very_long_string': 'x' * 10000,
            'large_array': list(range(1000))
        }

        with open(config_file, 'w') as f:
            yaml.dump(large_config, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.get('max_tokens') == 1000000
        assert config_manager.get('top_k') == 999999
        assert config_manager.get('seed') == 9223372036854775807
        assert len(config_manager.get('very_long_string')) == 10000
        assert len(config_manager.get('large_array')) == 1000
        assert config_manager.get('large_array')[999] == 999

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)