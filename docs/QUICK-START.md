# Quick Start Guide - Run Your First Prompt in 3 Minutes

Get started with OpenRouter Prompt Runner in just a few simple steps. No complex configuration needed!

## ⚡ Super Quick Setup (30 seconds)

1. **Get your API key** from [OpenRouter.ai](https://openrouter.ai/keys)
2. **Set environment variable:**
   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```
3. **Install requirements:**
   ```bash
   pip install requests PyYAML
   ```

Done! You're ready to run prompts.

## 🚀 Run Your First Prompt (2 minutes)

### Method 1: Interactive Mode (Easiest)
Just run the program and follow the menu:

```bash
python prompt_runner.py
```

The program will:
- Show you all available prompts (`.json` files)
- Let you pick one from a menu
- Ask for an input file to process
- Run the AI and show results

### Method 2: Direct Command (Fastest)
If you know exactly what you want:

```bash
python prompt_runner.py -p "creative_writing_assistant.json" -i your_document.md
```

## 📝 What You Need

**Two files minimum:**
1. **A prompt file** (`.json`) - Instructions for the AI
2. **An input file** (`.md`, `.txt`, etc.) - Your content to process

**We include 25+ ready-to-use prompts:**
- `creative_writing_assistant.json` - General writing help
- `dialogue_editor.json` - Improve dialogue
- `engagement_checker.json` - Check if text is engaging
- `copy_editor_prompt_v1.3.json` - Copy editing
- `first_chapter_checker.json` - First chapter feedback
- And many more...

## 🎯 Try These Examples

### Example 1: Quick Writing Check
```bash
# Check if your writing is engaging
python prompt_runner.py -p "engagement_checker.json" -i my_chapter.md
```

### Example 2: Dialogue Improvement
```bash
# Improve dialogue in your story
python prompt_runner.py -p "dialogue_editor.json" -i story_draft.md
```

### Example 3: Save Results to File
```bash
# Save AI feedback to a file
python prompt_runner.py -p "copy_editor_prompt_v1.3.json" -i document.md -o feedback.md
```

## 📄 Sample Files to Get Started

### Create a simple input file (`test_input.md`):
```markdown
# My Story Draft

John walked into the room. "Hello," he said to Mary.

"Hi there," Mary replied. "How was your day?"

"It was fine," John answered.

The weather outside was nice. They talked for a while about various things.
```

### Try it with the dialogue editor:
```bash
python prompt_runner.py -p "dialogue_editor.json" -i test_input.md
```

## ✅ What Happens

1. **AI analyzes your content** using the selected prompt
2. **Results stream to your console** in real-time
3. **Optionally saves to file** (use `-o filename.md`)
4. **You get professional AI feedback** instantly

## 🔧 Common Options

```bash
# Save output to file
python prompt_runner.py -p prompt.json -i input.md -o results.md

# Enable detailed logging
python prompt_runner.py -p prompt.json -i input.md -v

# Use custom configuration
python prompt_runner.py -p prompt.json -i input.md -c config.yaml
```

## 🆘 Quick Troubleshooting

**"No API key found"**
```bash
export OPENROUTER_API_KEY="your-actual-key-here"
```

**"No JSON files found"**
- Make sure you're in the right directory
- JSON prompt files should be in the same folder

**"File not found"**
- Check file paths are correct
- Use absolute paths if needed: `/full/path/to/file.md`

## 🎓 What's Next?

Once you've run your first prompt successfully:

1. **Explore more prompts** - Try different ones for various writing tasks
2. **Chain prompts together** - Use `prompt_chain_runner.py` for multi-step processing
3. **Create custom prompts** - Make your own `.json` prompt files
4. **Use the web interface** - Run `python prompt_runner_flask.py` for a GUI

## 📚 Available Prompt Types

**Writing & Editing:**
- Creative writing assistance
- Copy editing and proofreading  
- Dialogue improvement
- Engagement analysis

**Story Analysis:**
- Chapter quality checking
- Character development review
- Plot structure analysis
- Genre convention checking

**Technical:**
- Code review and analysis
- Document analysis
- Technical writing review

## 💡 Pro Tips

- **Use descriptive input files** - The AI works better with more context
- **Try different prompts** on the same content for varied perspectives
- **Save important results** with `-o output_file.md`
- **Use logging** with `-l log_file.log` to track what you've done

---

**Need more help?** Check the main CLAUDE.md file for advanced features, or run:
```bash
python prompt_runner.py --help
```