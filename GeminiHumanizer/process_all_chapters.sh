#!/bin/bash
# Batch processing script for Gemini Humanizer Chain
# Processes all chapters (chapter_1.md through chapter_30.md) through the 4-stage humanization pipeline

set -e  # Exit on error

# Configuration
CHAIN_CONFIG="GeminiHumanizer/gemini_humanizer_chain.yaml"
INPUT_DIR="."  # Directory containing chapter files
OUTPUT_DIR="humanized_chapters"  # Directory for processed output
START_CHAPTER=1
END_CHAPTER=30

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Gemini Humanizer - Batch Chapter Processor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Check if openrouter-chain is available
if ! command -v openrouter-chain &> /dev/null; then
    echo -e "${RED}ERROR: openrouter-chain command not found${NC}"
    echo "Please run ./install-global.sh first"
    exit 1
fi

# Check if base config exists
if [ ! -f "$CHAIN_CONFIG" ]; then
    echo -e "${RED}ERROR: Chain config not found: $CHAIN_CONFIG${NC}"
    exit 1
fi

# Process each chapter
TOTAL_CHAPTERS=$((END_CHAPTER - START_CHAPTER + 1))
CURRENT=0

for i in $(seq $START_CHAPTER $END_CHAPTER); do
    CURRENT=$((CURRENT + 1))
    INPUT_FILE="${INPUT_DIR}/chapter_${i}.md"
    OUTPUT_FILE="${OUTPUT_DIR}/chapter_${i}_humanized.md"
    TEMP_CONFIG="${OUTPUT_DIR}/temp_config_chapter_${i}.yaml"

    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}Processing Chapter $i ($CURRENT/$TOTAL_CHAPTERS)${NC}"
    echo -e "${YELLOW}========================================${NC}"

    # Check if input file exists
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${RED}WARNING: Input file not found: $INPUT_FILE${NC}"
        echo "Skipping..."
        continue
    fi

    # Create temporary config with updated paths
    sed "s|input_file:.*|input_file: \"$INPUT_FILE\"|g" "$CHAIN_CONFIG" | \
    sed "s|output_file:.*|output_file: \"$OUTPUT_FILE\"|g" > "$TEMP_CONFIG"

    # Run the chain
    echo -e "${GREEN}Starting 4-stage humanization pipeline...${NC}"
    echo ""

    if openrouter-chain -c "$TEMP_CONFIG"; then
        echo ""
        echo -e "${GREEN}✓ Chapter $i completed successfully${NC}"
        echo -e "${GREEN}  Output: $OUTPUT_FILE${NC}"

        # Show file size comparison
        INPUT_SIZE=$(wc -c < "$INPUT_FILE")
        OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
        echo -e "${GREEN}  Input size: $INPUT_SIZE bytes${NC}"
        echo -e "${GREEN}  Output size: $OUTPUT_SIZE bytes${NC}"
    else
        echo ""
        echo -e "${RED}✗ Chapter $i failed${NC}"
        echo -e "${RED}  Check the error messages above${NC}"

        # Ask if user wants to continue
        read -p "Continue with remaining chapters? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborting batch processing"
            exit 1
        fi
    fi

    # Clean up temp config
    rm -f "$TEMP_CONFIG"

    echo ""
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Batch Processing Complete${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Processed chapters saved to: $OUTPUT_DIR/${NC}"
echo ""

# Summary statistics
SUCCESSFUL=$(ls -1 "$OUTPUT_DIR"/chapter_*_humanized.md 2>/dev/null | wc -l)
echo -e "${GREEN}Successfully processed: $SUCCESSFUL/$TOTAL_CHAPTERS chapters${NC}"
