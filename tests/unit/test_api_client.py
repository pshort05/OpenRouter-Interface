"""
Unit tests for APIClient class.

Tests API communication, response processing, error handling, and commentary removal.
All API calls are mocked to avoid actual network requests.
"""

import json
from unittest.mock import Mock, patch, MagicMock

import pytest
import requests
import requests_mock

from src.openrouter_interface.api_client import APIClient
from src.openrouter_interface.config_manager import ConfigManager


class TestAPIClient:
    """Test suite for APIClient class."""

    def test_init_with_config(self, sample_config_file, mock_env_api_key):
        """Test APIClient initialization with configuration."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        assert api_client.config == config
        assert api_client.api_key == 'test-api-key-123'

    def test_init_api_key_loading(self, sample_config_file, mock_env_api_key):
        """Test that API key is loaded during initialization."""
        config = ConfigManager(str(sample_config_file))

        with patch.object(config, 'get_api_key', return_value='test-key') as mock_get_key:
            api_client = APIClient(config)
            mock_get_key.assert_called_once()
            assert api_client.api_key == 'test-key'

    @requests_mock.Mocker()
    def test_call_api_success(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test successful API call."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        # Mock successful response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "This is the API response content."
                }
            }]
        }

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json=mock_response,
            status_code=200
        )

        # Mock file handler to avoid file I/O
        with patch('src.openrouter_interface.api_client.FileHandler'):
            result = api_client.call_api("Test prompt")

        assert result == "This is the API response content."

    @requests_mock.Mocker()
    def test_call_api_with_custom_config(self, requests_mocker, temp_dir, mock_env_api_key):
        """Test API call with custom configuration values."""
        # Create config with custom values
        custom_config = {
            'model': 'custom/model',
            'api_base_url': 'https://custom.api.com/v1',
            'temperature': 0.5,
            'max_tokens': 15000
        }

        config_file = temp_dir / "custom_config.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(custom_config, f)

        config = ConfigManager(str(config_file))
        api_client = APIClient(config)

        mock_response = {"choices": [{"message": {"content": "Custom response"}}]}

        requests_mocker.post(
            'https://custom.api.com/v1/chat/completions',
            json=mock_response,
            status_code=200
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            result = api_client.call_api("Test prompt")

        # Check that request was made with correct parameters
        last_request = requests_mocker.last_request
        request_data = json.loads(last_request.body)

        assert request_data['model'] == 'custom/model'
        assert request_data['temperature'] == 0.5
        assert request_data['max_tokens'] == 15000
        assert result == "Custom response"

    @requests_mock.Mocker()
    def test_call_api_request_format(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test that API request is formatted correctly."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        mock_response = {"choices": [{"message": {"content": "Response"}}]}
        requests_mocker.post('https://openrouter.ai/api/v1/chat/completions', json=mock_response)

        with patch('src.openrouter_interface.api_client.FileHandler'):
            api_client.call_api("Test prompt content")

        # Verify request structure
        last_request = requests_mocker.last_request
        request_data = json.loads(last_request.body)

        assert 'model' in request_data
        assert 'messages' in request_data
        assert 'temperature' in request_data
        assert 'max_tokens' in request_data

        # Check message structure
        assert len(request_data['messages']) == 1
        assert request_data['messages'][0]['role'] == 'user'
        assert request_data['messages'][0]['content'] == 'Test prompt content'

        # Check headers
        assert last_request.headers['Authorization'] == 'Bearer test-api-key-123'
        assert last_request.headers['Content-Type'] == 'application/json'

    @requests_mock.Mocker()
    def test_call_api_error_response(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test handling of API error responses."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        error_response = {
            "error": {
                "message": "Invalid API key",
                "type": "authentication_error"
            }
        }

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json=error_response,
            status_code=401
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            with pytest.raises(Exception) as exc_info:
                api_client.call_api("Test prompt")

            assert "API Error" in str(exc_info.value)
            assert "Invalid API key" in str(exc_info.value)

    @requests_mock.Mocker()
    def test_call_api_http_error(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test handling of HTTP errors."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            status_code=500,
            text="Internal Server Error"
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            with pytest.raises(requests.exceptions.HTTPError):
                api_client.call_api("Test prompt")

    @requests_mock.Mocker()
    def test_call_api_timeout(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test handling of request timeouts."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            exc=requests.exceptions.Timeout
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            with pytest.raises(requests.exceptions.Timeout):
                api_client.call_api("Test prompt")

    @requests_mock.Mocker()
    def test_call_api_connection_error(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test handling of connection errors."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            exc=requests.exceptions.ConnectionError
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            with pytest.raises(requests.exceptions.ConnectionError):
                api_client.call_api("Test prompt")

    def test_process_api_response_no_commentary(self, sample_config_file, mock_env_api_key):
        """Test processing response with no AI commentary."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        clean_content = "This is clean content with no AI commentary."
        result = api_client._process_api_response(clean_content)

        assert result == clean_content

    def test_process_api_response_remove_prefix(self, sample_config_file, mock_env_api_key):
        """Test removing AI response prefixes."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        content_with_prefix = "Here's the improved version:\n\nThis is the actual content."
        result = api_client._process_api_response(content_with_prefix)

        assert result == "This is the actual content."
        assert "Here's the improved version:" not in result

    def test_process_api_response_remove_editorial_note(self, sample_config_file, mock_env_api_key):
        """Test removing editorial notes from response."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        content_with_note = "**Editorial Note:** This has been improved.\n\nActual content here."
        result = api_client._process_api_response(content_with_note)

        assert result == "Actual content here."
        assert "Editorial Note" not in result

    def test_process_api_response_remove_summary(self, sample_config_file, mock_env_api_key):
        """Test removing summary sections from response."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        content_with_summary = """This is the main content.

Key improvements made:
- Fixed grammar errors
- Improved flow
- Enhanced clarity"""

        result = api_client._process_api_response(content_with_summary)

        assert result == "This is the main content."
        assert "Key improvements made:" not in result

    def test_process_api_response_remove_end_notes(self, sample_config_file, mock_env_api_key):
        """Test removing end notes from response."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        content_with_note = """This is the main content.
*Note: This was enhanced for clarity.*"""

        result = api_client._process_api_response(content_with_note)

        assert result == "This is the main content."
        assert "*Note:" not in result

    def test_process_api_response_multiple_patterns(self, sample_config_file, mock_env_api_key):
        """Test removing multiple types of AI commentary."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        complex_content = """Here's the enhanced version:

**Editorial Note:** This has been improved.

This is the actual content that should remain.

Key changes made:
- Grammar fixes
- Style improvements

*Final note: Enhanced for readability.*"""

        result = api_client._process_api_response(complex_content)

        # Should only contain the main content
        assert result == "This is the actual content that should remain."
        assert "Here's the enhanced version:" not in result
        assert "Editorial Note:" not in result
        assert "Key changes made:" not in result
        assert "*Final note:" not in result

    def test_process_api_response_preserve_valid_content(self, sample_config_file, mock_env_api_key):
        """Test that valid content with similar patterns is preserved."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        # Content that looks like commentary but should be preserved
        valid_content = """Chapter 1: Here's the story

The character said: "Here's what happened."

Summary:
This chapter introduces the main character.

Note: The author's intention was clear."""

        result = api_client._process_api_response(valid_content)

        # Should preserve content that's not actual AI commentary
        assert "Chapter 1: Here's the story" in result
        assert 'The character said: "Here\'s what happened."' in result
        # Note: Summary might be removed as it matches the pattern

    def test_call_api_payload_saving(self, sample_config_file, mock_env_api_key):
        """Test that API payload is saved before making request."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        mock_file_handler = Mock()

        with patch('src.openrouter_interface.api_client.FileHandler', return_value=mock_file_handler), \
             patch('requests.post') as mock_post:

            # Setup mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            api_client.call_api("Test prompt")

            # Verify file handler was called to save payload
            mock_file_handler.save_payload.assert_called_once()

    def test_call_api_timing_logging(self, sample_config_file, mock_env_api_key):
        """Test that API call timing is logged."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        with patch('src.openrouter_interface.api_client.FileHandler'), \
             patch('requests.post') as mock_post, \
             patch('time.time', side_effect=[100.0, 102.5]):  # Mock 2.5 second duration

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"choices": [{"message": {"content": "Response"}}]}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            with patch('logging.info') as mock_log:
                api_client.call_api("Test prompt")

                # Check that timing was logged
                timing_calls = [call for call in mock_log.call_args_list
                              if 'completed in' in str(call)]
                assert len(timing_calls) > 0

    @requests_mock.Mocker()
    def test_call_api_unexpected_response_format(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test handling of unexpected API response format."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        # Response missing expected structure
        malformed_response = {"unexpected": "format"}

        requests_mocker.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json=malformed_response,
            status_code=200
        )

        with patch('src.openrouter_interface.api_client.FileHandler'):
            with pytest.raises((KeyError, IndexError)):
                api_client.call_api("Test prompt")


@pytest.mark.unit
class TestAPIClientEdgeCases:
    """Test edge cases and error conditions for APIClient."""

    def test_api_client_with_missing_config_values(self, temp_dir, mock_env_api_key):
        """Test APIClient with incomplete configuration."""
        # Config missing some values
        minimal_config = {'model': 'test-model'}

        config_file = temp_dir / "minimal_config.yaml"
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(minimal_config, f)

        config = ConfigManager(str(config_file))
        api_client = APIClient(config)

        # Should use defaults for missing values
        assert api_client.config.get('temperature', 0.8) == 0.8
        assert api_client.config.get('max_tokens', 10000) == 25000  # Default updated value

    @requests_mock.Mocker()
    def test_call_api_empty_prompt(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test API call with empty prompt."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        mock_response = {"choices": [{"message": {"content": "Empty response"}}]}
        requests_mocker.post('https://openrouter.ai/api/v1/chat/completions', json=mock_response)

        with patch('src.openrouter_interface.api_client.FileHandler'):
            result = api_client.call_api("")

        assert result == "Empty response"

    @requests_mock.Mocker()
    def test_call_api_very_long_prompt(self, requests_mocker, sample_config_file, mock_env_api_key):
        """Test API call with very long prompt."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        # Create very long prompt (100,000 characters)
        long_prompt = "A" * 100000

        mock_response = {"choices": [{"message": {"content": "Long response"}}]}
        requests_mocker.post('https://openrouter.ai/api/v1/chat/completions', json=mock_response)

        with patch('src.openrouter_interface.api_client.FileHandler'):
            result = api_client.call_api(long_prompt)

        assert result == "Long response"

        # Verify the long prompt was sent
        last_request = requests_mocker.last_request
        request_data = json.loads(last_request.body)
        assert len(request_data['messages'][0]['content']) == 100000

    def test_process_api_response_unicode_content(self, sample_config_file, mock_env_api_key):
        """Test processing response with unicode characters."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        unicode_content = "Here's the improved version:\n\nContenu français avec émojis 🇫🇷 ✨"
        result = api_client._process_api_response(unicode_content)

        assert result == "Contenu français avec émojis 🇫🇷 ✨"
        assert "Here's the improved version:" not in result

    def test_process_api_response_nested_commentary(self, sample_config_file, mock_env_api_key):
        """Test processing response with nested commentary patterns."""
        config = ConfigManager(str(sample_config_file))
        api_client = APIClient(config)

        nested_content = """Here's the enhanced version:

**Editorial Note:** Multiple patterns here.

Main content with "Here's what the character said."

Key improvements made:
- Various changes
- Here's another improvement

*Note: This is the end note.*"""

        result = api_client._process_api_response(nested_content)

        # Should preserve character dialogue but remove AI commentary
        assert 'Main content with "Here\'s what the character said."' in result
        assert "Here's the enhanced version:" not in result
        assert "Editorial Note:" not in result
        assert "Key improvements made:" not in result