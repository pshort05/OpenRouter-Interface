#!/usr/bin/env python3
"""
Flask Helper Utilities for OpenRouter Prompt Runner

This module contains utility and helper functions extracted from prompt_runner_flask.py.
These standalone functions don't depend on Flask class state and can be used independently.
"""

import socket
from typing import Dict


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Converts byte sizes to appropriate units (B, KB, MB, GB) with one decimal place.

    Args:
        size_bytes: Size in bytes to format

    Returns:
        Human-readable string representation (e.g., "1.5 MB", "256 B")

    Examples:
        >>> format_file_size(0)
        '0 B'
        >>> format_file_size(1024)
        '1.0 KB'
        >>> format_file_size(1536)
        '1.5 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def enhance_prompt_with_system_and_format(full_prompt: str, system_prompt: str, output_format: str) -> str:
    """
    Enhance the prompt with system prompt and output format instructions.

    Prepends system prompt and output format instructions to the main prompt content.
    Supports markdown, json, xml, and text output formats with appropriate instructions.

    Args:
        full_prompt: The main prompt content
        system_prompt: Optional system-level instructions to prepend
        output_format: Desired output format ('markdown', 'json', 'xml', or 'text')

    Returns:
        Enhanced prompt string with system prompt and format instructions prepended

    Examples:
        >>> enhance_prompt_with_system_and_format("Analyze this text", "Be concise", "markdown")
        'SYSTEM: Be concise\\n\\nOUTPUT FORMAT: Please format your response...\\n\\nAnalyze this text'
    """
    enhanced_prompt = ""

    # Add system prompt if provided
    if system_prompt:
        enhanced_prompt += f"SYSTEM: {system_prompt}\n\n"

    # Add output format instructions
    format_instructions = {
        'markdown': "Please format your response in clear, well-structured Markdown with appropriate headers, lists, and formatting for readability.",
        'json': "Please format your response as valid JSON. Use appropriate keys and structure the data logically.",
        'xml': "Please format your response as well-formed XML with appropriate tags and structure.",
        'text': "Please format your response as plain text with clear paragraphs and structure."
    }

    if output_format in format_instructions:
        enhanced_prompt += f"OUTPUT FORMAT: {format_instructions[output_format]}\n\n"

    # Add the original prompt
    enhanced_prompt += full_prompt

    return enhanced_prompt


def get_local_ip() -> str:
    """
    Get the local IP address of the machine.

    Attempts to determine the local IP by connecting to a remote address (8.8.8.8).
    Falls back to localhost (127.0.0.1) if unable to determine the actual local IP.

    Returns:
        Local IP address as a string (e.g., "192.168.1.100" or "127.0.0.1")

    Examples:
        >>> ip = get_local_ip()
        >>> isinstance(ip, str)
        True
        >>> '.' in ip  # All IPs contain dots
        True
    """
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"