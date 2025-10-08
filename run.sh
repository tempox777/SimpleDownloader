#!/bin/bash
# Launch script for Downloader AI GUI

cd "$(dirname "$0")"

# Check if tk is installed
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ Error: tkinter is not installed!"
    echo ""
    echo "Please install it first:"
    echo "  Arch Linux:    sudo pacman -S tk"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  macOS:         (usually pre-installed)"
    echo ""
    exit 1
fi

# Activate virtual environment and run
source .venv/bin/activate
python DownloaderGUI.py

