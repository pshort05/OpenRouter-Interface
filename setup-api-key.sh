#!/bin/bash
# OpenRouter API Key Setup Script
# Sets up the API key for current session and permanently in .bashrc

set -e

echo "🔑 OpenRouter API Key Setup"
echo "=========================="

# Check if API key is already set
if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "✅ OpenRouter API key is already set in current session"
    echo "Current key: ${OPENROUTER_API_KEY:0:8}..."
    read -p "Do you want to update it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing API key"
        exit 0
    fi
fi

# Prompt for API key
echo ""
echo "📋 Get your API key from: https://openrouter.ai/keys"
echo ""
read -p "Enter your OpenRouter API key: " -r api_key

# Validate API key format (basic check)
if [ -z "$api_key" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

if [ ${#api_key} -lt 20 ]; then
    echo "❌ Error: API key seems too short (should be at least 20 characters)"
    exit 1
fi

# Export for current session
export OPENROUTER_API_KEY="$api_key"
echo "✅ API key set for current session"

# Check if already in .bashrc
bashrc_file="$HOME/.bashrc"
api_key_line="export OPENROUTER_API_KEY=\"$api_key\""

if grep -q "export OPENROUTER_API_KEY=" "$bashrc_file" 2>/dev/null; then
    echo "📝 Updating existing API key in .bashrc..."
    # Use sed to replace the existing line
    sed -i "s|export OPENROUTER_API_KEY=.*|$api_key_line|" "$bashrc_file"
else
    echo "📝 Adding API key to .bashrc..."
    echo "" >> "$bashrc_file"
    echo "# OpenRouter API Key" >> "$bashrc_file"
    echo "$api_key_line" >> "$bashrc_file"
fi

echo "✅ API key saved to .bashrc (will be available after reboot)"

# Test the API key
echo ""
echo "🧪 Testing API key..."
if command -v curl >/dev/null 2>&1; then
    response=$(curl -s -H "Authorization: Bearer $api_key" \
                   -H "Content-Type: application/json" \
                   "https://openrouter.ai/api/v1/models" 2>/dev/null)
    
    if [[ $response == *'"data":'* ]] && [[ $response == *'"id":'* ]]; then
        echo "✅ API key is valid and working!"
        # Show first model as example
        first_model=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        echo "   First available model: $first_model"
    else
        echo "⚠️  Warning: API key test failed. Please verify your key is correct."
        echo "   This might be due to network issues or an invalid key."
        echo "   You can test manually at: https://openrouter.ai/playground"
    fi
else
    echo "⚠️  curl not available - cannot test API key"
    echo "✅ API key has been set (manual testing recommended)"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "The API key is now:"
echo "  ✅ Active in this session"  
echo "  ✅ Saved to .bashrc for future sessions"
echo ""
echo "You can now run OpenRouter Interface applications:"
echo "  • openrouter-runner  (CLI interface)"
echo "  • openrouter-web     (Web interface)"
echo "  • openrouter-chain   (Chain runner)"
echo ""