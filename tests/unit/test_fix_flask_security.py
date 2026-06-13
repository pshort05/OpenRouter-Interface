"""Unit tests for security-critical containment helpers in prompt_runner_flask.

These cover the pure helper functions used to confine user-supplied paths to an
allowed base directory (path-traversal / arbitrary file access defense) and to
restrict local-endpoint URLs to loopback hosts (SSRF defense).
"""

import os
import tempfile
from pathlib import Path

import pytest

from openrouter_interface.prompt_runner_flask import (
    safe_resolve,
    _is_local_endpoint,
)


class TestSafeResolve:
    """Tests for safe_resolve(base, user_path)."""

    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.base = Path(self.tmp) / "prompts"
        self.base.mkdir(parents=True, exist_ok=True)
        # A legitimate file under the base
        (self.base / "foo.json").write_text("{}", encoding="utf-8")

    def test_simple_filename_under_base_accepted(self):
        result = safe_resolve(self.base, "foo.json")
        assert result is not None
        assert result == (self.base / "foo.json").resolve()

    def test_relative_subpath_accepted(self):
        # A relative path that stays inside base resolves OK even if file absent
        result = safe_resolve(self.base, "subdir/bar.json")
        assert result is not None
        assert str(result).startswith(str(self.base.resolve()))

    def test_parent_traversal_rejected(self):
        assert safe_resolve(self.base, "../../etc/passwd") is None

    def test_absolute_path_rejected(self):
        assert safe_resolve(self.base, "/etc/passwd") is None

    def test_base_itself_rejected_as_file(self):
        # Resolving to the base directory itself is not a valid file target
        assert safe_resolve(self.base, "") is None

    def test_sneaky_traversal_with_prefix_rejected(self):
        assert safe_resolve(self.base, "foo/../../../etc/passwd") is None


class TestIsLocalEndpoint:
    """Tests for _is_local_endpoint(url)."""

    @pytest.mark.parametrize(
        "url",
        [
            "http://127.0.0.1:11434/v1",
            "http://localhost:8080",
            "http://[::1]:5000/api",
            "https://127.0.0.1/chat",
            "http://127.0.0.1",
        ],
    )
    def test_loopback_accepted(self, url):
        assert _is_local_endpoint(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "http://example.com/v1",
            "http://169.254.169.254/latest/meta-data",
            "http://10.0.0.5:11434",
            "http://evil.local",
            "ftp://127.0.0.1/x",
            "",
            None,
            "not-a-url",
        ],
    )
    def test_non_loopback_rejected(self, url):
        assert _is_local_endpoint(url) is False
