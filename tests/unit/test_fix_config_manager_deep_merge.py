"""
Regression tests for ConfigManager nested-dict deep merge.

Confirms that overriding a single sub-key of a nested config dict (e.g.
file_size_validation.enabled) preserves the other default sub-keys instead of
replacing the entire nested dict via a shallow update.
"""

import yaml

from src.openrouter_interface.config_manager import ConfigManager


class TestConfigManagerDeepMerge:
    """Test suite for recursive deep merge of nested configuration."""

    def test_partial_nested_override_preserves_sibling_defaults(self, temp_dir):
        """Overriding one sub-key of a nested dict keeps the other defaults."""
        config_file = temp_dir / "partial_nested.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'file_size_validation': {'enabled': False}}, f)

        config_manager = ConfigManager(str(config_file))

        fsv = config_manager.config['file_size_validation']
        # User override applied
        assert fsv['enabled'] is False
        # Sibling defaults preserved (would be dropped by a shallow update)
        assert fsv['max_size_difference_percent'] == 30
        assert fsv['min_file_size_bytes'] == 100

    def test_top_level_scalar_override_still_works(self, temp_dir):
        """Top-level scalar values still override the defaults."""
        config_file = temp_dir / "scalar_override.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'temperature': 0.2, 'max_tokens': 12345}, f)

        config_manager = ConfigManager(str(config_file))

        assert config_manager.config['temperature'] == 0.2
        assert config_manager.config['max_tokens'] == 12345
        # Unspecified defaults remain intact
        assert config_manager.config['model'] == 'anthropic/claude-4-sonnet-20250522'

    def test_nested_key_only_in_user_config_is_added(self, temp_dir):
        """A nested sub-key present only in the user config is added."""
        config_file = temp_dir / "new_nested_key.yaml"
        with open(config_file, 'w') as f:
            yaml.dump({'file_size_validation': {'extra_threshold': 7}}, f)

        config_manager = ConfigManager(str(config_file))

        fsv = config_manager.config['file_size_validation']
        # New user-only sub-key added
        assert fsv['extra_threshold'] == 7
        # Existing defaults still present
        assert fsv['enabled'] is True
        assert fsv['max_size_difference_percent'] == 30
        assert fsv['min_file_size_bytes'] == 100
