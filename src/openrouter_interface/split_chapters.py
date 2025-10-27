#!/usr/bin/env python3
"""
Chapter Splitter - Split markdown documents into separate files by chapter

This utility reads a markdown file and splits it into separate files based on
chapter headings (e.g., "# Chapter 1", "## Chapter 2", etc.).

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
from typing import Dict, List, Optional


class ChapterSplitter:
    """Splits markdown documents by chapter headings."""

    # Regex pattern to match chapter headings at any level
    # Matches: "# Chapter 1", "## Chapter 2: Title", etc.
    CHAPTER_PATTERN = re.compile(
        r'^(#{1,6})\s+Chapter\s+(\d+)(?:[:\s].*)?$',
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

    def get_chapter_filename(self, chapter_num: int) -> str:
        """
        Generate filename for a chapter, handling duplicates with A, B, C suffixes.

        Args:
            chapter_num: The chapter number

        Returns:
            Filename for the chapter (e.g., "chapter_1.md", "chapter_1_A.md")
        """
        if chapter_num not in self.chapter_counts:
            self.chapter_counts[chapter_num] = 0
            return f"chapter_{chapter_num}.md"
        else:
            self.chapter_counts[chapter_num] += 1
            suffix = chr(ord('A') + self.chapter_counts[chapter_num] - 1)
            return f"chapter_{chapter_num}_{suffix}.md"

    def split(self) -> tuple:
        """
        Split the input file by chapters.

        Returns:
            Tuple of (chapters_processed, chapters_written)
        """
        current_chapter_num: Optional[int] = None
        current_chapter_file: Optional[Path] = None
        current_chapter_lines: List[str] = []
        preamble_lines: List[str] = []  # Content before first chapter
        chapters_processed = 0

        with open(self.input_file, 'r', encoding='utf-8-sig') as f:
            for line_num, line in enumerate(f, 1):
                match = self.CHAPTER_PATTERN.match(line.rstrip())

                if match:
                    # Save previous chapter if exists
                    if current_chapter_num is not None:
                        self._write_chapter(
                            current_chapter_file,
                            current_chapter_lines,
                            current_chapter_num
                        )

                    # Start new chapter
                    chapter_num = int(match.group(2))
                    filename = self.get_chapter_filename(chapter_num)
                    current_chapter_file = self.output_dir / filename
                    current_chapter_num = chapter_num
                    current_chapter_lines = [line]
                    chapters_processed += 1

                    print(f"Found Chapter {chapter_num} at line {line_num} → {filename}")

                else:
                    # Add line to current chapter or preamble
                    if current_chapter_num is not None:
                        current_chapter_lines.append(line)
                    else:
                        preamble_lines.append(line)

        # Write final chapter
        if current_chapter_num is not None:
            self._write_chapter(
                current_chapter_file,
                current_chapter_lines,
                current_chapter_num
            )

        # Handle preamble (content before first chapter)
        if preamble_lines and not self.dry_run:
            preamble_file = self.output_dir / "preamble.md"
            print(f"\nWriting preamble ({len(preamble_lines)} lines) → {preamble_file.name}")
            with open(preamble_file, 'w', encoding='utf-8') as f:
                f.writelines(preamble_lines)

        return (chapters_processed, len(self.chapters_found))

    def _write_chapter(self, filepath: Path, lines: List[str], chapter_num: int):
        """Write chapter content to file."""
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
        description="Split markdown documents into separate files by chapter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s book.md
  %(prog)s book.md -o chapters/
  %(prog)s book.md --dry-run

The utility will detect chapter headings like:
  # Chapter 1
  ## Chapter 2: The Beginning
  ### Chapter 3 - Introduction

And create files like:
  chapter_1.md
  chapter_2.md
  chapter_3.md

Duplicate chapters get suffixes:
  chapter_1_A.md
  chapter_1_B.md
        """
    )

    parser.add_argument(
        'input_file',
        help='Input markdown file to split'
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

        chapters_processed, chapters_written = splitter.split()
        splitter.print_summary()

        if chapters_processed == 0:
            print("\n⚠️  No chapters found in the input file!")
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
