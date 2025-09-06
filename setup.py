#!/usr/bin/env python3
"""
Setup script for OpenRouter Interface.

This is a backup setup.py for systems that don't support pyproject.toml.
The canonical configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
import os

# Read version from package
def get_version():
    version_file = os.path.join("src", "openrouter_interface", "__init__.py")
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

# Read long description from README
def get_long_description():
    readme_path = os.path.join("docs", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A comprehensive tool for executing JSON prompts using the OpenRouter API"

setup(
    name="openrouter-interface",
    version=get_version(),
    description="A comprehensive tool for executing JSON prompts using the OpenRouter API",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="OpenRouter Interface Team",
    python_requires=">=3.7",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
        "pathlib2; python_version<'3.4'",
    ],
    
    extras_require={
        "web": [
            "flask>=2.0.0",
            "werkzeug>=2.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8", 
            "mypy",
            "tox",
        ],
        "all": [
            "flask>=2.0.0",
            "werkzeug>=2.0.0",
            "pytest>=6.0",
            "pytest-cov", 
            "black",
            "flake8",
            "mypy",
            "tox",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "openrouter-runner=openrouter_interface.cli:main",
            "openrouter-web=openrouter_interface.web:main",
            "openrouter-chain=openrouter_interface.chain:main",
            "bookgen=openrouter_interface.bookgen:main",
        ],
    },
    
    package_data={
        "openrouter_interface": [
            "templates/*.html",
            "static/*.css", 
            "static/*.js",
        ],
    },
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    
    keywords=[
        "openrouter", "ai", "llm", "prompt", "cli", "web", "automation",
        "claude", "gpt", "gemini", "api", "processing"
    ],
)