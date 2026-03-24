#!/usr/bin/env bash
# ARIA Install & Launch Script
set -e

echo ""
echo "  ◈  ARIA — Autonomous Resident Intelligence Assistant"
echo "  ──────────────────────────────────────────────────"
echo ""

# Check Python 3.10+
python3 --version | grep -E "3\.(1[0-9]|[2-9][0-9])" > /dev/null 2>&1 || {
    echo "  ERROR: Python 3.10+ required."
    exit 1
}

echo "  → Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "  → Installing core dependencies..."
pip install PyQt6 psutil --quiet

echo ""
read -p "  → Install Ollama model for AI chat? (requires Ollama at ollama.com) [y/N]: " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
    echo "  → Installing Ollama model..."
    which ollama > /dev/null 2>&1 && ollama pull mistral || echo "  Ollama not found. Install from https://ollama.com first."
fi

echo ""
echo "  ✅ Setup complete!"
echo ""
echo "  → Launching ARIA..."
echo "  (Look for the ARIA icon in your system tray)"
echo "  (Press Ctrl+Space anywhere to open/close ARIA)"
echo ""
python3 aria.py
