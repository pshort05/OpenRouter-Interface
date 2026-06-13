#!/usr/bin/env python3
"""
Chapter Splitter - Split markdown documents into separate files by chapter

This utility reads a markdown file and splits it into separate files based on
chapter headings (e.g., "# Chapter 1", "## Chapter 2", etc.).

Supports:
- Decimal chapter numbers (Chapter 1, Chapter 2)
- Roman numeral chapter numbers (Chapter I, Chapter II)
- Prologue and Epilogue sections
- Both markdown headers (# Chapter 1) and plain text format (Chapter 1)

Usage:
    python split_chapters.py input.md
    python split_chapters.py input.md -o output_dir
    python split_chapters.py input.md --dry-run
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def roman_to_int(roman: str) -> Optional[int]:
    """
    Convert Roman numeral to integer.

    Args:
        roman: Roman numeral string (e.g., "I", "IV", "IX", "XLII")

    Returns:
        Integer value or None if invalid
    """
    roman = roman.upper()

    # Reject empty or non-canonical numerals before summation, so that
    # invalid forms (e.g. "IIII", "VV") do not convert silently.
    if not roman or not re.match(
        r'^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$',
        roman
    ):
        return None

    roman_values = {
        'I': 1, 'V': 5, 'X': 10, 'L': 50,
        'C': 100, 'D': 500, 'M': 1000
    }

    total = 0
    prev_value = 0

    for char in reversed(roman):
        if char not in roman_values:
            return None

        value = roman_values[char]
        if value < prev_value:
            total -= value
        else:
            total += value
        prev_value = value

    return total


class ChapterSplitter:
    """Splits markdown documents by chapter headings."""

    # Multiple regex patterns to match various chapter formats
    # Pattern 1: Markdown header with decimal chapter number
    # Matches: "# Chapter 1", "## Chapter 2: Title", etc.
    CHAPTER_DECIMAL_HEADER = re.compile(
        r'^(#{1,6})\s+Chapter\s+(\d+)(?:[:\s\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 2: Markdown header with Roman numeral chapter number
    # Matches: "# Chapter I", "## Chapter IV: Title", etc.
    CHAPTER_ROMAN_HEADER = re.compile(
        r'^(#{1,6})\s+Chapter\s+([IVXLCDM]+)(?:[:\s\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 3: Plain text decimal chapter (no markdown header)
    # Matches: "Chapter 1", "Chapter 2: Title", "CHAPTER 1", etc.
    CHAPTER_DECIMAL_PLAIN = re.compile(
        r'^Chapter\s+(\d+)(?:\s*[:\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 4: Plain text Roman numeral chapter
    # Matches: "Chapter I", "Chapter IV: Title", etc.
    CHAPTER_ROMAN_PLAIN = re.compile(
        r'^Chapter\s+([IVXLCDM]+)(?:\s*[:\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 5: Prologue (markdown header)
    # Matches: "# Prologue", "## Prologue: Beginning", etc.
    PROLOGUE_HEADER = re.compile(
        r'^(#{1,6})\s+(Prologue|Prolog)(?:[:\s\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 6: Prologue (plain text)
    # Matches: "Prologue", "PROLOGUE", "Prolog", etc.
    PROLOGUE_PLAIN = re.compile(
        r'^(Prologue|Prolog)(?:\s*[:\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 7: Epilogue (markdown header)
    # Matches: "# Epilogue", "## Epilogue: End", etc.
    EPILOGUE_HEADER = re.compile(
        r'^(#{1,6})\s+(Epilogue|Epilog)(?:[:\s\-].*)?$',
        re.IGNORECASE
    )

    # Pattern 8: Epilogue (plain text)
    # Matches: "Epilogue", "EPILOGUE", "Epilog", etc.
    EPILOGUE_PLAIN = re.compile(
        r'^(Epilogue|Epilog)(?:\s*[:\-].*)?$',
        re.IGNORECASE
    )

    def __init__(self, input_file: str, output_dir: Optional[str] = None, dry_run: bool = False, overwrite: bool = False):
        """
        Initialize the chapter splitter.

        Args:
            input_file: Path to the input markdown file
            output_dir: Directory to save chapter files (default: same as input file)
            dry_run: If True, only show what would be done without creating files
            overwrite: If True, overwrite existing chapter files; if False, skip existing files
        """
        self.input_file = Path(input_file)

        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = self.input_file.parent

        self.dry_run = dry_run
        self.overwrite = overwrite
        self.chapter_counts: Dict[int, int] = {}  # Track duplicate chapter numbers
        self.chapters_found: List[tuple] = []  # (chapter_num, filename, line_count)
        self.chapters_skipped: List[tuple] = []  # (chapter_num, filename, reason)
        self.prologue_count = 0  # Track multiple prologues
        self.epilogue_count = 0  # Track multiple epilogues

    def detect_section(self, line: str) -> Optional[Tuple[str, int]]:
        """
        Detect if a line is a chapter, prologue, or epilogue.

        Args:
            line: The line to check

        Returns:
            Tuple of (section_type, chapter_num) where:
            - section_type is 'chapter', 'prologue', or 'epilogue'
            - chapter_num is the chapter number (or -1 for prologue, -2 for epilogue)
            Returns None if no match found.
        """
        line = line.rstrip()

        # Check for decimal chapter (header format)
        match = self.CHAPTER_DECIMAL_HEADER.match(line)
        if match:
            chapter_num = int(match.group(2))
            return ('chapter', chapter_num)

        # Check for Roman numeral chapter (header format)
        match = self.CHAPTER_ROMAN_HEADER.match(line)
        if match:
            roman = match.group(2)
            chapter_num = roman_to_int(roman)
            if chapter_num is not None:
                return ('chapter', chapter_num)

        # Check for decimal chapter (plain text format)
        match = self.CHAPTER_DECIMAL_PLAIN.match(line)
        if match:
            chapter_num = int(match.group(1))
            return ('chapter', chapter_num)

        # Check for Roman numeral chapter (plain text format)
        match = self.CHAPTER_ROMAN_PLAIN.match(line)
        if match:
            roman = match.group(1)
            chapter_num = roman_to_int(roman)
            if chapter_num is not None:
                return ('chapter', chapter_num)

        # Check for prologue (header format)
        if self.PROLOGUE_HEADER.match(line):
            return ('prologue', -1)

        # Check for prologue (plain text format)
        if self.PROLOGUE_PLAIN.match(line):
            return ('prologue', -1)

        # Check for epilogue (header format)
        if self.EPILOGUE_HEADER.match(line):
            return ('epilogue', -2)

        # Check for epilogue (plain text format)
        if self.EPILOGUE_PLAIN.match(line):
            return ('epilogue', -2)

        return None

    def get_chapter_filename(self, section_type: str, chapter_num: int) -> str:
        """
        Generate filename for a chapter/prologue/epilogue, handling duplicates.

        Args:
            section_type: 'chapter', 'prologue', or 'epilogue'
            chapter_num: The chapter number (or -1 for prologue, -2 for epilogue)

        Returns:
            Filename for the section (e.g., "chapter_1.md", "prologue.md", "epilogue_A.md")
        """
        if section_type == 'prologue':
            if self.prologue_count == 0:
                self.prologue_count += 1
                return "prologue.md"
            else:
                self.prologue_count += 1
                suffix = chr(ord('A') + self.prologue_count - 2)
                return f"prologue_{suffix}.md"

        elif section_type == 'epilogue':
            if self.epilogue_count == 0:
                self.epilogue_count += 1
                return "epilogue.md"
            else:
                self.epilogue_count += 1
                suffix = chr(ord('A') + self.epilogue_count - 2)
                return f"epilogue_{suffix}.md"

        else:  # chapter
            if chapter_num not in self.chapter_counts:
                self.chapter_counts[chapter_num] = 0
                return f"chapter_{chapter_num}.md"
            else:
                self.chapter_counts[chapter_num] += 1
                suffix = chr(ord('A') + self.chapter_counts[chapter_num] - 1)
                return f"chapter_{chapter_num}_{suffix}.md"

    def split(self) -> tuple:
        """
        Split the input file by chapters, prologues, and epilogues.

        Returns:
            Tuple of (sections_processed, sections_written)
        """
        current_section_type: Optional[str] = None
        current_chapter_num: Optional[int] = None
        current_section_file: Optional[Path] = None
        current_section_lines: List[str] = []
        preamble_lines: List[str] = []  # Content before first section
        sections_processed = 0

        with open(self.input_file, 'r', encoding='utf-8-sig') as f:
            for line_num, line in enumerate(f, 1):
                section_info = self.detect_section(line)

                if section_info:
                    # Save previous section if exists
                    if current_section_type is not None:
                        self._write_section(
                            current_section_file,
                            current_section_lines,
                            current_section_type,
                            current_chapter_num
                        )

                    # Start new section
                    section_type, chapter_num = section_info
                    filename = self.get_chapter_filename(section_type, chapter_num)
                    current_section_file = self.output_dir / filename
                    current_section_type = section_type
                    current_chapter_num = chapter_num
                    current_section_lines = [line]
                    sections_processed += 1

                    # Print appropriate message based on section type
                    if section_type == 'prologue':
                        print(f"Found Prologue at line {line_num} → {filename}")
                    elif section_type == 'epilogue':
                        print(f"Found Epilogue at line {line_num} → {filename}")
                    else:
                        print(f"Found Chapter {chapter_num} at line {line_num} → {filename}")

                else:
                    # Add line to current section or preamble
                    if current_section_type is not None:
                        current_section_lines.append(line)
                    else:
                        preamble_lines.append(line)

        # Write final section
        if current_section_type is not None:
            self._write_section(
                current_section_file,
                current_section_lines,
                current_section_type,
                current_chapter_num
            )

        # Handle preamble (content before first section)
        if preamble_lines and not self.dry_run:
            preamble_file = self.output_dir / "preamble.md"
            print(f"\nWriting preamble ({len(preamble_lines)} lines) → {preamble_file.name}")
            with open(preamble_file, 'w', encoding='utf-8') as f:
                f.writelines(preamble_lines)

        return (sections_processed, len(self.chapters_found))

    def _write_section(self, filepath: Path, lines: List[str], section_type: str, chapter_num: int):
        """Write section content to file (chapter, prologue, or epilogue)."""
        # Check if file exists and overwrite is disabled
        if filepath.exists() and not self.overwrite:
            if self.dry_run:
                print(f"  → Would skip {len(lines)} lines to {filepath.name} (already exists)")
            else:
                print(f"  → Skipping {filepath.name} (already exists)")
            self.chapters_skipped.append((chapter_num, filepath.name, "already exists"))
            return

        self.chapters_found.append((chapter_num, filepath.name, len(lines)))

        if self.dry_run:
            print(f"  → Would write {len(lines)} lines to {filepath.name}")
            return

        # Create output directory if needed
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"  → Wrote {len(lines)} lines to {filepath.name}")

    def print_summary(self):
        """Print summary of chapters found."""
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output directory: {self.output_dir}")
        print(f"Chapters written: {len(self.chapters_found)}")

        if self.chapters_skipped:
            print(f"Chapters skipped: {len(self.chapters_skipped)}")

        if self.chapters_found:
            print("\nChapter files written:")
            for chapter_num, filename, line_count in self.chapters_found:
                print(f"  Chapter {chapter_num:2d} → {filename:20s} ({line_count:4d} lines)")

        if self.chapters_skipped:
            print("\nChapter files skipped:")
            for chapter_num, filename, reason in self.chapters_skipped:
                print(f"  Chapter {chapter_num:2d} → {filename:20s} ({reason})")

        # Show duplicate warnings
        duplicates = {num: count for num, count in self.chapter_counts.items() if count > 0}
        if duplicates:
            print("\n⚠️  Duplicate chapter numbers found:")
            for chapter_num, count in sorted(duplicates.items()):
                print(f"  Chapter {chapter_num} appeared {count + 1} times")

        if self.dry_run:
            print("\n(DRY RUN - No files were created)")


def main():
    parser = argparse.ArgumentParser(
        description="Split markdown documents into separate files by chapter, prologue, and epilogue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s book.md
  %(prog)s book.md -o chapters/
  %(prog)s book.md --dry-run
  %(prog)s plaintext_book.txt -o output/

Supported formats:
  Markdown headers:
    # Prologue
    # Chapter 1
    # Chapter I: The Beginning
    ## Chapter 2 - Middle
    # Epilogue

  Plain text (no # prefix):
    Prologue
    Chapter 1
    Chapter I: The Beginning
    Chapter 2 - Middle
    Epilogue

  Roman numerals supported: I, II, III, IV, V, etc.
  Prologue variations: Prologue, Prolog
  Epilogue variations: Epilogue, Epilog

Output files:
  prologue.md
  chapter_1.md
  chapter_2.md
  epilogue.md

Duplicate sections get suffixes:
  chapter_1_A.md, chapter_1_B.md
  prologue_A.md, prologue_B.md
        """
    )

    parser.add_argument(
        'input_file',
        help='Input file to split (markdown or plain text)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory for chapter files (default: same as input file)',
        default=None
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without creating files'
    )

    parser.add_argument(
        '--overwrite-existing',
        action='store_true',
        help='Overwrite existing chapter files (default: skip existing files)'
    )

    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    args = parser.parse_args()

    try:
        splitter = ChapterSplitter(
            args.input_file,
            args.output_dir,
            args.dry_run,
            args.overwrite_existing
        )

        sections_processed, sections_written = splitter.split()
        splitter.print_summary()

        if sections_processed == 0:
            print("\n⚠️  No chapters, prologues, or epilogues found in the input file!")
            sys.exit(1)

        sys.exit(0)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
