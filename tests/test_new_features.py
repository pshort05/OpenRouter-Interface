#!/usr/bin/env python3
"""
Test runner for new features added in this session.

Runs comprehensive tests for:
- Per-phase setting override functionality
- Enhanced API parameter handling
- Configuration validation
"""

import subprocess
import sys
from pathlib import Path


def run_test_suite(test_file, description):
    """Run a test suite and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"File: {test_file}")
    print('='*60)

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', test_file, '-v', '--tb=short'
        ], capture_output=True, text=True, timeout=120)

        if result.returncode == 0:
            print(f"✅ {description} - ALL TESTS PASSED")
            # Count passed tests
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line and '==' in line:
                    print(f"   {line.strip()}")
        else:
            print(f"❌ {description} - TESTS FAILED")
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
            print("STDERR:", result.stderr[-500:])  # Last 500 chars

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TESTS TIMED OUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR RUNNING TESTS: {e}")
        return False


def main():
    """Run all new feature tests."""
    print("🧪 Running comprehensive tests for new features")
    print("=" * 80)

    test_suites = [
        ("tests/unit/test_config_manager_new_params.py", "ConfigManager New API Parameters"),
        ("tests/unit/test_api_client_new_params.py", "API Client Enhanced Parameter Handling"),
        ("tests/unit/test_prompt_chain_runner_new_features.py", "Chain Runner Per-Phase Settings"),
        ("tests/unit/test_configuration_validation.py", "Configuration Validation"),
        ("tests/integration/test_chain_runner_new_parameters.py", "Chain Runner Integration Tests")
    ]

    results = []

    for test_file, description in test_suites:
        if Path(test_file).exists():
            success = run_test_suite(test_file, description)
            results.append((description, success))
        else:
            print(f"⚠️  {description} - TEST FILE NOT FOUND: {test_file}")
            results.append((description, False))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)

    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")

    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")

    if passed_tests == total_tests:
        print("🎉 ALL NEW FEATURES TESTED SUCCESSFULLY!")
        return 0
    else:
        print("❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())