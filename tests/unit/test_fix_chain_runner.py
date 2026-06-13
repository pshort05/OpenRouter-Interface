"""
Regression tests for prompt_chain_runner / chain_status bug fixes.

Covers:
- Multi-pass execution (passes: N) actually runs N times with content chaining.
- postscript executes after a successful step (and its failure does not fail the step).
- output_append / per-step append accumulation wiring.
- _validate_file_size does not mutate the shared config dict.
- _get_intermediate_filename sanitizes prompt names (single definition).
- ChainStatusManager restart helpers are robust and persist step output paths.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from openrouter_interface.prompt_chain_runner import PromptChainRunner
from openrouter_interface.chain_status import ChainStatusManager


def _make_runner(tmp_path, config=None):
    """Build a PromptChainRunner without running __init__, with the minimal
    attributes _process_step and friends need."""
    runner = PromptChainRunner.__new__(PromptChainRunner)
    runner.config = config if config is not None else {}
    runner.temp_dir = tmp_path
    runner.status_manager = Mock()
    runner.console = Mock()
    return runner


def _stub_step_collaborators(runner):
    """Stub the side-effecting collaborators of _process_step so it can run in
    isolation. _run_prompt_runner writes its output file and records calls."""
    calls = []

    def fake_run(prompt_config, input_file, output_file, step_display):
        in_path = Path(input_file)
        out_path = Path(output_file)
        in_text = in_path.read_text(encoding='utf-8') if in_path.exists() else ""
        calls.append({'input': in_path, 'output': out_path, 'input_text': in_text})
        out_path.write_text(f"OUT[{in_text}]", encoding='utf-8')
        return (True, None)

    runner._run_prompt_runner = fake_run
    runner._verify_output_file = lambda *a, **k: True
    runner._format_file_size = lambda *a, **k: "1.0k"
    runner._convert_step_output = lambda *a, **k: None
    return calls


# --------------------------------------------------------------------------
# Multi-pass
# --------------------------------------------------------------------------
def test_multi_pass_runs_n_times_with_content_chaining(tmp_path):
    runner = _make_runner(tmp_path)
    calls = _stub_step_collaborators(runner)

    input_file = tmp_path / "chapter.md"
    input_file.write_text("seed", encoding='utf-8')

    prompt_config = {'prompt_file': 'p.json', 'name': 'humanize', 'passes': 3}
    file_result = {'prompts': []}

    ok = runner._process_step(input_file, "1", prompt_config, input_file, file_result, [])

    assert ok is True
    assert len(calls) == 3, "passes:3 must invoke the runner three times"
    # Pass 2's input must be pass 1's output content (chaining), not the seed.
    assert calls[1]['input_text'] == "OUT[seed]"
    assert calls[2]['input_text'] == "OUT[OUT[seed]]"


def test_single_pass_runs_once(tmp_path):
    runner = _make_runner(tmp_path)
    calls = _stub_step_collaborators(runner)
    input_file = tmp_path / "in.md"
    input_file.write_text("seed", encoding='utf-8')
    runner._process_step(input_file, "1", {'prompt_file': 'p.json', 'name': 'x', 'passes': 1}, input_file, {'prompts': []}, [])
    assert len(calls) == 1


# --------------------------------------------------------------------------
# postscript
# --------------------------------------------------------------------------
def test_postscript_executes_after_successful_step(tmp_path):
    runner = _make_runner(tmp_path)
    _stub_step_collaborators(runner)
    script_calls = []
    runner._execute_single_script = lambda cmd, kind, step, inp, outp: (script_calls.append(kind) or True)

    input_file = tmp_path / "in.md"
    input_file.write_text("seed", encoding='utf-8')
    runner._process_step(input_file, "1",
                         {'prompt_file': 'p.json', 'name': 'x', 'postscript': 'wc -l {output_file}'},
                         input_file, {'prompts': []}, [])
    assert "postscript" in script_calls


def test_postscript_failure_does_not_fail_step(tmp_path):
    runner = _make_runner(tmp_path)
    _stub_step_collaborators(runner)
    # prescript path must succeed; postscript returns False.
    runner._execute_single_script = lambda cmd, kind, step, inp, outp: kind != "postscript"

    input_file = tmp_path / "in.md"
    input_file.write_text("seed", encoding='utf-8')
    ok = runner._process_step(input_file, "1",
                             {'prompt_file': 'p.json', 'name': 'x', 'postscript': 'false'},
                             input_file, {'prompts': []}, [])
    assert ok is True, "postscript failure is logged but must not fail the step"


# --------------------------------------------------------------------------
# append accumulation
# --------------------------------------------------------------------------
def test_accumulate_if_appending_global(tmp_path):
    runner = _make_runner(tmp_path, config={'output_append': True})
    step_out = tmp_path / "step1.md"
    step_out.write_text("STEP ONE BODY", encoding='utf-8')
    final = tmp_path / "final.md"

    appended = runner._accumulate_if_appending(step_out, final, "1", {'name': 'grammar'})

    assert appended is True
    assert final.exists()
    assert "STEP ONE BODY" in final.read_text(encoding='utf-8')


def test_accumulate_if_appending_per_step_flag(tmp_path):
    runner = _make_runner(tmp_path, config={})
    step_out = tmp_path / "step1.md"
    step_out.write_text("BODY", encoding='utf-8')
    final = tmp_path / "final.md"
    appended = runner._accumulate_if_appending(step_out, final, "1", {'name': 'x', 'append': 'yes'})
    assert appended is True
    assert "BODY" in final.read_text(encoding='utf-8')


def test_accumulate_if_appending_disabled(tmp_path):
    runner = _make_runner(tmp_path, config={})
    step_out = tmp_path / "step1.md"
    step_out.write_text("BODY", encoding='utf-8')
    final = tmp_path / "final.md"
    appended = runner._accumulate_if_appending(step_out, final, "1", {'name': 'x'})
    assert appended is False
    assert not final.exists()


# --------------------------------------------------------------------------
# _validate_file_size must not mutate shared config
# --------------------------------------------------------------------------
def test_validate_file_size_does_not_mutate_config(tmp_path):
    runner = _make_runner(tmp_path, config={
        'file_size_validation': {'enabled': True, 'max_size_difference_percent': 50}
    })
    f = tmp_path / "f.md"
    f.write_text("x" * 100, encoding='utf-8')

    runner._validate_file_size(f, f, "1", step_config={'max_size_difference_percent': 5})

    assert runner.config['file_size_validation']['max_size_difference_percent'] == 50, \
        "step-level override must not leak into the shared config"


# --------------------------------------------------------------------------
# intermediate filename sanitization (single definition)
# --------------------------------------------------------------------------
def test_intermediate_filename_sanitizes_prompt_name(tmp_path):
    runner = _make_runner(tmp_path)
    name = runner._get_intermediate_filename(Path("book.md"), "1", "AI Word Cleaning")
    assert " " not in name
    assert name.endswith(".md")


# --------------------------------------------------------------------------
# ChainStatusManager robustness + output-path persistence
# --------------------------------------------------------------------------
def test_get_restart_point_ignores_nonnumeric_step_keys(tmp_path):
    cfg = tmp_path / "chain.yaml"
    cfg.write_text("prompts: {}\n", encoding='utf-8')
    mgr = ChainStatusManager(cfg)
    mgr.status_data["files"]["f.md"] = {
        "status": "running",
        "steps": {
            "1": {"status": "completed"},
            "grammar": {"status": "running"},   # non-numeric key must not crash
            "2": {"status": "failed"},
        },
    }
    # Must not raise ValueError.
    point = mgr.get_restart_point("f.md")
    assert point is not None


def test_update_step_complete_creates_entry_and_stores_output_path(tmp_path):
    cfg = tmp_path / "chain.yaml"
    cfg.write_text("prompts: {}\n", encoding='utf-8')
    mgr = ChainStatusManager(cfg)
    # No prior update_step_start: must still record completion (no silent no-op).
    mgr.update_step_complete("f.md", "1", 1.0, "2.0k", output_path="/tmp/out_step1.md")
    step = mgr.status_data["files"]["f.md"]["steps"]["1"]
    assert step["status"] == "completed"
    assert mgr.get_step_output_path("f.md", "1") == "/tmp/out_step1.md"
