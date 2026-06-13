#!/usr/bin/env python3
"""
Tests for confirmed bug fixes in api_client.py.

Covers:
1. Request timeout must be configurable and default to a generous value
   (>= 300s) for both streaming and non-streaming POST calls. The previous
   hard-coded 30s timeout fails for long-running LLM generations.
2. A 200 response with empty/missing ``choices`` must raise a clear,
   descriptive exception rather than a bare KeyError/IndexError.

These tests patch ``requests.post`` directly (the repo's existing
requests_mock-based tests are broken in this environment).
"""

import unittest
from unittest.mock import Mock, patch

from openrouter_interface.api_client import APIClient


class FakeConfig:
    """Minimal stand-in for ConfigManager driven by a plain dict."""

    def __init__(self, values=None):
        self.values = {
            'model': 'anthropic/claude-4-sonnet-20250522',
            'api_base_url': 'https://openrouter.ai/api/v1',
            'temperature': 0.8,
            'max_tokens': 100,
        }
        if values:
            self.values.update(values)

    def get(self, key, default=None):
        return self.values.get(key, default)

    def get_api_key(self):
        return 'fake-api-key'


def _make_response(payload, status_code=200):
    """Build a Mock response object behaving like requests.Response."""
    response = Mock()
    response.status_code = status_code
    response.headers = {}
    response.json.return_value = payload
    response.text = str(payload)
    response.raise_for_status.return_value = None
    return response


class TestRequestTimeout(unittest.TestCase):
    """The POST timeout must be generous and configurable."""

    def _timeout_seconds(self, timeout):
        """Normalize a timeout (scalar or (connect, read) tuple) to read secs."""
        if isinstance(timeout, (tuple, list)):
            return timeout[-1]
        return timeout

    def test_non_streaming_timeout_default_is_generous(self):
        config = FakeConfig()
        client = APIClient(config)
        valid_payload = {
            'choices': [{'message': {'content': 'hello world'}}]
        }
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = _make_response(valid_payload)
            client.call_api('prompt')

        self.assertTrue(mock_post.called)
        timeout = mock_post.call_args.kwargs.get('timeout')
        self.assertIsNotNone(timeout, "timeout kwarg must be passed to requests.post")
        self.assertGreaterEqual(
            self._timeout_seconds(timeout), 300,
            f"non-streaming timeout too short: {timeout}",
        )

    def test_streaming_timeout_default_is_generous(self):
        config = FakeConfig({'stream': True})
        client = APIClient(config)
        streaming_response = _make_response({})
        streaming_response.iter_lines.return_value = iter([
            'data: {"choices":[{"delta":{"content":"hi"}}]}',
            'data: [DONE]',
        ])
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = streaming_response
            client.call_api('prompt')

        self.assertTrue(mock_post.called)
        timeout = mock_post.call_args.kwargs.get('timeout')
        self.assertIsNotNone(timeout, "timeout kwarg must be passed to requests.post")
        self.assertGreaterEqual(
            self._timeout_seconds(timeout), 300,
            f"streaming timeout too short: {timeout}",
        )

    def test_timeout_is_configurable(self):
        config = FakeConfig({'request_timeout': 600})
        client = APIClient(config)
        valid_payload = {
            'choices': [{'message': {'content': 'hello'}}]
        }
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = _make_response(valid_payload)
            client.call_api('prompt')

        timeout = mock_post.call_args.kwargs.get('timeout')
        self.assertEqual(self._timeout_seconds(timeout), 600)


class TestMissingChoices(unittest.TestCase):
    """A 200 response without usable choices must fail clearly."""

    def test_empty_choices_raises_clear_error(self):
        config = FakeConfig()
        client = APIClient(config)
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = _make_response({'choices': []})
            with self.assertRaises((ValueError, RuntimeError)) as ctx:
                client.call_api('prompt')

        # Should not be a bare KeyError/IndexError, and message should be useful.
        self.assertNotIsInstance(ctx.exception, (KeyError, IndexError))
        self.assertTrue(str(ctx.exception).strip())

    def test_missing_choices_key_raises_clear_error(self):
        config = FakeConfig()
        client = APIClient(config)
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = _make_response({'usage': {'total_tokens': 0}})
            with self.assertRaises((ValueError, RuntimeError)) as ctx:
                client.call_api('prompt')

        self.assertNotIsInstance(ctx.exception, (KeyError, IndexError))
        self.assertTrue(str(ctx.exception).strip())

    def test_choice_missing_message_content_raises_clear_error(self):
        config = FakeConfig()
        client = APIClient(config)
        with patch('openrouter_interface.api_client.requests.post') as mock_post:
            mock_post.return_value = _make_response({'choices': [{'message': {}}]})
            with self.assertRaises((ValueError, RuntimeError)) as ctx:
                client.call_api('prompt')

        self.assertNotIsInstance(ctx.exception, (KeyError, IndexError))
        self.assertTrue(str(ctx.exception).strip())


if __name__ == '__main__':
    unittest.main()
