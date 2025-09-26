# Multi-Prompt Quick Reference

## Command Line Usage

### Single Prompt (Existing)
```bash
openrouter-runner -p prompts/analysis.json -i document.md
```

### Multi-Prompt (NEW)
```bash
# Two prompts
openrouter-runner -p "prompts/quality.json,prompts/grammar.json" -i document.md

# Three prompts
openrouter-runner -p "prompts/analysis.json,prompts/style.json,prompts/polish.json" -i document.md
```

## Chain Configuration

### Single Prompt Chain Step
```yaml
prompt 1: "analysis.json"
```

### Multi-Prompt Chain Step
```yaml
prompt 1:
  name: "comprehensive_analysis"
  prompt_file: "quality.json,grammar.json,style.json"
```

### Mixed Chain
```yaml
prompts:
  prompt 1: "single_analysis.json"                    # Single prompt
  prompt 2:
    name: "multi_enhancement"
    prompt_file: "grammar.json,style.json"           # Multi-prompt
  prompt 3: "final_polish.json"                      # Single prompt
```

## Master System Prompt Structure

When multiple prompts are combined, the system creates:

```
MASTER SYSTEM PROMPT - Combined from Multiple Sources
============================================================

PROMPT SECTION 1: quality.json
----------------------------------------
[Content from quality.json]

PROMPT SECTION 2: grammar.json
----------------------------------------
[Content from grammar.json]

END OF COMBINED PROMPTS
============================================================

Instructions: Apply all the above prompt sections in sequence.
[Additional metadata and your input content]
```

## Use Cases

- **Quality Pipeline**: `quality.json,grammar.json,readability.json`
- **Code Review**: `security.json,performance.json,style.json`
- **Content Enhancement**: `analysis.json,improvement.json,polish.json`
- **Creative Writing**: `plot.json,character.json,dialogue.json`

## Key Benefits

- **Comprehensive Processing**: Combine multiple specialized prompts
- **Single API Call**: More efficient than sequential individual calls
- **Structured Output**: Clear organization of different prompt requirements
- **Flexible Configuration**: Mix single and multi-prompt steps as needed