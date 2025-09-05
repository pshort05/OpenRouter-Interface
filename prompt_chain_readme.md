# OpenRouter Prompt Chain Runner

A powerful automation wrapper for `prompt_runner.py` that executes multiple prompts in sequence, creating sophisticated document processing pipelines. Perfect for complex AI workflows that require multiple processing steps.

## 🚀 Overview

The Prompt Chain Runner takes a single input document and processes it through 1-99 sequential prompts, where each prompt's output becomes the next prompt's input. This enables complex multi-step AI processing workflows like:

- **Document editing pipelines**: Grammar → Style → Content → Formatting
- **Analysis workflows**: Extract → Analyze → Summarize → Report
- **Content transformation**: Research → Draft → Refine → Polish → Publish
- **Data processing**: Clean → Analyze → Visualize → Interpret

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage Examples](#-usage-examples)
- [File Management](#-file-management)
- [Advanced Usage](#-advanced-usage)
- [Troubleshooting](#-troubleshooting)
- [Best Practices](#-best-practices)

## ✨ Features

### Core Functionality
- **Sequential Processing**: 1-99 prompts executed in order
- **Automatic Chaining**: Output from step N becomes input for step N+1
- **Flexible Configuration**: YAML-based configuration with command-line overrides
- **Unique File Tracking**: Timestamp + UUID naming for all generated files
- **Comprehensive Logging**: Detailed execution logs with step-by-step tracking

### File Management
- **Isolated Execution**: Each run gets unique temporary directory (`temp/inputname_date_pid/`)
- **Shared Temp Directory**: All prompt_runner.py executions use the same temp directory
- **Unique Payload Files**: Each step creates timestamped payload files for debugging
- **Intermediate Files**: All intermediate outputs preserved with descriptive names
- **Complete File History**: Original input, all steps, final output, logs, and API payloads preserved
- **Clean Output**: Final output contains only the result (no metadata)
- **Smart Cleanup**: Optional temporary file cleanup with debug support

### 🆕 Enhanced Features (New!)

#### Multi-File Processing
- **Batch Operations**: Process multiple input files through the same prompt chain
- **Pattern-Based Output**: Generate organized output files using naming patterns
- **Efficient Execution**: Each file processes through all prompts before moving to the next
- **Organized Results**: All files maintained in the same temp directory with clear naming

#### Per-Prompt Configuration
- **Different LLMs per Step**: Use optimal AI model for each processing step
- **Flexible Model Selection**: Claude for creative tasks, GPT-4 for technical, DeepSeek for analysis
- **Configuration Priority**: Step-specific > Global > Default configuration
- **Cost Optimization**: Use appropriate model pricing for each task type

### Error Handling & Monitoring
- **Step Validation**: Each step verified before proceeding to next
- **Timeout Protection**: 5-minute timeout per prompt execution
- **Detailed Error Reporting**: Clear error messages with recovery suggestions
- **Progress Tracking**: Real-time progress reporting and logging

## 📦 Prerequisites

### Required Software
- **Python 3.7+**: Main interpreter
- **prompt_runner.py**: Must be in PATH or current directory
- **OpenRouter API Key**: Set as `OPENROUTER_API_KEY` environment variable

### Required Python Packages
```bash
pip install pyyaml
```

### Required Files
- **prompt_runner.py**: The base prompt execution tool
- **JSON prompt files**: All prompts referenced in configuration
- **Input document**: The initial file to process

## 🛠️ Installation

### 1. Download the Script
```bash
# Download prompt_chain_runner.py to your project directory
wget https://example.com/prompt_chain_runner.py
chmod +x prompt_chain_runner.py
```

### 2. Verify Dependencies
```bash
# Check Python version
python3 --version

# Check required packages
python3 -c "import yaml; print('PyYAML installed')"

# Check prompt_runner.py
python3 prompt_runner.py --help
```

### 3. Set API Key
```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY="your_api_key_here"

# Make it permanent
echo 'export OPENROUTER_API_KEY="your_api_key_here"' >> ~/.bashrc
```

## 🚀 Quick Start

### 1. Create Sample Configuration
```bash
# Generate a sample configuration file
python3 prompt_chain_runner.py --create-sample
```

This creates `prompt_chain_config_sample.yaml`:
```yaml
input_file: input_document.md
output_file: final_output.md
prompts:
    prompt 1: step1_analysis.json
    prompt 2: step2_refinement.json
    prompt 3: step3_finalization.json
```

### 2. Create Your Prompt Files
Create the JSON prompt files referenced in your configuration:

**step1_analysis.json**:
```json
{
  "instruction": "Analyze the following text for grammar and clarity issues",
  "type": "analysis",
  "output_format": "corrected text with inline comments"
}
```

**step2_refinement.json**:
```json
{
  "instruction": "Improve the style and flow of the following text",
  "type": "refinement", 
  "requirements": ["maintain original meaning", "improve readability"]
}
```

### 3. Run Your First Chain
```bash
# Execute the prompt chain
python3 prompt_chain_runner.py -c prompt_chain_config_sample.yaml

# Or with custom input/output
python3 prompt_chain_runner.py -c config.yaml -i my_document.md -o result.md
```

## ⚙️ Configuration

### YAML Configuration Format

```yaml
# Required: Input and output files
input_file: path/to/input.md
output_file: path/to/output.md

# Required: Sequential prompts (numbered 1-99)
prompts:
    prompt 1: first_step.json
    prompt 2: second_step.json
    prompt 3: third_step.json
    # ... up to prompt 99
```

### Configuration Rules

#### Prompt Numbering
- **Sequential**: Must start with `prompt 1` and continue sequentially
- **No gaps**: Cannot skip numbers (1, 2, 3... not 1, 3, 5)
- **Range**: Supports 1-99 prompts maximum
- **Format**: Exactly `prompt N` where N is the step number

#### File Paths
- **Relative or absolute**: Both supported for all file paths
- **Auto-creation**: Output directories created automatically
- **Validation**: All prompt files validated at startup

### Command Line Overrides

```bash
# Override input file
python3 prompt_chain_runner.py -c config.yaml -i different_input.md

# Override output file  
python3 prompt_chain_runner.py -c config.yaml -o different_output.md

# Override both
python3 prompt_chain_runner.py -c config.yaml -i input.md -o output.md
```

## 📝 Usage Examples

### Example 1: Document Editing Pipeline

**Configuration** (`editing_chain.yaml`):
```yaml
input_file: draft_chapter.md
output_file: edited_chapter.md
prompts:
    prompt 1: grammar_check.json
    prompt 2: style_improvement.json
    prompt 3: content_enhancement.json
    prompt 4: final_polish.json
```

**Execution**:
```bash
python3 prompt_chain_runner.py -c editing_chain.yaml
```

**File Flow**:
```
draft_chapter.md 
  → grammar_check.json → temp/step01_grammar_check_20250126_154530_a1b2c3d4.tmp
  → style_improvement.json → temp/step02_style_improvement_20250126_154530_a1b2c3d4.tmp  
  → content_enhancement.json → temp/step03_content_enhancement_20250126_154530_a1b2c3d4.tmp
  → final_polish.json → edited_chapter.md
```

### Example 2: Data Analysis Workflow

**Configuration** (`analysis_chain.yaml`):
```yaml
input_file: raw_survey_data.csv
output_file: analysis_report.md
prompts:
    prompt 1: data_cleanup.json
    prompt 2: statistical_analysis.json
    prompt 3: trend_identification.json
    prompt 4: insight_generation.json
    prompt 5: report_formatting.json
```

**Execution with Custom Output**:
```bash
python3 prompt_chain_runner.py -c analysis_chain.yaml -o quarterly_report.md
```

### Example 3: Content Creation Pipeline

**Configuration** (`content_chain.yaml`):
```yaml
input_file: research_notes.txt
output_file: blog_post.md
prompts:
    prompt 1: outline_creation.json
    prompt 2: draft_writing.json
    prompt 3: fact_checking.json
    prompt 4: seo_optimization.json
    prompt 5: final_formatting.json
```

**Execution with Debug Mode**:
```bash
python3 prompt_chain_runner.py -c content_chain.yaml --keep-temp
```

## 📁 File Management

### Unique Naming Convention

All files use timestamp + execution ID for uniqueness:
- **Format**: `{type}_{timestamp}_{execution_id}.{ext}`
- **Timestamp**: `YYYYMMDD_HHMMSS` (e.g., `20250126_154530`)
- **Execution ID**: 8-character UUID (e.g., `a1b2c3d4`)

### File Structure Example

```
project/
├── temp/
│   └── input_document_20250126_154530_12345/          # Shared temp directory
│       ├── input_document_20250126_154530_12345.log   # Chain runner log
│       ├── original_input_input_document.md           # Original input copy
│       ├── step01_grammar_check.tmp                   # Single file intermediates
│       ├── step02_style_improvement.tmp
│       ├── file01_step01_analysis.tmp                 # Multi-file intermediates
│       ├── file01_step02_refinement.tmp               # (when using multi-file mode)
│       ├── file02_step01_analysis.tmp
│       ├── file02_step02_refinement.tmp
│       ├── final_output_final_output.md               # Final output copy
│       ├── prompt_runner_20250126_154531_12346.payload.json  # API payloads
│       ├── prompt_runner_20250126_154532_12347.payload.json  # (one per execution)
│       └── prompt_runner_20250126_154533_12348.payload.json
├── input_document.md                                   # Your input(s)
├── document2.md                                        # (multi-file mode)
├── document3.txt
├── final_output.md                                     # Final result(s)
├── processed_document2_output.md                      # (multi-file mode)
└── processed_document3_output.txt
```

### Temporary File Management

#### Default Behavior (Cleanup)
```bash
# Temporary files are automatically cleaned up
python3 prompt_chain_runner.py -c config.yaml
# → temp files deleted after successful completion
```

#### Debug Mode (Keep Files)
```bash
# Keep temporary files for debugging
python3 prompt_chain_runner.py -c config.yaml --keep-temp
# → temp files preserved for inspection
```

#### Manual File Inspection
```bash
# View intermediate results
cat temp/prompt_chain_20250126_154530_a1b2c3d4/step02_style_improvement_20250126_154530_a1b2c3d4.tmp

# Compare steps
diff temp/*/step01_*.tmp temp/*/step02_*.tmp

# View API payload for debugging
cat temp/input_document_*/prompt_runner_*.payload.json
```

## ⚙️ Command Line Options

### New Features

#### Configuration Passing
Pass configuration files to each `prompt_runner.py` execution:
```bash
# Use specific model, temperature, etc. for all prompts in the chain
python prompt_chain_runner.py -c chain_config.yaml --prompt-runner-config openrouter_editor.yaml
```

#### File Organization
All files are automatically organized in a shared temporary directory:
```bash
# Standard execution - creates temp/inputname_date_pid/ directory
python prompt_chain_runner.py -c my_chain.yaml -i document.md -o result.md

# Files will be organized as:
# temp/document_20250131_143052_12345/
# ├── document_20250131_143052_12345.log           # Chain log
# ├── original_input_document.md                   # Input copy
# ├── prompt_runner_20250131_143053_12346.payload.json  # Step 1 API payload
# ├── step01_analysis.tmp                          # Step 1 output
# └── final_output_result.md                       # Final output copy
```

#### Debug and Review
Each execution creates unique payload files for debugging:
```bash
# After execution, review what was sent to the API for each step
ls temp/input_*/prompt_runner_*.payload.json
jq . temp/input_*/prompt_runner_20250131_143053_12346.payload.json
```

### 🆕 Enhanced Configuration Examples

#### Multi-File Processing Configuration
Process multiple files through the same prompt sequence:
```yaml
# multi_file_config.yaml
input_files:
  - "document1.md"
  - "document2.md"
  - "document3.txt"
output_pattern: "processed_{input_name}_output{input_ext}"
prompts:
  prompt 1: "analysis.json"
  prompt 2: "refinement.json"
  prompt 3: "polish.json"
```

#### Multi-LLM Configuration
Use different AI models for each processing step:
```yaml
# multi_llm_config.yaml
input_file: "input_document.md"
output_file: "final_processed_document.md"
prompts:
  prompt 1:
    prompt_file: "creative_brainstorm.json"
    config_file: "claude_config.yaml"     # Claude for creative tasks
  prompt 2:
    prompt_file: "technical_analysis.json"
    config_file: "gpt4_config.yaml"      # GPT-4 for technical analysis
  prompt 3:
    prompt_file: "fact_checking.json"
    config_file: "deepseek_config.yaml"  # DeepSeek for fact checking
  prompt 4: "final_editing.json"         # Uses global/default config
```

#### Model Configuration Files
```yaml
# claude_config.yaml
model: anthropic/claude-4-sonnet-20250522
temperature: 0.8
max_tokens: 25000

# gpt4_config.yaml  
model: openai/gpt-4o-2024-11-20
temperature: 0.7
max_tokens: 20000

# deepseek_config.yaml
model: deepseek/deepseek-r1
temperature: 0.5
max_tokens: 15000
```

#### Usage Examples
```bash
# Multi-file processing
python prompt_chain_runner.py -c multi_file_config.yaml

# Multi-LLM single file processing
python prompt_chain_runner.py -c multi_llm_config.yaml

# Combine with global config fallback
python prompt_chain_runner.py -c multi_file_config.yaml --prompt-runner-config default_config.yaml

# Debug multi-file execution
python prompt_chain_runner.py -c multi_file_config.yaml --debug
```

## 🔧 Advanced Usage

### Complex Configuration Examples

#### Multi-Language Processing
```yaml
input_file: document.txt
output_file: processed_document.txt
prompts:
    prompt 1: detect_language.json
    prompt 2: translate_to_english.json
    prompt 3: grammar_correction.json
    prompt 4: style_improvement.json
    prompt 5: translate_back.json
```

#### Scientific Paper Processing
```yaml
input_file: research_draft.md
output_file: publication_ready.md
prompts:
    prompt 1: technical_review.json
    prompt 2: citation_formatting.json
    prompt 3: abstract_optimization.json
    prompt 4: conclusion_strengthening.json
    prompt 5: final_proofreading.json
```

#### Code Documentation Generation
```yaml
input_file: source_code.py
output_file: documentation.md
prompts:
    prompt 1: code_analysis.json
    prompt 2: function_documentation.json
    prompt 3: example_generation.json
    prompt 4: tutorial_creation.json
    prompt 5: markdown_formatting.json
```

### Performance Optimization

#### Timeout Configuration
The default timeout is 5 minutes per step. For longer processing:
```python
# Modify in prompt_chain_runner.py
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=600  # 10 minutes
)
```

#### Parallel Processing
Currently sequential only. For parallel processing of independent documents:
```bash
# Process multiple documents in parallel
python3 prompt_chain_runner.py -c config.yaml -i doc1.md -o result1.md &
python3 prompt_chain_runner.py -c config.yaml -i doc2.md -o result2.md &
python3 prompt_chain_runner.py -c config.yaml -i doc3.md -o result3.md &
wait
```

## 🔍 Monitoring and Logging

### Log File Structure

Each execution creates a detailed log file:
```
prompt_chain_20250126_154530_a1b2c3d4.log
```

### Log Content Example
```
2025-01-26 15:45:30 - INFO - Prompt Chain Runner initialized - Execution ID: a1b2c3d4
2025-01-26 15:45:30 - INFO - Configuration file: editing_chain.yaml
2025-01-26 15:45:30 - INFO - Starting prompt chain execution - 3 prompts
2025-01-26 15:45:30 - INFO - --- Step 1/3 ---
2025-01-26 15:45:30 - INFO - Executing prompt: grammar_check.json
2025-01-26 15:45:30 - DEBUG - Command: python3 prompt_runner.py -p grammar_check.json -i input.md -o temp/step01_grammar_check_20250126_154530_a1b2c3d4.tmp -l prompt_chain_20250126_154530_a1b2c3d4.log
2025-01-26 15:45:32 - INFO - Step 1: SUCCESS - prompt_runner.py completed
2025-01-26 15:45:32 - INFO - Step 1 temp file created: temp/step01_grammar_check_20250126_154530_a1b2c3d4.tmp
2025-01-26 15:45:32 - INFO - Temp file size: 2847 bytes
```

### Real-time Monitoring
```bash
# Monitor execution in real-time
tail -f prompt_chain_20250126_154530_a1b2c3d4.log

# Watch temp directory
watch -n 2 'ls -la temp/prompt_chain_*/'
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Configuration File Not Found
```
Error: Configuration file not found: config.yaml
```
**Solution**: Check file path and existence
```bash
ls -la config.yaml
python3 prompt_chain_runner.py --create-sample
```

#### 2. Invalid Prompt Numbering
```
Error: Prompts must be numbered sequentially starting from 1. Found: [1, 3, 5]
```
**Solution**: Fix prompt numbering in YAML
```yaml
# Wrong
prompts:
    prompt 1: step1.json
    prompt 3: step3.json
    prompt 5: step5.json

# Correct  
prompts:
    prompt 1: step1.json
    prompt 2: step2.json
    prompt 3: step3.json
```

#### 3. Prompt File Not Found
```
Error: Prompt file not found: missing_prompt.json (for prompt 2)
```
**Solution**: Ensure all prompt files exist
```bash
ls -la *.json
# Create missing files or fix paths in config
```

#### 4. API Key Issues
```
Error: API key not found
```
**Solution**: Set OpenRouter API key
```bash
export OPENROUTER_API_KEY="your_api_key_here"
echo $OPENROUTER_API_KEY  # Verify it's set
```

#### 5. Step Execution Failure
```
Step 2: FAILED - prompt_runner.py returned code 1
```
**Solution**: Check individual prompt execution
```bash
# Test the failing prompt manually
python3 prompt_runner.py -p step2.json -i input.md -o test_output.md -v

# Check the detailed log
grep "Step 2" prompt_chain_*.log
```

#### 6. Timeout Issues
```
Step 3: TIMEOUT - prompt_runner.py timed out after 5 minutes
```
**Solution**: Increase timeout or optimize prompts
- Simplify complex prompts
- Reduce input size
- Check API response times

### Debug Mode

Enable detailed debugging:
```bash
# Keep temp files and enable verbose logging
python3 prompt_chain_runner.py -c config.yaml --keep-temp

# Examine temp files
ls -la temp/prompt_chain_*/
cat temp/prompt_chain_*/step*.tmp
```

### Log Analysis

Find issues in logs:
```bash
# Search for errors
grep -i error prompt_chain_*.log

# Check execution times
grep "Step.*completed" prompt_chain_*.log

# View command execution
grep "Command:" prompt_chain_*.log
```

## 💡 Best Practices

### Configuration Management

#### 1. Organized File Structure
```
project/
├── configs/
│   ├── editing_pipeline.yaml
│   ├── analysis_workflow.yaml
│   └── content_creation.yaml
├── prompts/
│   ├── editing/
│   │   ├── grammar_check.json
│   │   └── style_improve.json
│   └── analysis/
│       ├── data_clean.json
│       └── stats_analysis.json
├── inputs/
├── outputs/
└── logs/
```

#### 2. Descriptive Naming
```yaml
# Good: Descriptive prompt names
prompts:
    prompt 1: 01_initial_grammar_check.json
    prompt 2: 02_style_enhancement.json
    prompt 3: 03_content_optimization.json
    prompt 4: 04_final_proofreading.json

# Avoid: Generic names
prompts:
    prompt 1: step1.json
    prompt 2: step2.json
```

#### 3. Version Control
```bash
# Track configurations
git add configs/ prompts/
git commit -m "Add editing pipeline configuration"

# Tag versions
git tag -a v1.0 -m "Stable editing pipeline"
```

### Prompt Design

#### 1. Clear Handoffs
Design prompts that work well in sequence:
```json
{
  "instruction": "Improve the grammar and punctuation in the following text. Preserve all content and structure exactly, only fix grammatical errors.",
  "requirements": [
    "Keep original paragraph structure",
    "Maintain author's voice and style", 
    "Fix only obvious grammar/punctuation errors"
  ]
}
```

#### 2. Consistent Output Format
Ensure each prompt produces compatible output:
```json
{
  "instruction": "Analyze the text and provide improved version",
  "output_format": "Return only the improved text without any commentary or metadata"
}
```

#### 3. Error Recovery
Design prompts to handle various input formats:
```json
{
  "instruction": "Process the following text, handling both markdown and plain text formats appropriately"
}
```

### Execution Management

#### 1. Test Individual Steps
```bash
# Test each prompt individually first
python3 prompt_runner.py -p step1.json -i test_input.md -o test1.md
python3 prompt_runner.py -p step2.json -i test1.md -o test2.md
```

#### 2. Start Small
```yaml
# Begin with 2-3 steps, then expand
prompts:
    prompt 1: basic_cleanup.json
    prompt 2: final_polish.json
```

#### 3. Monitor Progress
```bash
# Use separate terminal for monitoring
tail -f prompt_chain_*.log

# Check intermediate results
head -n 20 temp/prompt_chain_*/step*.tmp
```

### Production Deployment

#### 1. Automated Execution
```bash
#!/bin/bash
# production_pipeline.sh

# Set API key
export OPENROUTER_API_KEY="$PRODUCTION_API_KEY"

# Execute with error handling
if python3 prompt_chain_runner.py -c production_config.yaml -i "$1" -o "$2"; then
    echo "Pipeline completed successfully"
    exit 0
else
    echo "Pipeline failed - check logs"
    exit 1
fi
```

#### 2. Batch Processing
```bash
# Process multiple files
for file in inputs/*.md; do
    basename=$(basename "$file" .md)
    python3 prompt_chain_runner.py -c config.yaml -i "$file" -o "outputs/${basename}_processed.md"
done
```

#### 3. Error Recovery
```bash
# Restart from specific step
cp temp/prompt_chain_*/step02_*.tmp recovery_input.md
python3 prompt_runner.py -p step3.json -i recovery_input.md -o final_output.md
```

---

## 📞 Support

### Getting Help

1. **Check the logs**: Most issues are explained in the execution logs
2. **Test individual components**: Verify `prompt_runner.py` works independently
3. **Validate configuration**: Use `--create-sample` for reference format
4. **Check prerequisites**: Ensure all dependencies are installed

### Common Commands

```bash
# Create sample config
python3 prompt_chain_runner.py --create-sample

# Test with debug mode
python3 prompt_chain_runner.py -c config.yaml --keep-temp

# Check dependencies
python3 -c "import yaml; print('OK')"
python3 prompt_runner.py --help
```

---

**Transform your document processing with powerful AI prompt chains!** 🚀