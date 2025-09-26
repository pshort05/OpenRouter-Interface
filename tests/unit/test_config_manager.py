"""
Unit tests for ConfigManager class.

Tests configuration loading, validation, API key handling, and error scenarios.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest
import yaml

from src.openrouter_interface.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_init_with_default_config(self):
        """Test ConfigManager initialization with default configuration."""
        config_manager = ConfigManager()

        # Should use default config file name
        assert config_manager.config_file == "openrouter_editor.yaml"

        # Should have default configuration values
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.config['max_tokens'] == 25000
        assert config_manager.config['temperature'] == 0.8
        assert config_manager.config['log_level'] == 'INFO'

    def test_init_with_custom_config_file(self, sample_config_file):
        """Test ConfigManager initialization with custom config file."""
        config_manager = ConfigManager(str(sample_config_file))

        assert config_manager.config_file == str(sample_config_file)
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.config['max_tokens'] == 25000

    def test_load_config_with_existing_file(self, temp_dir, sample_config):
        """Test loading configuration from existing YAML file."""
        config_file = temp_dir / "test_config.yaml"

        # Create config file with custom values
        custom_config = sample_config.copy()
        custom_config['temperature'] = 0.5
        custom_config['max_tokens'] = 15000

        with open(config_file, 'w') as f:
            yaml.dump(custom_config, f)

        config_manager = ConfigManager(str(config_file))

        # Should load custom values
        assert config_manager.config['temperature'] == 0.5
        assert config_manager.config['max_tokens'] == 15000
        # Should preserve defaults for unspecified values
        assert config_manager.config['log_level'] == 'INFO'

    def test_load_config_with_nonexistent_file(self):
        """Test loading configuration when file doesn't exist."""
        config_manager = ConfigManager("nonexistent_config.yaml")

        # Should use default values
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.config['max_tokens'] == 25000
        assert config_manager.config['temperature'] == 0.8

    def test_load_config_with_empty_file(self, temp_dir):
        """Test loading configuration from empty YAML file."""
        config_file = temp_dir / "empty_config.yaml"
        config_file.touch()  # Create empty file

        config_manager = ConfigManager(str(config_file))

        # Should use default values when file is empty
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.config['max_tokens'] == 25000

    def test_load_config_with_invalid_yaml(self, temp_dir):
        """Test loading configuration with invalid YAML content."""
        config_file = temp_dir / "invalid_config.yaml"

        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")

        # Should raise yaml.YAMLError
        with pytest.raises(yaml.YAMLError):
            ConfigManager(str(config_file))

    def test_load_config_partial_override(self, temp_dir):
        """Test that user config partially overrides defaults."""
        config_file = temp_dir / "partial_config.yaml"

        partial_config = {
            'temperature': 0.3,
            'log_level': 'DEBUG'
        }

        with open(config_file, 'w') as f:
            yaml.dump(partial_config, f)

        config_manager = ConfigManager(str(config_file))

        # Should override specified values
        assert config_manager.config['temperature'] == 0.3
        assert config_manager.config['log_level'] == 'DEBUG'

        # Should keep defaults for unspecified values
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.config['max_tokens'] == 25000

    def test_get_method(self, sample_config_file):
        """Test the get method for retrieving configuration values."""
        config_manager = ConfigManager(str(sample_config_file))

        # Test getting existing values
        assert config_manager.get('model') == 'anthropic/claude-4-sonnet-20250522'
        assert config_manager.get('temperature') == 0.8

        # Test getting non-existent value with default
        assert config_manager.get('nonexistent_key', 'default_value') == 'default_value'

        # Test getting non-existent value without default
        assert config_manager.get('nonexistent_key') is None

    def test_get_api_key_from_environment(self, mock_env_api_key):
        """Test getting API key from environment variable."""
        config_manager = ConfigManager()

        api_key = config_manager.get_api_key()
        assert api_key == 'test-api-key-123'

    def test_get_api_key_from_config_file(self, temp_dir):
        """Test getting API key from configuration file."""
        config_file = temp_dir / "config_with_key.yaml"

        config_with_key = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_key': 'config-file-api-key'
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_with_key, f)

        # Ensure no environment variable is set
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigManager(str(config_file))
            api_key = config_manager.get_api_key()
            assert api_key == 'config-file-api-key'

    def test_get_api_key_environment_takes_precedence(self, temp_dir, mock_env_api_key):
        """Test that environment variable takes precedence over config file."""
        config_file = temp_dir / "config_with_key.yaml"

        config_with_key = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_key': 'config-file-api-key'
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_with_key, f)

        config_manager = ConfigManager(str(config_file))
        api_key = config_manager.get_api_key()

        # Environment variable should take precedence
        assert api_key == 'test-api-key-123'

    def test_get_api_key_missing_raises_error(self, temp_dir):
        """Test that missing API key raises ValueError."""
        config_file = temp_dir / "config_no_key.yaml"

        config_without_key = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.8
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_without_key, f)

        # Ensure no environment variable is set
        with patch.dict(os.environ, {}, clear=True):
            config_manager = ConfigManager(str(config_file))

            with pytest.raises(ValueError) as exc_info:
                config_manager.get_api_key()

            assert "API key not found" in str(exc_info.value)
            assert "OPENROUTER_API_KEY" in str(exc_info.value)

    def test_default_config_values(self):
        """Test that all expected default configuration values are present."""
        config_manager = ConfigManager()

        expected_defaults = {
            'input_file': 'input.md',
            'output_file': 'output.md',
            'action_file': 'action.json',
            'payload_file': 'openrouter_editor.payload.json',
            'log_level': 'INFO',
            'log_to_file': False,
            'log_file': 'openrouter_editor.log',
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 25000,
            'enable_compliance_check': True,
            'compliance_output_file': 'compliance_analysis.md',
            'enable_chunking': False,
            'chunk_size': 1000,
            'chunk_identifier': 'ch'
        }

        for key, expected_value in expected_defaults.items():
            assert config_manager.config[key] == expected_value

    def test_config_file_permission_error(self, temp_dir):
        """Test handling of permission errors when reading config file."""
        config_file = temp_dir / "readonly_config.yaml"

        # Create config file
        with open(config_file, 'w') as f:
            yaml.dump({'model': 'test-model'}, f)

        # Mock open to raise PermissionError
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                ConfigManager(str(config_file))

    def test_config_update_behavior(self, temp_dir):
        """Test that user config properly updates default config."""
        config_file = temp_dir / "update_test.yaml"

        user_config = {
            'model': 'custom/model',
            'temperature': 0.1,
            'custom_field': 'custom_value'
        }

        with open(config_file, 'w') as f:
            yaml.dump(user_config, f)

        config_manager = ConfigManager(str(config_file))

        # User values should override defaults
        assert config_manager.config['model'] == 'custom/model'
        assert config_manager.config['temperature'] == 0.1

        # New user fields should be added
        assert config_manager.config['custom_field'] == 'custom_value'

        # Default values should remain for unspecified fields
        assert config_manager.config['max_tokens'] == 25000
        assert config_manager.config['log_level'] == 'INFO'


@pytest.mark.unit
class TestConfigManagerEdgeCases:
    """Test edge cases and error conditions for ConfigManager."""

    def test_config_with_none_values(self, temp_dir):
        """Test configuration with None values."""
        config_file = temp_dir / "none_values.yaml"

        config_with_none = {
            'model': None,
            'temperature': 0.5,
            'api_key': None
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_with_none, f)

        config_manager = ConfigManager(str(config_file))

        # None values are preserved as-is in current implementation
        assert config_manager.config['model'] is None
        # Non-None values should be preserved
        assert config_manager.config['temperature'] == 0.5

    def test_config_with_wrong_types(self, temp_dir):
        """Test configuration with wrong data types."""
        config_file = temp_dir / "wrong_types.yaml"

        config_with_wrong_types = {
            'temperature': "not_a_number",
            'max_tokens': "also_not_a_number",
            'log_to_file': "not_a_boolean"
        }

        with open(config_file, 'w') as f:
            yaml.dump(config_with_wrong_types, f)

        config_manager = ConfigManager(str(config_file))

        # Values should be loaded as-is (no type checking in ConfigManager)
        assert config_manager.config['temperature'] == "not_a_number"
        assert config_manager.config['max_tokens'] == "also_not_a_number"
        assert config_manager.config['log_to_file'] == "not_a_boolean"

    def test_very_large_config_file(self, temp_dir):
        """Test loading a configuration file with many entries."""
        config_file = temp_dir / "large_config.yaml"

        large_config = {}
        # Add many configuration entries
        for i in range(1000):
            large_config[f'key_{i}'] = f'value_{i}'

        # Add some standard entries
        large_config.update({
            'model': 'test-model',
            'temperature': 0.7
        })

        with open(config_file, 'w') as f:
            yaml.dump(large_config, f)

        config_manager = ConfigManager(str(config_file))

        # Should handle large configs without issues
        assert config_manager.config['model'] == 'test-model'
        assert config_manager.config['temperature'] == 0.7
        assert len(config_manager.config) > 1000