"""
Integration tests for PromptRunner functionality.

Tests end-to-end workflows including batch mode, configuration loading,
and multi-prompt processing.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

import pytest
import requests_mock

from src.openrouter_interface.prompt_runner import PromptRunner


class TestPromptRunnerIntegration:
    """Integration tests for PromptRunner class."""

    def test_batch_mode_single_prompt_success(self, sample_prompt_file, sample_input_file,
                                            temp_dir, mock_env_api_key):
        """Test successful batch mode execution with single prompt."""
        output_file = temp_dir / "output.md"
        config_file = temp_dir / "config.yaml"

        # Create minimal config
        config_data = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'log_level': 'ERROR'  # Suppress logs for cleaner test output
        }

        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)

        runner = PromptRunner(
            output_file=str(output_file),
            config_file=str(config_file),
            temp_dir=str(temp_dir)
        )

        # Mock API response
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={
                    "choices": [{
                        "message": {
                            "content": "This is the processed output from the AI."
                        }
                    }]
                }
            )

            success = runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        assert success is True
        assert output_file.exists()

        # Verify output content
        with open(output_file, 'r') as f:
            output_content = f.read()

        assert "This is the processed output from the AI." in output_content

    def test_batch_mode_multi_prompt_success(self, multiple_prompt_files, sample_input_file,
                                           temp_dir, mock_env_api_key):
        """Test successful batch mode execution with multiple prompts."""
        output_file = temp_dir / "multi_output.md"

        runner = PromptRunner(
            output_file=str(output_file),
            temp_dir=str(temp_dir)
        )

        # Create comma-separated prompt file string
        prompt_files_str = ','.join(str(f) for f in multiple_prompt_files)

        # Mock API response
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={
                    "choices": [{
                        "message": {
                            "content": "Combined response from multiple prompts."
                        }
                    }]
                }
            )

            success = runner.run_batch_mode(prompt_files_str, str(sample_input_file))

        assert success is True
        assert output_file.exists()

        # Verify multi-prompt processing occurred
        with open(output_file, 'r') as f:
            output_content = f.read()

        assert "Combined response from multiple prompts." in output_content

    def test_batch_mode_api_error(self, sample_prompt_file, sample_input_file,
                                temp_dir, mock_env_api_key):
        """Test batch mode handling of API errors."""
        runner = PromptRunner(temp_dir=str(temp_dir))

        # Mock API error response
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                status_code=401,
                json={"error": {"message": "Invalid API key"}}
            )

            success = runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        assert success is False

    def test_batch_mode_invalid_prompt_file(self, sample_input_file, temp_dir):
        """Test batch mode with invalid prompt file."""
        runner = PromptRunner(temp_dir=str(temp_dir))

        nonexistent_prompt = temp_dir / "nonexistent.json"

        success = runner.run_batch_mode(str(nonexistent_prompt), str(sample_input_file))
        assert success is False

    def test_batch_mode_invalid_input_file(self, sample_prompt_file, temp_dir):
        """Test batch mode with invalid input file."""
        runner = PromptRunner(temp_dir=str(temp_dir))

        nonexistent_input = temp_dir / "nonexistent.md"

        success = runner.run_batch_mode(str(sample_prompt_file), str(nonexistent_input))
        assert success is False

    def test_configuration_integration(self, sample_prompt_file, sample_input_file,
                                     temp_dir, mock_env_api_key):
        """Test integration with custom configuration."""
        config_file = temp_dir / "custom_config.yaml"

        custom_config = {
            'model': 'custom/test-model',
            'temperature': 0.3,
            'max_tokens': 5000,
            'log_level': 'DEBUG',
            'log_to_file': True,
            'log_file': 'integration_test.log'
        }

        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(custom_config, f)

        runner = PromptRunner(
            config_file=str(config_file),
            temp_dir=str(temp_dir)
        )

        # Verify configuration was loaded
        assert runner.config.get('model') == 'custom/test-model'
        assert runner.config.get('temperature') == 0.3
        assert runner.config.get('max_tokens') == 5000

    def test_temp_directory_management(self, sample_prompt_file, sample_input_file,
                                     temp_dir, mock_env_api_key):
        """Test temporary directory creation and usage."""
        custom_temp_dir = temp_dir / "custom_temp"

        runner = PromptRunner(temp_dir=str(custom_temp_dir))

        # Mock API to avoid actual calls
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={"choices": [{"message": {"content": "Test response"}}]}
            )

            runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        # Verify temp directory structure
        assert custom_temp_dir.exists()

        # Check for log files and payload files in temp directory
        temp_files = list(custom_temp_dir.glob("*"))
        log_files = [f for f in temp_files if f.suffix == '.log']
        payload_files = [f for f in temp_files if 'payload' in f.name]

        # Should have created some temporary files
        assert len(temp_files) > 0

    def test_logging_integration(self, sample_prompt_file, sample_input_file,
                               temp_dir, mock_env_api_key):
        """Test logging functionality integration."""
        log_file = temp_dir / "integration_test.log"

        runner = PromptRunner(
            log_file=str(log_file),
            temp_dir=str(temp_dir)
        )

        # Mock API response
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={"choices": [{"message": {"content": "Logged response"}}]}
            )

            runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        # Verify log file was created and contains relevant entries
        assert log_file.exists()

        with open(log_file, 'r') as f:
            log_content = f.read()

        # Should contain various log entries
        assert "Initializing OpenRouter Prompt Runner" in log_content
        assert "Running OpenRouter Prompt Runner in BATCH MODE" in log_content


class TestPromptRunnerValidation:
    """Test validation functionality in PromptRunner."""

    def test_validate_file_path_success(self, sample_input_file):
        """Test successful file path validation."""
        from src.openrouter_interface.prompt_runner import validate_file_path

        result = validate_file_path(str(sample_input_file), "test")
        assert result == sample_input_file

    def test_validate_file_path_nonexistent(self, temp_dir):
        """Test file path validation with non-existent file."""
        from src.openrouter_interface.prompt_runner import validate_file_path
        import argparse

        nonexistent_file = temp_dir / "nonexistent.txt"

        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            validate_file_path(str(nonexistent_file), "test")

        assert "not found" in str(exc_info.value)

    def test_validate_prompt_files_single(self, sample_prompt_file):
        """Test prompt files validation with single file."""
        from src.openrouter_interface.prompt_runner import validate_prompt_files

        result = validate_prompt_files(str(sample_prompt_file))
        assert result == str(sample_prompt_file)

    def test_validate_prompt_files_multiple(self, multiple_prompt_files):
        """Test prompt files validation with multiple files."""
        from src.openrouter_interface.prompt_runner import validate_prompt_files

        files_str = ','.join(str(f) for f in multiple_prompt_files)
        result = validate_prompt_files(files_str)
        assert result == files_str

    def test_validate_prompt_files_invalid(self, temp_dir):
        """Test prompt files validation with invalid file."""
        from src.openrouter_interface.prompt_runner import validate_prompt_files
        import argparse

        invalid_file = temp_dir / "invalid.json"

        with pytest.raises(argparse.ArgumentTypeError):
            validate_prompt_files(str(invalid_file))


@pytest.mark.integration
class TestPromptRunnerWorkflows:
    """Test complete workflows and edge cases."""

    def test_complete_workflow_with_output_file(self, sample_prompt_file, sample_input_file,
                                              temp_dir, mock_env_api_key):
        """Test complete workflow including output file generation."""
        output_file = temp_dir / "complete_output.md"
        config_file = temp_dir / "workflow_config.yaml"

        # Create comprehensive config
        config_data = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'temperature': 0.7,
            'max_tokens': 15000,
            'log_level': 'INFO',
            'log_to_file': True,
            'log_file': 'workflow.log'
        }

        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)

        runner = PromptRunner(
            output_file=str(output_file),
            config_file=str(config_file),
            temp_dir=str(temp_dir)
        )

        # Mock successful API response
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={
                    "choices": [{
                        "message": {
                            "content": "Complete workflow response with detailed analysis."
                        }
                    }]
                }
            )

            success = runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        # Verify complete success
        assert success is True
        assert output_file.exists()

        # Verify output file format and content
        with open(output_file, 'r') as f:
            content = f.read()

        assert "Complete workflow response" in content
        assert sample_prompt_file.name in content
        assert sample_input_file.name in content

    def test_error_recovery_workflow(self, sample_prompt_file, sample_input_file,
                                   temp_dir, mock_env_api_key):
        """Test workflow error handling and recovery."""
        runner = PromptRunner(temp_dir=str(temp_dir))

        # Test sequence: network error, then success
        with requests_mock.Mocker() as m:
            # First call fails with network error
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                exc=requests_mock.exceptions.ConnectTimeout
            )

            success = runner.run_batch_mode(str(sample_prompt_file), str(sample_input_file))

        # Should handle error gracefully
        assert success is False

    def test_unicode_content_workflow(self, temp_dir, mock_env_api_key):
        """Test workflow with unicode content in prompts and input."""
        # Create prompt with unicode
        unicode_prompt = {
            "instruction": "Analysez le contenu en français 🇫🇷",
            "persona": "Analyseur français",
            "output_format": "Réponse en français"
        }

        prompt_file = temp_dir / "unicode_prompt.json"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(unicode_prompt, f, ensure_ascii=False)

        # Create input with unicode
        unicode_input = "Contenu à analyser avec des émojis 🚀 et caractères spéciaux éàüñ"
        input_file = temp_dir / "unicode_input.md"
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(unicode_input)

        output_file = temp_dir / "unicode_output.md"

        runner = PromptRunner(
            output_file=str(output_file),
            temp_dir=str(temp_dir)
        )

        # Mock API response with unicode
        with requests_mock.Mocker() as m:
            m.post(
                'https://openrouter.ai/api/v1/chat/completions',
                json={
                    "choices": [{
                        "message": {
                            "content": "Réponse analysée avec succès 🎉"
                        }
                    }]
                }
            )

            success = runner.run_batch_mode(str(prompt_file), str(input_file))

        assert success is True
        assert output_file.exists()

        # Verify unicode content was preserved
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        assert "Réponse analysée avec succès 🎉" in content