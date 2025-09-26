# Multi-Prompt Processing Guide

## Overview

The OpenRouter Interface supports combining multiple JSON prompt files into a single master system prompt, enabling sophisticated AI processing workflows that leverage multiple specialized prompts simultaneously.

## Features

- **Flexible Combination**: Mix and match any number of prompt files
- **Master System Prompt**: Automatically creates structured combined prompts
- **Chain Integration**: Use multi-prompts in chain operations
- **Backward Compatible**: Single prompts continue to work unchanged
- **Per-Step Configuration**: Each chain step can have different prompt combinations

## Basic Usage

### Command Line Interface

```bash
# Single prompt (existing functionality)
openrouter-runner -p prompts/analysis.json -i document.md

# Multiple prompts combined
openrouter-runner -p "prompts/quality.json,prompts/grammar.json" -i document.md

# Three or more prompts
openrouter-runner -p "prompts/analysis.json,prompts/style.json,prompts/polish.json" -i document.md
```

### Chain Configuration

```yaml
# config/multi_prompt_chain.yaml
input_file: manuscript.md
output_file: enhanced_output.md

prompts:
  # Step 1: Single prompt
  prompt 1:
    name: "initial_analysis"
    prompt_file: "prompts/content_analysis.json"

  # Step 2: Combine two prompts
  prompt 2:
    name: "quality_and_grammar"
    prompt_file: "prompts/quality_check.json,prompts/grammar_fix.json"

  # Step 3: Combine three prompts
  prompt 3:
    name: "comprehensive_enhancement"
    prompt_file: "prompts/style.json,prompts/clarity.json,prompts/readability.json"
```

## How It Works

### 1. Prompt Combination Process

When multiple prompts are specified:

1. **Validation**: Each prompt file is validated individually
2. **Loading**: All prompt files are loaded and parsed
3. **Combination**: Prompts are combined into a structured master prompt
4. **Processing**: The AI model receives the master prompt with your content

### 2. Master System Prompt Structure

The system creates a structured prompt:

```
MASTER SYSTEM PROMPT - Combined from Multiple Sources
============================================================

PROMPT SECTION 1: quality_check.json
----------------------------------------
You are a content quality evaluator. Analyze the text for...
[Full content from first prompt]

PROMPT SECTION 2: grammar_fix.json
----------------------------------------
You are a grammar and style editor. Focus on correcting...
[Full content from second prompt]

PROMPT SECTION 3: readability.json
----------------------------------------
You are a readability specialist. Improve clarity and...
[Full content from third prompt]

END OF COMBINED PROMPTS
============================================================

Instructions: Apply all the above prompt sections in sequence to the provided input content.
Each section should be considered as contributing to the overall task requirements.

[Additional metadata from individual prompts]

Input content to process:
[Your actual content here]
```

### 3. Metadata Handling

- **Personas**: Combined from all prompts (first prompt takes precedence)
- **Evaluation Directives**: Merged from all sources
- **Review Criteria**: Combined into comprehensive criteria
- **Output Formats**: Consolidated requirements
- **Source Tracking**: System notes which files were combined

## Use Cases and Examples

### Content Enhancement Pipeline

```bash
# Combine quality analysis, grammar checking, and style improvement
openrouter-runner -p "prompts/quality_analysis.json,prompts/grammar_check.json,prompts/style_guide.json" -i article.md -o enhanced_article.md
```

**Prompt Files:**
- `quality_analysis.json`: Evaluates content structure and clarity
- `grammar_check.json`: Fixes grammatical errors and typos
- `style_guide.json`: Improves writing style and flow

### Code Review Workflow

```bash
# Security analysis + performance review + style checking
openrouter-runner -p "prompts/security_audit.json,prompts/performance_review.json,prompts/code_style.json" -i code.py -o reviewed_code.py
```

### Document Processing Chain

```yaml
input_file: technical_document.md
output_file: publication_ready.md

prompts:
  prompt 1:
    name: "technical_accuracy"
    prompt_file: "prompts/technical_review.json,prompts/fact_check.json"

  prompt 2:
    name: "readability_enhancement"
    prompt_file: "prompts/clarity_check.json,prompts/audience_adaptation.json"

  prompt 3:
    name: "final_polish"
    prompt_file: "prompts/formatting.json,prompts/publication_standards.json"
```

### Creative Writing Enhancement

```yaml
prompts:
  prompt 1:
    name: "story_analysis"
    prompt_file: "prompts/plot_structure.json,prompts/character_development.json"

  prompt 2:
    name: "dialogue_and_style"
    prompt_file: "prompts/dialogue_enhancement.json,prompts/prose_style.json"

  prompt 3:
    name: "final_editing"
    prompt_file: "prompts/line_editing.json,prompts/copyediting.json"
```

## Advanced Configuration

### Per-Step Models with Multi-Prompts

```yaml
prompts:
  prompt 1:
    name: "analysis_phase"
    prompt_file: "prompts/deep_analysis.json,prompts/structure_review.json"
    model: "anthropic/claude-4-sonnet-20250522"

  prompt 2:
    name: "creative_phase"
    prompt_file: "prompts/creative_enhancement.json,prompts/style_improvement.json"
    model: "openai/gpt-4o-2024-11-20"

  prompt 3:
    name: "technical_phase"
    prompt_file: "prompts/technical_accuracy.json"
    model: "google/gemini-2.5-pro-exp-03-25"
```

### Multiple File Processing with Multi-Prompts

```yaml
input_files:
  - chapter1.md
  - chapter2.md
  - chapter3.md

output_pattern: "enhanced_{input_name}{input_ext}"

prompts:
  prompt 1:
    name: "comprehensive_review"
    prompt_file: "prompts/content_review.json,prompts/consistency_check.json,prompts/style_alignment.json"
```

## Best Practices

### 1. Prompt Selection

- **Complementary Prompts**: Choose prompts that work well together
- **Avoid Conflicts**: Ensure prompts don't have contradictory instructions
- **Logical Order**: Arrange prompts in a logical processing sequence

### 2. Prompt Design

When creating prompts for multi-prompt use:

```json
{
  "instruction": "You are a [specific role]. Focus on [specific aspect] of the content.",
  "persona": "[specific expertise]",
  "evaluation_directives": {
    "primary_focus": "[what this prompt specializes in]"
  },
  "output_format": "Provide [specific type of output] while maintaining overall text coherence."
}
```

### 3. Chain Design

- **Progressive Enhancement**: Start with analysis, then improvement, then polish
- **Balanced Steps**: Don't overload early steps with too many prompts
- **Validation Points**: Include single-prompt steps for focused validation

### 4. Performance Considerations

- **Token Limits**: More prompts = longer master prompt (monitor token usage)
- **Processing Time**: Combined prompts may take longer to process
- **Cost Management**: Multi-prompts consume more tokens per request

## Troubleshooting

### Common Issues

1. **Prompt File Not Found**
   ```
   Error: Prompt file not found: prompts/missing_file.json
   ```
   **Solution**: Verify all files in comma-separated list exist

2. **Conflicting Instructions**
   ```
   Output may show mixed or conflicting guidance
   ```
   **Solution**: Review prompts for contradictory instructions

3. **Token Limit Exceeded**
   ```
   Error: Request exceeds model token limit
   ```
   **Solution**: Reduce number of prompts or use model with higher limits

### Validation

The system validates:
- ✅ All prompt files exist and are readable
- ✅ Each prompt file contains valid JSON
- ✅ Required prompt fields are present
- ✅ File paths are correctly formatted

### Debug Mode

Use verbose logging to see how prompts are combined:

```bash
openrouter-runner -p "prompt1.json,prompt2.json" -i input.md -v
```

## Migration Guide

### From Single to Multi-Prompt

**Before:**
```bash
openrouter-runner -p analysis.json -i document.md
# Then separately:
openrouter-runner -p grammar.json -i document.md
# Then separately:
openrouter-runner -p style.json -i document.md
```

**After:**
```bash
openrouter-runner -p "analysis.json,grammar.json,style.json" -i document.md
```

### Chain Migration

**Before:**
```yaml
prompts:
  prompt 1: analysis.json
  prompt 2: grammar.json
  prompt 3: style.json
```

**After (optional):**
```yaml
prompts:
  prompt 1:
    name: "comprehensive_enhancement"
    prompt_file: "analysis.json,grammar.json,style.json"
```

## API Integration

### Python API

```python
from openrouter_interface import PromptRunner

runner = PromptRunner()

# Multi-prompt processing
success = runner.run_batch_mode(
    "quality.json,grammar.json,style.json",
    "document.md"
)
```

### Web Interface

The web interface supports multi-prompt selection through:
- File upload with comma-separated naming
- Chain builder with multi-prompt step configuration
- Prompt combination interface (future enhancement)

## Examples Repository

Complete working examples available in:
- `examples/multi_prompt_basic.yaml`
- `examples/multi_prompt_chain.yaml`
- `examples/multi_prompt_advanced.yaml`

## Support

For questions about multi-prompt functionality:
1. Check the troubleshooting section above
2. Review example configurations
3. Enable verbose logging for debugging
4. Report issues via GitHub issues with multi-prompt label