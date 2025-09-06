#!/usr/bin/env python3
"""
Basic usage examples for OpenRouter Interface.

This file demonstrates how to use the OpenRouter Interface package
programmatically instead of through the command line.
"""

import os
from pathlib import Path
from openrouter_interface import (
    ConfigManager, 
    PromptRunner, 
    PromptScanner,
    PromptLoader,
    InputFileHandler,
    PromptAPIClient
)

# Set your API key (required)
# os.environ['OPENROUTER_API_KEY'] = 'your-api-key-here'

def example_basic_processing():
    """Example: Basic prompt processing workflow."""
    print("=== Basic Processing Example ===")
    
    # Initialize configuration
    config = ConfigManager()
    
    # Create prompt runner
    runner = PromptRunner()
    
    # For this example, we'd need actual files
    prompt_file = Path("prompts/creative_writing_assistant.json")
    input_file = Path("examples/sample_input.md")
    
    if prompt_file.exists() and input_file.exists():
        success = runner.run_batch_mode(str(prompt_file), str(input_file))
        if success:
            print("✓ Processing completed successfully")
        else:
            print("✗ Processing failed")
    else:
        print(f"Required files not found:")
        print(f"  Prompt: {prompt_file} ({'exists' if prompt_file.exists() else 'missing'})")
        print(f"  Input: {input_file} ({'exists' if input_file.exists() else 'missing'})")

def example_scan_prompts():
    """Example: Scan for available prompts."""
    print("\n=== Prompt Scanning Example ===")
    
    scanner = PromptScanner()
    
    # Change to prompts directory for scanning
    original_dir = Path.cwd()
    prompts_dir = Path("prompts")
    
    if prompts_dir.exists():
        os.chdir(prompts_dir)
        prompts = scanner.scan_for_prompts()
        os.chdir(original_dir)
        
        print(f"Found {len(prompts)} prompt files:")
        for i, prompt in enumerate(prompts[:5], 1):  # Show first 5
            print(f"  {i}. {prompt.name}")
        
        if len(prompts) > 5:
            print(f"  ... and {len(prompts) - 5} more")
    else:
        print("Prompts directory not found")

def example_load_prompt():
    """Example: Load and examine a prompt file."""
    print("\n=== Prompt Loading Example ===")
    
    loader = PromptLoader()
    prompt_file = Path("prompts/creative_writing_assistant.json")
    
    if prompt_file.exists():
        try:
            prompt_data = loader.load_prompt(prompt_file)
            print(f"✓ Loaded prompt: {prompt_file.name}")
            print(f"  Instruction: {prompt_data.get('instruction', 'N/A')[:100]}...")
            print(f"  Type: {prompt_data.get('type', 'N/A')}")
            
            if 'requirements' in prompt_data:
                print(f"  Requirements: {len(prompt_data['requirements'])} items")
                
        except Exception as e:
            print(f"✗ Failed to load prompt: {e}")
    else:
        print(f"Prompt file not found: {prompt_file}")

def example_configuration():
    """Example: Working with configuration."""
    print("\n=== Configuration Example ===")
    
    # Load default configuration
    config = ConfigManager()
    print("Default configuration:")
    print(f"  Model: {config.get('model', 'Not set')}")
    print(f"  Temperature: {config.get('temperature', 'Not set')}")
    print(f"  Max Tokens: {config.get('max_tokens', 'Not set')}")
    
    # Load from custom config file
    config_file = Path("config/config.yaml")
    if config_file.exists():
        custom_config = ConfigManager(str(config_file))
        print(f"\nCustom configuration from {config_file}:")
        print(f"  Model: {custom_config.get('model', 'Not set')}")
        print(f"  Temperature: {custom_config.get('temperature', 'Not set')}")
    else:
        print(f"\nCustom config file not found: {config_file}")

def example_api_client():
    """Example: Direct API client usage."""
    print("\n=== API Client Example ===")
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠ API key not set. Set OPENROUTER_API_KEY environment variable.")
        return
    
    config = ConfigManager()
    client = PromptAPIClient(config)
    
    # Example prompt - this would normally come from a loaded JSON file
    test_prompt = {
        "role": "user",
        "content": "Write a haiku about programming."
    }
    
    try:
        print("Making test API call...")
        response = client.call_api(test_prompt)
        print("✓ API call successful")
        print(f"Response preview: {str(response)[:100]}...")
    except Exception as e:
        print(f"✗ API call failed: {e}")

def main():
    """Run all examples."""
    print("OpenRouter Interface - Usage Examples")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/openrouter_interface").exists():
        print("Error: Please run this script from the project root directory")
        return
    
    try:
        example_scan_prompts()
        example_load_prompt()
        example_configuration()
        example_basic_processing()
        example_api_client()
        
    except ImportError as e:
        print(f"\nImport Error: {e}")
        print("Make sure the package is installed:")
        print("  pip install -e .")
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()