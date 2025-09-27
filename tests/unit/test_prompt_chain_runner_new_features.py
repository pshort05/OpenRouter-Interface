"""
Unit tests for PromptChainRunner new per-phase setting override features.

Tests the enhanced setting override system and configuration hierarchy.
"""

import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.openrouter_interface.prompt_chain_runner import PromptChainRunner


class TestPromptChainRunnerSettingOverrides:
    """Test suite for per-phase setting override functionality."""

    def test_get_prompt_settings_string_config(self):
        """Test extracting settings from string prompt config."""
        runner = self._create_test_runner()

        # String config should return empty settings
        settings = runner._get_prompt_settings("simple_prompt.json")
        assert settings == {}

    def test_get_prompt_settings_dict_config(self):
        """Test extracting settings from dictionary prompt config."""
        runner = self._create_test_runner()

        prompt_config = {
            'prompt_file': 'test.json',
            'config_file': 'config.yaml',
            'name': 'test_prompt',
            'model': 'openai/gpt-4-turbo',
            'temperature': 0.3,
            'top_k': 25,
            'frequency_penalty': 0.2
        }

        settings = runner._get_prompt_settings(prompt_config)

        # Should extract only the setting parameters, not special keys
        expected_settings = {
            'model': 'openai/gpt-4-turbo',
            'temperature': 0.3,
            'top_k': 25,
            'frequency_penalty': 0.2
        }

        assert settings == expected_settings

    def test_get_prompt_settings_excludes_special_keys(self):
        """Test that special keys are excluded from settings extraction."""
        runner = self._create_test_runner()

        prompt_config = {
            'prompt_file': 'test.json',      # Special key - should be excluded
            'config_file': 'config.yaml',   # Special key - should be excluded
            'name': 'test_prompt',           # Special key - should be excluded
            'model': 'test-model',           # Setting - should be included
            'temperature': 0.5,              # Setting - should be included
            'custom_setting': 'value'        # Setting - should be included
        }

        settings = runner._get_prompt_settings(prompt_config)

        # Should only include non-special keys
        expected_settings = {
            'model': 'test-model',
            'temperature': 0.5,
            'custom_setting': 'value'
        }

        assert settings == expected_settings
        assert 'prompt_file' not in settings
        assert 'config_file' not in settings
        assert 'name' not in settings

    def test_create_step_config_file_no_settings_no_global(self, temp_dir):
        """Test config file creation when no settings or global config."""
        runner = self._create_test_runner(temp_dir=temp_dir)

        # No step settings, no global config, no prompt_runner_config
        result = runner._create_step_config_file(1, {})

        assert result is None

    def test_create_step_config_file_with_step_settings(self, temp_dir):
        """Test config file creation with step-specific settings."""
        runner = self._create_test_runner(temp_dir=temp_dir)

        step_settings = {
            'model': 'openai/gpt-4-turbo',
            'temperature': 0.3,
            'top_k': 25
        }

        config_file = runner._create_step_config_file(1, step_settings)

        assert config_file is not None
        assert Path(config_file).exists()

        # Verify config file content
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        assert config_data['model'] == 'openai/gpt-4-turbo'
        assert config_data['temperature'] == 0.3
        assert config_data['top_k'] == 25

    def test_create_step_config_file_with_global_config(self, temp_dir):
        """Test config file creation with global config."""
        global_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.7,
            'max_tokens': 20000,
            'top_p': 0.9
        }

        runner = self._create_test_runner(temp_dir=temp_dir, global_config=global_config)

        config_file = runner._create_step_config_file(1, {})

        assert config_file is not None

        # Verify global config is included
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        assert config_data['model'] == 'anthropic/claude-4-sonnet-20250522'
        assert config_data['temperature'] == 0.7
        assert config_data['max_tokens'] == 20000
        assert config_data['top_p'] == 0.9

    def test_create_step_config_file_setting_override_hierarchy(self, temp_dir):
        """Test that step settings override global config."""
        global_config = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.7,
            'max_tokens': 20000,
            'top_p': 0.9
        }

        runner = self._create_test_runner(temp_dir=temp_dir, global_config=global_config)

        step_settings = {
            'model': 'openai/gpt-4-turbo',  # Override global model
            'temperature': 0.3,             # Override global temperature
            'top_k': 25                     # New setting
        }

        config_file = runner._create_step_config_file(1, step_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Step settings should override global
        assert config_data['model'] == 'openai/gpt-4-turbo'
        assert config_data['temperature'] == 0.3
        assert config_data['top_k'] == 25

        # Global settings not overridden should remain
        assert config_data['max_tokens'] == 20000
        assert config_data['top_p'] == 0.9

    def test_create_step_config_file_with_prompt_runner_config(self, temp_dir):
        """Test config file creation with base prompt_runner_config."""
        # Create a base config file
        base_config_file = temp_dir / "base_config.yaml"
        base_config = {
            'model': 'base-model',
            'temperature': 0.5,
            'api_base_url': 'https://api.example.com'
        }

        with open(base_config_file, 'w') as f:
            yaml.dump(base_config, f)

        runner = self._create_test_runner(
            temp_dir=temp_dir,
            prompt_runner_config=str(base_config_file)
        )

        step_settings = {
            'model': 'override-model',
            'max_tokens': 15000
        }

        config_file = runner._create_step_config_file(1, step_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Should have base config
        assert config_data['api_base_url'] == 'https://api.example.com'
        assert config_data['temperature'] == 0.5

        # Step settings should override base
        assert config_data['model'] == 'override-model'
        assert config_data['max_tokens'] == 15000

    def test_create_step_config_file_complete_hierarchy(self, temp_dir):
        """Test complete configuration hierarchy: base -> global -> step."""
        # Create base config file
        base_config_file = temp_dir / "base_config.yaml"
        base_config = {
            'model': 'base-model',
            'temperature': 0.5,
            'max_tokens': 10000,
            'api_base_url': 'https://api.example.com'
        }

        with open(base_config_file, 'w') as f:
            yaml.dump(base_config, f)

        global_config = {
            'model': 'global-model',      # Override base
            'temperature': 0.7,           # Override base
            'top_p': 0.9                  # New setting
        }

        runner = self._create_test_runner(
            temp_dir=temp_dir,
            global_config=global_config,
            prompt_runner_config=str(base_config_file)
        )

        step_settings = {
            'model': 'step-model',        # Override global
            'frequency_penalty': 0.1      # New setting
        }

        config_file = runner._create_step_config_file(1, step_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Final hierarchy should be: step > global > base
        assert config_data['model'] == 'step-model'        # Step override
        assert config_data['temperature'] == 0.7           # Global override
        assert config_data['max_tokens'] == 10000          # Base value
        assert config_data['api_base_url'] == 'https://api.example.com'  # Base value
        assert config_data['top_p'] == 0.9                 # Global setting
        assert config_data['frequency_penalty'] == 0.1     # Step setting

    def test_create_step_config_file_logs_overrides(self, temp_dir, caplog):
        """Test that setting overrides are logged."""
        runner = self._create_test_runner(temp_dir=temp_dir)

        step_settings = {
            'model': 'test-model',
            'temperature': 0.3,
            'top_k': 25
        }

        with caplog.at_level('INFO'):
            runner._create_step_config_file(1, step_settings)

        # Should log the step-specific settings
        assert "Step 1: Using step-specific settings:" in caplog.text
        assert "model: test-model" in caplog.text
        assert "temperature: 0.3" in caplog.text
        assert "top_k: 25" in caplog.text

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def _create_test_runner(self, temp_dir=None, global_config=None, prompt_runner_config=None):
        """Helper to create a test PromptChainRunner instance."""
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp())

        # Create a minimal config file
        config_file = temp_dir / "test_config.yaml"
        config_data = {
            'input_file': 'test_input.md',
            'output_file': 'test_output.md',
            'prompts': {
                'prompt 1': 'test_prompt.json'
            }
        }

        if global_config:
            config_data['global_config'] = global_config

        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Create test input file
        input_file = temp_dir / "test_input.md"
        input_file.write_text("Test input content")

        # Create test prompt file
        prompt_dir = temp_dir / "prompts"
        prompt_dir.mkdir(exist_ok=True)
        prompt_file = prompt_dir / "test_prompt.json"
        prompt_file.write_text('{"system_prompt": "Test prompt"}')

        # Mock the runner to avoid actual execution
        with patch('src.openrouter_interface.prompt_chain_runner.PromptChainRunner.__init__') as mock_init:
            mock_init.return_value = None
            runner = PromptChainRunner.__new__(PromptChainRunner)

            # Set up minimal required attributes
            runner.config_file = config_file
            runner.config = config_data
            runner.temp_dir = temp_dir
            runner.prompt_runner_config = prompt_runner_config
            runner.total_prompts = 1

            return runner


class TestPromptChainRunnerAdvancedParameterHandling:
    """Test advanced parameter handling scenarios."""

    def test_complex_parameter_types_preservation(self, temp_dir):
        """Test that complex parameter types are preserved correctly."""
        runner = self._create_basic_runner(temp_dir)

        complex_settings = {
            'response_format': {'type': 'json_object', 'schema': {'properties': {'answer': {'type': 'string'}}}},
            'provider': {'order': ['Anthropic', 'OpenAI'], 'allow_fallbacks': True},
            'models': ['anthropic/claude-4-sonnet-20250522', 'openai/gpt-4-turbo'],
            'transforms': ['middle-out', 'compression'],
            'usage': {'include': True, 'detailed': False}
        }

        config_file = runner._create_step_config_file(1, complex_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Verify complex types are preserved
        assert config_data['response_format'] == complex_settings['response_format']
        assert config_data['provider'] == complex_settings['provider']
        assert config_data['models'] == complex_settings['models']
        assert config_data['transforms'] == complex_settings['transforms']
        assert config_data['usage'] == complex_settings['usage']

    def test_numeric_parameter_precision(self, temp_dir):
        """Test that numeric parameter precision is maintained."""
        runner = self._create_basic_runner(temp_dir)

        precise_settings = {
            'temperature': 0.123456789,
            'top_p': 0.987654321,
            'frequency_penalty': -1.5,
            'presence_penalty': 1.999999,
            'repetition_penalty': 0.000001,
            'min_p': 0.0001
        }

        config_file = runner._create_step_config_file(1, precise_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Verify precision is maintained
        for key, value in precise_settings.items():
            assert abs(config_data[key] - value) < 1e-10

    def test_boolean_parameter_handling(self, temp_dir):
        """Test that boolean parameters are handled correctly."""
        runner = self._create_basic_runner(temp_dir)

        boolean_settings = {
            'stream': True,
            'enable_logging': False,
            'debug_mode': True
        }

        config_file = runner._create_step_config_file(1, boolean_settings)

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        # Verify boolean values are preserved
        assert config_data['stream'] is True
        assert config_data['enable_logging'] is False
        assert config_data['debug_mode'] is True

    def test_step_config_filename_format(self, temp_dir):
        """Test that step config files follow correct naming convention."""
        runner = self._create_basic_runner(temp_dir)

        # Test different step numbers
        for step_num in [1, 5, 10, 99]:
            config_file = runner._create_step_config_file(step_num, {'model': 'test'})

            expected_filename = f"step_{step_num:02d}_config.yaml"
            assert Path(config_file).name == expected_filename

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def _create_basic_runner(self, temp_dir):
        """Helper to create a basic test runner."""
        with patch('src.openrouter_interface.prompt_chain_runner.PromptChainRunner.__init__') as mock_init:
            mock_init.return_value = None
            runner = PromptChainRunner.__new__(PromptChainRunner)

            runner.temp_dir = temp_dir
            runner.config = {}
            runner.prompt_runner_config = None

            return runner


class TestPromptChainRunnerParameterValidation:
    """Test parameter validation and error handling."""

    def test_invalid_step_number_handling(self, temp_dir):
        """Test handling of invalid step numbers."""
        runner = self._create_basic_runner(temp_dir)

        # Should handle edge case step numbers gracefully
        config_file = runner._create_step_config_file(0, {'model': 'test'})
        assert Path(config_file).name == "step_00_config.yaml"

        config_file = runner._create_step_config_file(100, {'model': 'test'})
        assert Path(config_file).name == "step_100_config.yaml"

    def test_empty_settings_dict(self, temp_dir):
        """Test handling of empty settings dictionary."""
        runner = self._create_basic_runner(temp_dir)

        # Empty settings should still create file if global config exists
        runner.config = {'global_config': {'model': 'test'}}

        config_file = runner._create_step_config_file(1, {})
        assert config_file is not None

        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        assert config_data['model'] == 'test'

    def _create_basic_runner(self, temp_dir):
        """Helper to create a basic test runner."""
        with patch('src.openrouter_interface.prompt_chain_runner.PromptChainRunner.__init__') as mock_init:
            mock_init.return_value = None
            runner = PromptChainRunner.__new__(PromptChainRunner)

            runner.temp_dir = temp_dir
            runner.config = {}
            runner.prompt_runner_config = None

            return runner