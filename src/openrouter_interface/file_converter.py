#!/usr/bin/env python3
"""
File Converter Module for OpenRouter Interface

Handles document format conversions using pypandoc.
Supports conversion to/from markdown for various formats (docx, pdf, epub, etc.)
"""

import logging
import os
from pathlib import Path
from typing import Optional, List


class FileConverter:
    """Handles file format conversions using pypandoc."""

    # Supported input formats that can be converted to markdown
    SUPPORTED_INPUT_FORMATS = [
        'docx', 'odt', 'rtf', 'html', 'epub', 'txt', 'pdf',
        'latex', 'tex', 'rst', 'org', 'mediawiki'
    ]

    # Supported output formats that can be created from markdown
    SUPPORTED_OUTPUT_FORMATS = [
        'docx', 'odt', 'rtf', 'html', 'epub', 'pdf', 'txt',
        'latex', 'tex', 'rst', 'org', 'mediawiki'
    ]

    def __init__(self):
        """Initialize the file converter."""
        self.pypandoc_available = False
        self.pandoc_available = False
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if pypandoc and pandoc are available."""
        try:
            import pypandoc
            self.pypandoc_available = True

            # Check if pandoc is installed
            try:
                pypandoc.get_pandoc_version()
                self.pandoc_available = True
                logging.info(f"Pandoc version: {pypandoc.get_pandoc_version()}")
            except Exception as e:
                logging.warning(f"pypandoc is installed but pandoc binary not found: {e}")
                logging.warning("Install pandoc: https://pandoc.org/installing.html")

        except ImportError:
            logging.warning("pypandoc not installed. File conversion features disabled.")
            logging.warning("Install with: pip install pypandoc")

    def is_available(self) -> bool:
        """Check if conversion functionality is available."""
        return self.pypandoc_available and self.pandoc_available

    def detect_format(self, file_path: Path) -> Optional[str]:
        """
        Detect file format from extension.

        Args:
            file_path: Path to the file

        Returns:
            Format string (e.g., 'docx', 'pdf') or None if unknown
        """
        suffix = file_path.suffix.lower().lstrip('.')
        if suffix in self.SUPPORTED_INPUT_FORMATS:
            return suffix
        return None

    def convert_to_markdown(self, input_file: Path, from_format: Optional[str] = None) -> Path:
        """
        Convert a file to markdown format.

        Args:
            input_file: Path to input file
            from_format: Source format (auto-detected if None)

        Returns:
            Path to the converted markdown file

        Raises:
            Exception: If conversion fails or dependencies not available
        """
        if not self.is_available():
            raise Exception(
                "File conversion not available. "
                "Install pypandoc and pandoc: pip install pypandoc && install pandoc binary"
            )

        # Auto-detect format if not specified
        if from_format is None:
            from_format = self.detect_format(input_file)
            if from_format is None:
                raise Exception(f"Could not detect format for file: {input_file}")

        if from_format not in self.SUPPORTED_INPUT_FORMATS:
            raise Exception(f"Unsupported input format: {from_format}")

        # Create output filename
        output_file = input_file.with_suffix('.md')

        logging.info(f"Converting {input_file.name} ({from_format}) to markdown")

        try:
            import pypandoc

            # Convert to markdown
            pypandoc.convert_file(
                str(input_file),
                'md',
                format=from_format,
                outputfile=str(output_file),
                extra_args=['--wrap=none']  # Preserve line structure
            )

            if not output_file.exists():
                raise Exception(f"Conversion failed: output file not created")

            file_size = output_file.stat().st_size
            logging.info(f"Conversion successful: {output_file.name} ({file_size} bytes)")

            return output_file

        except Exception as e:
            logging.error(f"Conversion to markdown failed: {e}")
            raise Exception(f"Failed to convert {input_file.name} to markdown: {e}")

    def convert_from_markdown(
        self,
        markdown_file: Path,
        to_format: str,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Convert a markdown file to another format.

        Args:
            markdown_file: Path to markdown file
            to_format: Target format (e.g., 'docx', 'pdf', 'epub')
            output_file: Output file path (auto-generated if None)

        Returns:
            Path to the converted file

        Raises:
            Exception: If conversion fails or dependencies not available
        """
        if not self.is_available():
            raise Exception(
                "File conversion not available. "
                "Install pypandoc and pandoc: pip install pypandoc && install pandoc binary"
            )

        if to_format not in self.SUPPORTED_OUTPUT_FORMATS:
            raise Exception(f"Unsupported output format: {to_format}")

        # Generate output filename if not provided
        if output_file is None:
            output_file = markdown_file.with_suffix(f'.{to_format}')

        logging.info(f"Converting {markdown_file.name} to {to_format}")

        try:
            import pypandoc

            # Extra arguments based on format
            extra_args = ['--wrap=none']

            # PDF-specific settings
            if to_format == 'pdf':
                extra_args.extend([
                    '--pdf-engine=xelatex',  # Better Unicode support
                ])

            # Convert from markdown
            pypandoc.convert_file(
                str(markdown_file),
                to_format,
                format='md',
                outputfile=str(output_file),
                extra_args=extra_args
            )

            if not output_file.exists():
                raise Exception(f"Conversion failed: output file not created")

            file_size = output_file.stat().st_size
            logging.info(f"Conversion successful: {output_file.name} ({file_size} bytes)")

            return output_file

        except Exception as e:
            logging.error(f"Conversion from markdown failed: {e}")
            raise Exception(f"Failed to convert {markdown_file.name} to {to_format}: {e}")

    def convert_multiple_formats(
        self,
        markdown_file: Path,
        formats: List[str],
        output_dir: Optional[Path] = None
    ) -> List[Path]:
        """
        Convert a markdown file to multiple formats.

        Args:
            markdown_file: Path to markdown file
            formats: List of target formats
            output_dir: Directory for output files (same as input if None)

        Returns:
            List of paths to converted files

        Raises:
            Exception: If any conversion fails
        """
        if output_dir is None:
            output_dir = markdown_file.parent

        output_files = []
        errors = []

        for fmt in formats:
            try:
                output_file = output_dir / f"{markdown_file.stem}.{fmt}"
                converted_file = self.convert_from_markdown(markdown_file, fmt, output_file)
                output_files.append(converted_file)
            except Exception as e:
                error_msg = f"Failed to convert to {fmt}: {e}"
                logging.error(error_msg)
                errors.append(error_msg)

        if errors:
            raise Exception(f"Some conversions failed: {'; '.join(errors)}")

        return output_files

    def get_supported_formats(self) -> dict:
        """
        Get lists of supported input and output formats.

        Returns:
            Dictionary with 'input' and 'output' format lists
        """
        return {
            'input': self.SUPPORTED_INPUT_FORMATS,
            'output': self.SUPPORTED_OUTPUT_FORMATS
        }