# OpenRouter Interface

## Project Overview

This project, `openrouter-interface`, is a comprehensive Python toolkit for interacting with the OpenRouter API. It provides a command-line interface (CLI), a web interface, and a programmatic API for executing prompts against a wide range of AI models.

The project is designed to support complex workflows, including:

*   **Prompt Chaining:** Executing a series of prompts in sequence, with the output of one prompt serving as the input for the next.
*   **File Conversion:** Converting files between different formats (e.g., docx to markdown) before and after processing.
*   **Pre/Post-processing Scripts:** Executing custom scripts before and after the entire chain, as well as before and after each individual prompt.
*   **Web Interface:** A Flask-based web application that provides a user-friendly way to interact with the core functionalities of the application.

The project is built using Python and relies on a few key libraries, including `requests` for making API calls, `PyYAML` for configuration management, and `Flask` for the web interface.

## Building and Running

The project uses standard Python packaging tools (`setuptools` and `pip`) for building and distribution.

### Installation

To install the project and its dependencies, run the following command:

```bash
./install-global.sh
```

This will install the necessary packages and create the command-line entry points.

### Running the Application

The project provides three main entry points:

*   `openrouter-runner`: A command-line tool for executing single prompts.
*   `openrouter-chain`: A command-line tool for executing prompt chains.
*   `openrouter-web`: A web interface for interacting with the application.

To run the `openrouter-runner` in interactive mode, use the following command:

```bash
openrouter-runner
```

To run the `openrouter-chain`, you need to provide a YAML configuration file:

```bash
openrouter-chain -c my_chain_config.yaml
```

To start the web interface, use the following command:

```bash
openrouter-web
```

The web interface will be available at `http://localhost:5000`.

### Testing

The project uses `pytest` for testing. to run the test suite, use the following command:

```bash
pytest
```

## Development Conventions

The project follows standard Python development conventions.

### Code Style

The project uses `black` for code formatting and `flake8` for linting. to format the code and check for linting errors, use the following commands:

```bash
black src tests
flake8 src
```

### Type Checking

The project uses `mypy` for static type checking. to run the type checker, use the following command:

```bash
mypy src
```

### Contributing

Contributions are welcome! Please follow the standard GitHub flow for submitting pull requests.
