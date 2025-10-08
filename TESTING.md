# Testing and Verification Guide

This document describes how to test the SimpleDownloader installation.

## Pre-Installation Checks

### 1. Verify GitHub Files Are Accessible

```bash
# Test install script is accessible
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/install.sh | head -n 5

# Test uninstall script is accessible
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/uninstall.sh | head -n 5
```

Both commands should return the script headers without errors.

## Installation Testing

### 2. Test Installation

Run the installation:
```bash
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/install.sh | sudo sh
```

Verify no errors occurred during installation.

### 3. Verify Files Were Created

Check that all files were installed:

```bash
# Check main installation directory
ls -la /opt/SimpleDownloader

# Check CLI launchers exist
ls -la /usr/local/bin/simpledownloader*

# Check desktop entry
ls -la /usr/share/applications/simpledownloader.desktop

# Verify Python environment was created
ls -la /opt/SimpleDownloader/.venv
```

All commands should show existing files/directories.

### 4. Verify CLI Commands Work

```bash
# Test CLI launcher
which simpledownloader
which simpledownloader-gui

# Test help output
simpledownloader --help
```

Both `which` commands should return paths. The help command should display usage information.

### 5. Test GUI Launch

```bash
simpledownloader-gui
```

The GUI window should open without errors. Close it after verifying.

### 6. Verify Desktop Entry

**On GNOME/KDE/XFCE:**
- Open application launcher
- Search for "SimpleDownloader"
- Verify it appears in results
- Click to launch (should open GUI)

**On Hyprland/i3/Sway:**
```bash
# Verify desktop file is valid
desktop-file-validate /usr/share/applications/simpledownloader.desktop
```

### 7. Test Basic Download

```bash
# Test CLI download (small test file)
cd ~/Downloads
simpledownloader "https://www.youtube.com/watch?v=jNQXAC9IVRw" --audio-only --audio-format mp3
```

Should download "Me at the zoo" audio. Verify file exists in Downloads folder.

### 8. Test GUI Download

1. Launch `simpledownloader-gui`
2. Paste URL: `https://www.youtube.com/watch?v=jNQXAC9IVRw`
3. Click "Fetch Info" - should display video info
4. Select audio-only format
5. Click Download - should complete successfully

## Uninstallation Testing

### 9. Test Uninstallation

```bash
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/uninstall.sh | sudo sh
```

Should complete without errors.

### 10. Verify Complete Removal

```bash
# These should all return "No such file or directory"
ls /opt/SimpleDownloader
ls /usr/local/bin/simpledownloader
ls /usr/local/bin/simpledownloader-gui
ls /usr/share/applications/simpledownloader.desktop
```

All commands should indicate files don't exist.

### 11. Verify Desktop Launcher Entry Removed

Search for "SimpleDownloader" in application launcher - should not appear.

## Distribution-Specific Testing

### Arch Linux / Manjaro
```bash
# Verify dependencies installed
pacman -Q python tk ffmpeg git
```

### Ubuntu / Debian
```bash
# Verify dependencies installed
dpkg -l | grep -E "python3|python3-tk|ffmpeg|git"
```

### Fedora
```bash
# Verify dependencies installed
rpm -qa | grep -E "python3|python3-tkinter|ffmpeg|git"
```

## Troubleshooting Tests

### Test 1: ffmpeg Detection
```bash
# Should return version info
ffmpeg -version
```

### Test 2: Python Version
```bash
# Should be 3.7 or higher
python3 --version
```

### Test 3: tkinter Import
```bash
# Should return no error
python3 -c "import tkinter"
```

### Test 4: Virtual Environment Activation
```bash
source /opt/SimpleDownloader/.venv/bin/activate
python -c "import yt_dlp, customtkinter, PIL"
deactivate
```

All imports should succeed without errors.

## Expected Results Summary

**Installation Success:**
- All files created in correct locations
- CLI commands available in PATH
- Desktop entry appears in launcher
- GUI launches without errors
- Can download test video/audio

**Uninstallation Success:**
- All files removed
- CLI commands no longer available
- Desktop entry removed from launcher
- No leftover files in system

## Common Issues and Verification

### Issue: Command not found after install
**Verify:** 
```bash
echo $PATH | grep /usr/local/bin
```
Should include `/usr/local/bin`

### Issue: GUI doesn't launch
**Verify:**
```bash
/opt/SimpleDownloader/.venv/bin/python -c "import customtkinter"
```
Should import without error

### Issue: Downloads fail
**Verify:**
```bash
/opt/SimpleDownloader/.venv/bin/python -c "import yt_dlp; print(yt_dlp.version.__version__)"
```
Should print yt-dlp version

## Automated Test Script

Save this as `test_install.sh`:

```bash
#!/bin/bash
echo "Testing SimpleDownloader Installation..."

errors=0

# Test 1: Check installation directory
if [ -d "/opt/SimpleDownloader" ]; then
    echo "✓ Installation directory exists"
else
    echo "✗ Installation directory missing"
    ((errors++))
fi

# Test 2: Check CLI launchers
if [ -f "/usr/local/bin/simpledownloader" ] && [ -f "/usr/local/bin/simpledownloader-gui" ]; then
    echo "✓ CLI launchers exist"
else
    echo "✗ CLI launchers missing"
    ((errors++))
fi

# Test 3: Check desktop entry
if [ -f "/usr/share/applications/simpledownloader.desktop" ]; then
    echo "✓ Desktop entry exists"
else
    echo "✗ Desktop entry missing"
    ((errors++))
fi

# Test 4: Check Python environment
if [ -d "/opt/SimpleDownloader/.venv" ]; then
    echo "✓ Python virtual environment exists"
else
    echo "✗ Python virtual environment missing"
    ((errors++))
fi

# Test 5: Test CLI command availability
if command -v simpledownloader &> /dev/null; then
    echo "✓ CLI command available"
else
    echo "✗ CLI command not in PATH"
    ((errors++))
fi

echo ""
if [ $errors -eq 0 ]; then
    echo "All tests passed! Installation successful."
    exit 0
else
    echo "$errors test(s) failed. Check installation."
    exit 1
fi
```

Run with:
```bash
chmod +x test_install.sh
./test_install.sh
```

