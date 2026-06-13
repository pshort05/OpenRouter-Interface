# Gemini Humanizer Chain - Usage Guide

This directory contains a 4-stage AI text humanization pipeline designed to transform AI-generated prose into natural, human-like writing.

## Files Overview

- **1_foundational_cleanup.json** - Phase 1: Grammar, AI word removal, weak language
- **2_stylistic_narrative_enhancement.json** - Phase 2: Overwritten language, sensory details, subtlety
- **3_advanced_structural_statistical_humanization.json** - Phase 3: Pattern elimination, imperfections, statistical optimization
- **4_dialogue_refinement.json** - Phase 4: Character voice, subtext, dialogue pacing
- **gemini_humanizer_chain.yaml** - Chain configuration file
- **process_all_chapters.sh** - Batch processing script for multiple chapters
- **README.md** - Original workflow documentation

## Quick Start: Processing Your 30-Chapter Novel

### Option 1: Batch Process All Chapters (Recommended)

Process all chapters automatically with one command:

```bash
# Make sure you're in the OpenRouter-Interface directory
cd /home/paul/data/Dropbox/Writing/OpenRouter-Interface

# Run the batch processor
./GeminiHumanizer/process_all_chapters.sh
```

This will:
- Process `chapter_1.md` through `chapter_30.md`
- Save output to `humanized_chapters/` directory
- Show progress for each chapter
- Generate detailed statistics

**Input:** `chapter_1.md`, `chapter_2.md`, ..., `chapter_30.md` (in current directory)
**Output:** `humanized_chapters/chapter_1_humanized.md`, `chapter_2_humanized.md`, etc.

### Option 2: Process a Single Chapter

Process one chapter at a time:

```bash
# Edit the config to specify your chapter
nano GeminiHumanizer/gemini_humanizer_chain.yaml

# Change these lines:
# input_file: "chapter_1.md"
# output_file: "chapter_1_humanized.md"

# Run the chain
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml
```

### Option 3: Process Specific Chapter Range

Edit the batch script to process a specific range:

```bash
# Edit process_all_chapters.sh
nano GeminiHumanizer/process_all_chapters.sh

# Modify these lines:
START_CHAPTER=5   # Start at chapter 5
END_CHAPTER=10    # End at chapter 10

# Run the script
./GeminiHumanizer/process_all_chapters.sh
```

## Customization Options

### 1. Change the AI Model

Edit `gemini_humanizer_chain.yaml`:

```yaml
global_config:
  # Currently using latest Gemini model
  model: "google/gemini-3-pro-preview"     # Gemini 3 Pro (latest, recommended)
  # model: "anthropic/claude-sonnet-4"    # Claude Sonnet 4
  # model: "google/gemini-flash-1.5-8b"   # Gemini Flash (faster, cheaper)
```

### 2. Adjust Temperature for Each Phase

Each phase has a temperature setting optimized for its task:

```yaml
prompts:
  phase_1_foundational:
    temperature: 0.6  # Lower = more consistent grammar fixes
  phase_2_stylistic:
    temperature: 0.7  # Moderate = balanced creativity
  phase_3_structural:
    temperature: 0.75 # Higher = more variation
  phase_4_dialogue:
    temperature: 0.8  # Highest = natural dialogue variation
```

### 3. Multi-Pass Processing

Run any phase multiple times:

```yaml
prompts:
  phase_1_foundational:
    passes: 2  # Run Phase 1 twice for thorough cleanup
```

### 4. Change Input/Output Directories

Edit `process_all_chapters.sh`:

```bash
INPUT_DIR="../my_chapters"      # Where your chapter files are
OUTPUT_DIR="final_humanized"    # Where to save processed files
```

### 5. Debug Mode

See detailed processing information:

```bash
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml --debug
```

## What Each Phase Does

### Phase 1: Foundational Cleanup (Temperature: 0.6)
- ✓ Fixes critical grammar errors
- ✓ Removes AI-associated words and phrases
- ✓ Eliminates weak language (puff words, hedge words, filter phrases)
- ✓ Replaces formal transitions with casual connectors
- ✓ Adjusts active/passive voice distribution

**Processing Time:** ~2-3 minutes per chapter

### Phase 2: Stylistic & Narrative Enhancement (Temperature: 0.7)
- ✓ Reduces overwritten/purple prose
- ✓ Converts passive voice to active
- ✓ Adds sensory details to flat passages
- ✓ Creates subtlety (show don't tell)
- ✓ Eliminates on-the-nose writing

**Processing Time:** ~2-3 minutes per chapter

### Phase 3: Advanced Structural & Statistical Humanization (Temperature: 0.75)
- ✓ Eliminates 29 mechanical syntactic patterns
- ✓ Injects strategic human-like imperfections
- ✓ Removes Oxford commas (AI detection marker)
- ✓ Optimizes N-grams and perplexity
- ✓ Balances burstiness, POS distribution, lexical diversity

**Processing Time:** ~3-4 minutes per chapter

### Phase 4: Dialogue Refinement (Temperature: 0.8)
- ✓ Develops distinct character voices
- ✓ Layers subtext into conversations
- ✓ Optimizes pacing and flow
- ✓ Integrates modern language patterns
- ✓ Adds realistic disfluencies

**Processing Time:** ~2-3 minutes per chapter

**Total Processing Time per Chapter:** ~10-15 minutes
**Total Time for 30 Chapters:** ~5-7 hours

## Restart and Recovery

If processing fails mid-chain, use the restart functionality:

```bash
# Check status
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml --status-only

# Restart from where it failed
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml --restart

# Force restart from Phase 3
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml --restart-from 3
```

## Tips for Best Results

1. **Start with a Test Chapter**: Process chapter_1.md first to verify the workflow before batch processing
2. **Monitor the Output**: Check the first few humanized chapters to ensure quality meets your needs
3. **Adjust Temperatures**: If output is too conservative, increase temperature; if too wild, decrease it
4. **Use Appropriate Models**: Gemini 3 Pro (default) provides excellent quality; switch to Gemini Flash for faster/cheaper processing or Claude Sonnet 4 for maximum quality
5. **Review Intermediate Files**: Check `*_step_*` files in temp directory to see each phase's output
6. **Back Up Your Originals**: Keep original chapter files safe before processing

## File Naming Convention

Intermediate files are saved as:
- `chapter_1_step_1_phase_1_foundational_cleanup.md`
- `chapter_1_step_2_phase_2_stylistic_narrative.md`
- `chapter_1_step_3_phase_3_structural_statistical.md`
- `chapter_1_step_4_phase_4_dialogue_refinement.md`

Final output:
- `chapter_1_humanized.md`

## Troubleshooting

### "Input file not found"
Make sure your chapter files are in the correct directory:
```bash
ls chapter_*.md  # Should show chapter_1.md through chapter_30.md
```

### "openrouter-chain command not found"
Install the OpenRouter Interface globally:
```bash
./install-global.sh
```

### "API key not set"
Set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="your-key-here"
# Or run the setup script
./setup-api-key.sh
```

### Processing seems too aggressive/conservative
Adjust the temperature settings in `gemini_humanizer_chain.yaml`

### Want to skip a phase
Set `passes: 0` for any phase you want to skip:
```yaml
phase_2_stylistic:
  passes: 0  # Skip Phase 2
```

## Cost Estimation

Approximate costs using OpenRouter (prices vary by model):

- **Gemini 3 Pro Preview** (default): ~$0.03-0.06 per chapter → **~$0.90-1.80 for 30 chapters**
- **Gemini Flash 1.5 8B**: ~$0.01-0.02 per chapter → **~$0.30-0.60 for 30 chapters**
- **Claude Sonnet 4**: ~$0.15-0.30 per chapter → **~$4.50-9.00 for 30 chapters**

Costs depend on chapter length. Assumes average chapter ~5000 words.

## Advanced: Parallel Processing

Process multiple chapters simultaneously (requires more resources):

```bash
# Process chapters 1-10 in parallel (be careful with API rate limits!)
for i in {1..10}; do
  sed "s|chapter_1|chapter_$i|g" GeminiHumanizer/gemini_humanizer_chain.yaml > temp_config_$i.yaml
  openrouter-chain -c temp_config_$i.yaml &
done
wait
```

## Support

For issues or questions:
- Check the main README.md in the OpenRouter-Interface directory
- Review the original GeminiHumanizer/README.md for workflow details
- Check individual prompt JSON files for detailed instructions
