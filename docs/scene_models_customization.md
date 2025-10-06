# Scene Generator Model Customization

The Scene/Chapter Generator uses a customizable model configuration file to define available LLM models in the dropdown menu.

## Configuration File Location

After installation, the model configuration file is located at:
```
src/openrouter_interface/scene_models.yaml
```

For global installations, it's typically found at:
```
~/.local/lib/python3.X/site-packages/openrouter_interface/scene_models.yaml
```

## Configuration Format

The YAML file defines a list of models with the following structure:

```yaml
models:
  - name: "Display Name"
    id: "provider/model-id"
    description: "Brief description shown to users"
    default: true  # Optional: marks this as the default selected model
```

### Fields Explained

- **name** (required): The display name shown in the dropdown menu
- **id** (required): The OpenRouter model identifier (e.g., `anthropic/claude-4-sonnet-20250522`)
- **description** (optional): A brief description shown below the dropdown when the model is selected
- **default** (optional): Set to `true` to make this the default selected model (only one model should have this)

## Example Configuration

```yaml
models:
  - name: "Claude 4.5 Sonnet"
    id: "anthropic/claude-4-sonnet-20250522"
    description: "Latest Claude 4.5 - Best for creative writing"
    default: true

  - name: "Claude 4.1 Opus"
    id: "anthropic/claude-opus-4.1"
    description: "Most capable Claude model - Superior reasoning and creativity"

  - name: "Gemini 2.5 Pro"
    id: "google/gemini-2.5-pro-latest"
    description: "Google's latest and most capable model"

  - name: "GPT-4o"
    id: "openai/gpt-4o"
    description: "Latest OpenAI multimodal model"
```

## Adding New Models

When new models are released on OpenRouter, simply edit the `scene_models.yaml` file:

1. Add a new entry to the `models` list
2. Provide the model's OpenRouter ID (check https://openrouter.ai/models)
3. Add a descriptive name and description
4. Save the file
5. Restart the web server

## Finding Model IDs

To find the correct model ID for OpenRouter:

1. Visit https://openrouter.ai/models
2. Find the model you want to add
3. Copy the model ID (format: `provider/model-name`)
4. Add it to your configuration file

## Common Model Providers

- **Anthropic**: `anthropic/` (Claude models)
- **OpenAI**: `openai/` (GPT models)
- **Google**: `google/` (Gemini models)
- **Meta**: `meta-llama/` (Llama models)
- **Mistral**: `mistralai/` (Mistral models)
- **DeepSeek**: `deepseek/` (DeepSeek models)

## Removing Models

To remove a model from the dropdown, simply delete its entry from the YAML file or comment it out:

```yaml
# Commented out model won't appear in dropdown
#  - name: "Old Model"
#    id: "provider/old-model"
```

## Fallback Behavior

If the `scene_models.yaml` file cannot be loaded (missing, invalid YAML, etc.), the system will fall back to a default set of hardcoded models to ensure the Scene Generator continues to work.

## Validation

The system will:
- Log a warning if the configuration file is not found
- Log an error if the YAML is invalid
- Use fallback models if loading fails
- Continue to function even if the configuration has issues

## Tips

1. **Keep It Organized**: Order models by preference or capability
2. **Update Regularly**: As new models are released, update the configuration
3. **Test Changes**: After editing, reload the Scene Generator page to verify changes
4. **Backup**: Keep a backup of your customized configuration
5. **Model Availability**: Ensure models you add are actually available on your OpenRouter account

## Example: Adding Claude 4.1 Opus

```yaml
models:
  # Add the new model
  - name: "Claude 4.1 Opus"
    id: "anthropic/claude-opus-4.1"
    description: "Most capable Claude model with superior reasoning"

  # Keep existing models
  - name: "Claude 4.5 Sonnet"
    id: "anthropic/claude-4-sonnet-20250522"
    description: "Latest Claude 4.5 - Best for creative writing"
    default: true
```

## Troubleshooting

**Models not showing up?**
- Check YAML syntax (indentation matters!)
- Verify the file is in the correct location
- Check the Flask logs for error messages
- Restart the web server after making changes

**Default model not selected?**
- Ensure only ONE model has `default: true`
- Check that the model ID matches exactly

**Invalid YAML error?**
- Use a YAML validator (e.g., yamllint)
- Check for proper indentation (use spaces, not tabs)
- Ensure all quotes are balanced
