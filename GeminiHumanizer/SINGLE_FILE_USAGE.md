# Single YAML File - Complete 30 Chapter Processing

This file explains how to use the single YAML configuration to process all 30 chapters with one command.

## Quick Start

### Run All 30 Chapters in One Command

```bash
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml
```

That's it! This single command will:
- Process all 30 chapters sequentially
- Run each chapter through all 4 humanization phases
- Save outputs to `humanized_chapters/` directory
- Total: 120 prompt executions (30 chapters × 4 phases)

## Prerequisites

1. **Input Files**: Ensure you have `chapter_1.md` through `chapter_30.md` in the current directory
2. **API Key**: Set your OpenRouter API key:
   ```bash
   export OPENROUTER_API_KEY="your-key-here"
   ```
3. **Installation**: Make sure `openrouter-chain` is installed:
   ```bash
   ./install-global.sh
   ```

## How It Works

The YAML file contains **120 prompt definitions**:
- Chapters 1-30 (30 chapters)
- Each chapter has 4 phases (foundational, stylistic, structural, dialogue)
- 30 × 4 = 120 total steps

### Processing Flow for Each Chapter

```
chapter_N.md
  ↓ Phase 1: Foundational Cleanup (temp 0.6)
  ↓ Phase 2: Stylistic Enhancement (temp 0.7)
  ↓ Phase 3: Structural Humanization (temp 0.75)
  ↓ Phase 4: Dialogue Refinement (temp 0.8)
  → humanized_chapters/chapter_N_humanized.md
```

### Temporary Files

Each chapter uses a temporary file (`chapter_N_temp.md`) to pass content between phases. These are automatically cleaned up after each chapter completes.

## Expected Output

After completion, you'll have:
```
humanized_chapters/
  ├── chapter_1_humanized.md
  ├── chapter_2_humanized.md
  ├── chapter_3_humanized.md
  ...
  └── chapter_30_humanized.md
```

Plus intermediate step files in the temp directory for debugging.

## Restart and Recovery

If processing fails partway through, you can restart:

```bash
# Check status
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml --status-only

# Restart from where it failed
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml --restart

# Force restart from a specific step (e.g., step 45 = Chapter 12 Phase 1)
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml --restart-from 45
```

### Step Number Reference

Each chapter uses 4 steps, so to calculate step numbers:
- Chapter 1: Steps 1-4
- Chapter 2: Steps 5-8
- Chapter 3: Steps 9-12
- Chapter N: Steps ((N-1)×4+1) through (N×4)

For example:
- Chapter 10 starts at step 37 (9×4+1)
- Chapter 20 starts at step 77 (19×4+1)
- Chapter 30 starts at step 117 (29×4+1)

## Processing Time & Cost

**Time Estimate:**
- Per chapter: ~10-15 minutes
- All 30 chapters: ~5-7 hours

**Cost Estimate (Gemini 3 Pro Preview):**
- Per chapter: ~$0.03-0.06
- All 30 chapters: ~$0.90-1.80

Assumes average chapter length of ~5000 words. Actual costs may vary.

## Monitoring Progress

The script provides clear console output:

```
========================================
Gemini Humanizer: Processing 30 Chapters
4 Phases per Chapter = 120 Total Steps
========================================

Chapter 1 - Phase 1: Foundational Cleanup
Result: ✅ prompt 1 ch01_phase1_foundational output size: 21.6k time: 136.3 seconds

Chapter 1 - Phase 2: Stylistic Enhancement
Result: ✅ prompt 2 ch01_phase2_stylistic output size: 21.3k time: 135.7 seconds

Chapter 1 - Phase 3: Structural Humanization
Result: ✅ prompt 3 ch01_phase3_structural output size: 21.1k time: 139.2 seconds

Chapter 1 - Phase 4: Dialogue Refinement
Result: ✅ prompt 4 ch01_phase4_dialogue output size: 21.0k time: 138.5 seconds
✓ Chapter 1 Complete

[Process continues for chapters 2-30...]

✓ Chapter 30 Complete - ALL CHAPTERS PROCESSED!
========================================
All 30 Chapters Processed!
Files created: 30
========================================
```

## Debug Mode

For detailed logging:

```bash
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml --debug
```

## Customization

### Change Model

Edit the YAML file:

```yaml
global_config:
  model: "anthropic/claude-sonnet-4"  # Switch to Claude
  # model: "google/gemini-flash-1.5-8b"  # Switch to cheaper/faster Gemini Flash
```

### Adjust Temperatures

Each phase has optimized temperature settings in the YAML. You can adjust them globally or per-phase.

### Process Subset of Chapters

If you only want specific chapters, you can:

1. **Delete unwanted chapter entries** from the YAML
2. **Set passes: 0** for chapters you want to skip (add this to each of the 4 phases for that chapter)

## Advantages of Single YAML Approach

✅ **One Command**: No need for bash scripts or loops
✅ **Restart Support**: Built-in restart/recovery from any point
✅ **Status Tracking**: Complete visibility into progress
✅ **Consistent Configuration**: Same settings for all chapters
✅ **Easy to Customize**: Edit one file to change behavior

## Disadvantages

⚠️ **Sequential Only**: Processes one chapter at a time (no parallelization)
⚠️ **Large File**: 1400+ lines (but generated, so maintainability isn't an issue)
⚠️ **Long Runtime**: 5-7 hours for all 30 chapters

## Alternative: Bash Script

If you prefer the bash script approach with more flexibility:

```bash
./GeminiHumanizer/process_all_chapters.sh
```

This gives you:
- Colored output
- Better error handling
- Ability to continue after failures
- Individual progress indicators

## Troubleshooting

### "cp: cannot stat 'chapter_X.md': No such file or directory"

**Problem**: Missing input file
**Solution**: Ensure all `chapter_1.md` through `chapter_30.md` files exist in the current directory

```bash
ls chapter_*.md | wc -l  # Should show 30
```

### Processing Stops Midway

**Problem**: API timeout or error
**Solution**: Use restart functionality

```bash
openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml --restart
```

### Want to Test First

**Problem**: Don't want to process all 30 chapters yet
**Solution**: Use the single-chapter config for testing

```bash
openrouter-chain -c GeminiHumanizer/gemini_humanizer_chain.yaml
```

## File Structure

```
GeminiHumanizer/
├── 1_foundational_cleanup.json              # Phase 1 prompt
├── 2_stylistic_narrative_enhancement.json   # Phase 2 prompt
├── 3_advanced_structural_statistical_humanization.json  # Phase 3 prompt
├── 4_dialogue_refinement.json               # Phase 4 prompt
├── gemini_humanizer_chain.yaml              # Single chapter config
├── process_all_30_chapters.yaml             # ← THIS FILE (30 chapters, single command)
├── process_all_chapters.sh                  # Bash script alternative
├── README.md                                # Original workflow docs
├── USAGE.md                                 # General usage guide
└── SINGLE_FILE_USAGE.md                     # This file
```

## Summary

**Best for**: Long-running batch processing with built-in restart/recovery
**Use when**: You want one command to process everything
**Command**: `openrouter-chain -c GeminiHumanizer/process_all_30_chapters.yaml`

Happy humanizing! 🚀
