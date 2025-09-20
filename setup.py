#!/usr/bin/env python3
"""
Setup script for OpenRouter Interface
This provides better compatibility for pip installs and entry points
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "docs", "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "A comprehensive tool for executing JSON prompts using the OpenRouter API"

setup(
    name="openrouter-interface",
    version="1.0.0",
    description="A comprehensive tool for executing JSON prompts using the OpenRouter API",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="OpenRouter Interface Team",
    license="MIT",
    python_requires=">=3.7",
    
    # Package discovery
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Include package data
    package_data={
        "openrouter_interface": [
            "templates/*.html",
            "static/*.css", 
            "static/*.js",
        ],
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        "requests>=2.25.0",
        "PyYAML>=5.4.0",
    ],
    
    # Optional dependencies
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
    
    # Console scripts / entry points
    entry_points={
        "console_scripts": [
            "openrouter-runner=openrouter_interface.cli:main",
            "openrouter-web=openrouter_interface.web:main",
            "openrouter-chain=openrouter_interface.chain:main",
            "bookgen=openrouter_interface.bookGen:main",
        ],
    },
    
    # Classifiers
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
    
    # URLs
    project_urls={
        "Homepage": "https://github.com/openrouter-interface/openrouter-interface",
        "Documentation": "https://github.com/openrouter-interface/openrouter-interface/blob/main/docs/README.md",
        "Repository": "https://github.com/openrouter-interface/openrouter-interface",
        "Issues": "https://github.com/openrouter-interface/openrouter-interface/issues",
    },
    
    # Keywords
    keywords=[
        "openrouter", "ai", "llm", "prompt", "cli", "web", "automation",
        "claude", "gpt", "gemini", "api", "processing"
    ],
)