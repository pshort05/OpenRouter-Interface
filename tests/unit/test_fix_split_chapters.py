"""
Regression tests for split_chapters heading-detection and Roman-numeral bugs.

These tests pin two confirmed defects:

1. Plain-text heading patterns wrongly matched ordinary prose because the
   ``(?:[:\\s\\-].*)?$`` suffix allowed "space + arbitrary text" to satisfy the
   pattern (e.g. "Chapter 1 marked a turning point.").

2. ``roman_to_int`` performed pure subtractive summation with no validity
   check, so invalid numerals converted silently ("IIII" -> 4, "VV" -> 10,
   "MIX" -> 1009).
"""

import pytest

from openrouter_interface.split_chapters import ChapterSplitter, roman_to_int


@pytest.fixture
def splitter(tmp_path):
    """Provide a ChapterSplitter bound to a throwaway input file."""
    input_file = tmp_path / "book.md"
    input_file.write_text("placeholder\n", encoding="utf-8")
    return ChapterSplitter(str(input_file))


# ---------------------------------------------------------------------------
# Bug 1: prose lines must NOT be detected as headings
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prose", [
    "Chapter 1 marked a turning point.",
    "Prologue to the disaster was long.",
    "Epilogue of sorts came next.",
    "Chapter Mix things up",
])
def test_prose_lines_not_detected(splitter, prose):
    assert splitter.detect_section(prose) is None


# ---------------------------------------------------------------------------
# Bug 1: legitimate headings must STILL be detected
# ---------------------------------------------------------------------------

def test_plain_decimal_chapter_detected(splitter):
    assert splitter.detect_section("Chapter 1") == ('chapter', 1)


def test_plain_roman_chapter_with_colon_title_detected(splitter):
    assert splitter.detect_section("Chapter IV: The Title") == ('chapter', 4)


def test_plain_decimal_chapter_with_dash_title_detected(splitter):
    assert splitter.detect_section("Chapter 2 - Middle") == ('chapter', 2)


def test_plain_prologue_detected(splitter):
    assert splitter.detect_section("Prologue") == ('prologue', -1)


def test_plain_epilogue_with_colon_detected(splitter):
    assert splitter.detect_section("Epilogue: End") == ('epilogue', -2)


def test_markdown_header_chapter_detected(splitter):
    assert splitter.detect_section("# Chapter 3") == ('chapter', 3)


# ---------------------------------------------------------------------------
# Bug 2: roman_to_int must reject invalid / non-canonical numerals
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("invalid", ["IIII", "VV", ""])
def test_roman_to_int_rejects_invalid(invalid):
    assert roman_to_int(invalid) is None


@pytest.mark.parametrize("numeral,expected", [
    ("IV", 4),
    ("XLII", 42),
    ("IX", 9),
])
def test_roman_to_int_accepts_valid(numeral, expected):
    assert roman_to_int(numeral) == expected


def test_chapter_mix_prose_not_misrouted_to_chapter_1009(splitter):
    """End-to-end guard for the "Chapter Mix things up" -> chapter_1009.md case.

    "MIX" is a canonically valid Roman numeral (1009), so roman_to_int still
    converts it. The real-world damage is prevented at the detection layer:
    the prose line is not a standalone heading and must not be detected.
    """
    assert splitter.detect_section("Chapter Mix things up") is None
