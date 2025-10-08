#!/bin/bash
# SimpleDownloader Installation Script
# Installs SimpleDownloader system-wide with app launcher integration

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER="${SUDO_USER:-$USER}"
ACTUAL_HOME=$(getent passwd "$ACTUAL_USER" | cut -d: -f6)

print_info "Installing SimpleDownloader for user: $ACTUAL_USER"

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/arch-release ]; then
        DISTRO="arch"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        DISTRO="unknown"
    fi
    print_info "Detected distribution: $DISTRO"
}

# Install dependencies based on distribution
install_dependencies() {
    print_info "Installing system dependencies..."
    
    case $DISTRO in
        arch|manjaro|endeavouros)
            pacman -S --noconfirm python python-pip tk ffmpeg git
            ;;
        ubuntu|debian|linuxmint|pop)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv python3-tk ffmpeg git
            ;;
        fedora|rhel|centos)
            dnf install -y python3 python3-pip python3-tkinter ffmpeg git
            ;;
        opensuse*)
            zypper install -y python3 python3-pip python3-tk ffmpeg git
            ;;
        *)
            print_warning "Unknown distribution. Please manually install: python3, python3-pip, python3-venv, python3-tk, ffmpeg, git"
            print_info "Continuing with installation..."
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Download or copy application files
install_application() {
    print_info "Installing SimpleDownloader to $INSTALL_DIR..."
    
    # Remove old installation if exists
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Removing previous installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Check if we're running from the repo directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$SCRIPT_DIR/DownloaderGUI.py" ]; then
        print_info "Installing from local directory..."
        cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
        # Remove install/uninstall scripts and git files from installation directory
        rm -f "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" "$INSTALL_DIR/TESTING.md"
        rm -rf "$INSTALL_DIR/.git" "$INSTALL_DIR/.gitignore"
    else
        print_info "Downloading from GitHub..."
        # Clone to temporary directory first
        TEMP_DIR=$(mktemp -d)
        git clone https://github.com/tempox777/SimpleDownloader.git "$TEMP_DIR"
        # Copy only necessary files
        cp -r "$TEMP_DIR"/* "$INSTALL_DIR/"
        # Clean up
        rm -rf "$TEMP_DIR"
        rm -f "$INSTALL_DIR/install.sh" "$INSTALL_DIR/uninstall.sh" "$INSTALL_DIR/TESTING.md"
        rm -rf "$INSTALL_DIR/.git" "$INSTALL_DIR/.gitignore"
    fi
    
    print_success "Application files installed"
}

# Setup Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv .venv
    
    # Activate and install dependencies
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    print_success "Python virtual environment configured"
}

# Create launcher script for CLI access
create_cli_launcher() {
    print_info "Creating CLI launcher..."
    
    cat > "$BIN_DIR/simpledownloader" << 'EOF'
#!/bin/bash
# SimpleDownloader CLI Launcher
cd /opt/SimpleDownloader
source .venv/bin/activate
python3 Downloader.py "$@"
EOF
    
    chmod +x "$BIN_DIR/simpledownloader"
    print_success "CLI launcher created: simpledownloader"
}

# Create GUI launcher script
create_gui_launcher() {
    print_info "Creating GUI launcher..."
    
    cat > "$BIN_DIR/simpledownloader-gui" << 'EOF'
#!/bin/bash
# SimpleDownloader GUI Launcher
cd /opt/SimpleDownloader
source .venv/bin/activate
exec python3 DownloaderGUI.py "$@"
EOF
    
    chmod +x "$BIN_DIR/simpledownloader-gui"
    print_success "GUI launcher created: simpledownloader-gui"
}

# Create desktop entry for app launcher
create_desktop_entry() {
    print_info "Creating desktop entry..."
    
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/simpledownloader.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SimpleDownloader
Comment=Download videos and audio with a beautiful GUI
Exec=$BIN_DIR/simpledownloader-gui
Icon=simpledownloader
Terminal=false
Categories=Network;AudioVideo;Video;
Keywords=download;youtube;video;audio;yt-dlp;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_DIR/simpledownloader.desktop"
    
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    fi
    
    print_success "Desktop entry created"
}

# Create application icon
create_icon() {
    print_info "Creating application icon..."
    
    mkdir -p "$ICON_DIR"
    
    # Create a simple icon using ImageMagick if available, otherwise skip
    if command -v convert >/dev/null 2>&1; then
        convert -size 256x256 xc:black \
            -fill white -stroke white -strokewidth 2 \
            -draw "polygon 128,50 210,180 46,180" \
            -draw "rectangle 80,120 176,200" \
            "$ICON_DIR/simpledownloader.png" 2>/dev/null || print_warning "Could not create icon (ImageMagick not available)"
    else
        print_warning "ImageMagick not available, skipping icon creation"
    fi
}

# Set proper permissions
set_permissions() {
    print_info "Setting permissions..."
    
    # Set ownership to root but make readable by all
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    # Make scripts executable
    chmod +x "$INSTALL_DIR"/*.py 2>/dev/null || true
    chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true
    
    print_success "Permissions set"
}

# Main installation process
main() {
    echo ""
    print_info "================================"
    print_info "SimpleDownloader Installer"
    print_info "================================"
    echo ""
    
    detect_distro
    install_dependencies
    install_application
    setup_venv
    create_cli_launcher
    create_gui_launcher
    create_desktop_entry
    create_icon
    set_permissions
    
    echo ""
    print_success "================================"
    print_success "Installation Complete!"
    print_success "================================"
    echo ""
    print_info "You can now:"
    print_info "  1. Find 'SimpleDownloader' in your app launcher"
    print_info "  2. Run 'simpledownloader-gui' from terminal for GUI"
    print_info "  3. Run 'simpledownloader <url>' from terminal for CLI"
    echo ""
    print_info "To uninstall, run:"
    print_info "  curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/uninstall.sh | sudo sh"
    echo ""
}

# Run main installation
main

