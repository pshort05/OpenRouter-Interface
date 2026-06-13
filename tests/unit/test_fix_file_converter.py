"""
Regression tests for file_converter conversion bugs.

These tests pin three confirmed defects:

1. Source-file overwrite on round-trip: when the computed output path resolves
   to the same path as the input file, the conversion silently overwrote the
   user's original source. The converter must now raise a clear error instead.

2. Zero-byte output counted as success: success was asserted solely on the
   output file existing. A failed/partial pandoc run can leave a 0-byte file
   that passed. The converter must require a non-empty output file.

3. ``tex`` format identifier passed to pandoc: pandoc's identifier is
   ``latex``, not ``tex``. A ``.tex`` input/format must be normalized to
   ``latex`` before being handed to pypandoc.
"""

import pytest

from openrouter_interface.file_converter import FileConverter


@pytest.fixture
def converter():
    """Provide a FileConverter that reports conversion as available."""
    conv = FileConverter()
    # Force availability so tests do not require pandoc/pypandoc installed.
    conv.pypandoc_available = True
    conv.pandoc_available = True
    return conv


def _install_fake_pypandoc(monkeypatch, *, written_bytes=b"converted output\n"):
    """Install a fake ``pypandoc`` module that records calls and writes output.

    Returns the list of recorded calls. Each call is a dict with the positional
    args and the ``format`` keyword passed to ``convert_file``.

    If ``written_bytes`` is ``b""`` the fake simulates a partial pandoc run that
    leaves a 0-byte file.
    """
    import sys
    import types

    calls = []

    def fake_convert_file(source, to, format=None, outputfile=None, extra_args=None):
        calls.append({
            "source": source,
            "to": to,
            "format": format,
            "outputfile": outputfile,
        })
        if outputfile is not None:
            with open(outputfile, "wb") as handle:
                handle.write(written_bytes)
        return ""

    fake_module = types.ModuleType("pypandoc")
    fake_module.convert_file = fake_convert_file
    fake_module.get_pandoc_version = lambda: "3.0"
    monkeypatch.setitem(sys.modules, "pypandoc", fake_module)
    return calls


# ---------------------------------------------------------------------------
# Bug 1: output path equal to input path must raise (no source overwrite)
# ---------------------------------------------------------------------------

def test_convert_to_markdown_refuses_to_overwrite_source(converter, monkeypatch, tmp_path):
    calls = _install_fake_pypandoc(monkeypatch)
    # A .md input produces a .md output at the same path. The guard must fire
    # before pandoc is ever invoked.
    source = tmp_path / "book.md"
    source.write_text("# original\n", encoding="utf-8")

    with pytest.raises(Exception, match="overwrite"):
        converter.convert_to_markdown(source, from_format="latex")
    assert not calls, "pandoc should not run when output would clobber the source"


def test_convert_from_markdown_refuses_to_overwrite_source(converter, monkeypatch, tmp_path):
    calls = _install_fake_pypandoc(monkeypatch)
    # Converting a .txt back to .txt would land on the same path.
    source = tmp_path / "book.txt"
    source.write_text("plain text\n", encoding="utf-8")

    with pytest.raises(Exception, match="overwrite"):
        converter.convert_from_markdown(source, "txt", output_file=source)
    assert not calls, "pandoc should not run when output would clobber the source"


# ---------------------------------------------------------------------------
# Bug 2: a 0-byte output must not be reported as success
# ---------------------------------------------------------------------------

def test_convert_to_markdown_rejects_zero_byte_output(converter, monkeypatch, tmp_path):
    _install_fake_pypandoc(monkeypatch, written_bytes=b"")
    source = tmp_path / "book.docx"
    source.write_text("ignored\n", encoding="utf-8")

    with pytest.raises(Exception):
        converter.convert_to_markdown(source, from_format="docx")


def test_convert_from_markdown_rejects_zero_byte_output(converter, monkeypatch, tmp_path):
    _install_fake_pypandoc(monkeypatch, written_bytes=b"")
    source = tmp_path / "book.md"
    source.write_text("# content\n", encoding="utf-8")

    with pytest.raises(Exception):
        converter.convert_from_markdown(source, "docx")


# ---------------------------------------------------------------------------
# Bug 3: 'tex' must be normalized to pandoc's 'latex' identifier
# ---------------------------------------------------------------------------

def test_detect_format_normalizes_tex_to_latex(converter, tmp_path):
    source = tmp_path / "paper.tex"
    source.write_text("\\documentclass{article}\n", encoding="utf-8")
    assert converter.detect_format(source) == "latex"


def test_convert_to_markdown_passes_latex_for_tex_input(converter, monkeypatch, tmp_path):
    calls = _install_fake_pypandoc(monkeypatch)
    source = tmp_path / "paper.tex"
    source.write_text("\\documentclass{article}\n", encoding="utf-8")

    converter.convert_to_markdown(source)

    assert calls, "pypandoc.convert_file was not called"
    assert calls[0]["format"] == "latex"


def test_convert_from_markdown_passes_latex_for_tex_output(converter, monkeypatch, tmp_path):
    calls = _install_fake_pypandoc(monkeypatch)
    source = tmp_path / "book.md"
    source.write_text("# content\n", encoding="utf-8")

    converter.convert_from_markdown(source, "tex")

    assert calls, "pypandoc.convert_file was not called"
    assert calls[0]["to"] == "latex"
