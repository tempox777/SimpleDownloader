#!/bin/bash
# SimpleDownloader Uninstallation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_DIR="/opt/SimpleDownloader"
BIN_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/256x256/apps"

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

echo ""
print_info "================================"
print_info "SimpleDownloader Uninstaller"
print_info "================================"
echo ""

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    print_info "Removing installation directory..."
    rm -rf "$INSTALL_DIR"
    print_success "Installation directory removed"
else
    print_info "Installation directory not found (already removed)"
fi

# Remove CLI launcher
if [ -f "$BIN_DIR/simpledownloader" ]; then
    print_info "Removing CLI launcher..."
    rm -f "$BIN_DIR/simpledownloader"
    print_success "CLI launcher removed"
fi

# Remove GUI launcher
if [ -f "$BIN_DIR/simpledownloader-gui" ]; then
    print_info "Removing GUI launcher..."
    rm -f "$BIN_DIR/simpledownloader-gui"
    print_success "GUI launcher removed"
fi

# Remove desktop entry
if [ -f "$DESKTOP_DIR/simpledownloader.desktop" ]; then
    print_info "Removing desktop entry..."
    rm -f "$DESKTOP_DIR/simpledownloader.desktop"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    print_success "Desktop entry removed"
fi

# Remove icon
if [ -f "$ICON_DIR/simpledownloader.png" ]; then
    print_info "Removing application icon..."
    rm -f "$ICON_DIR/simpledownloader.png"
    print_success "Icon removed"
fi

echo ""
print_success "================================"
print_success "Uninstallation Complete!"
print_success "================================"
echo ""
print_info "SimpleDownloader has been completely removed from your system."
echo ""

