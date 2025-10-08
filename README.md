# SimpleDownloader

A GUI and CLI application for downloading videos and audio using yt-dlp.

## Installation

### One-Line Install (Recommended)

This installs SimpleDownloader system-wide and adds it to your application launcher:

```bash
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/install.sh | sudo sh
```

**What it does:**
- Installs system dependencies (python, ffmpeg, tk)
- Installs the application to `/opt/SimpleDownloader`
- Creates desktop launcher entry
- Creates CLI commands: `simpledownloader` and `simpledownloader-gui`

**Supported distributions:**
- Arch Linux, Manjaro, EndeavourOS
- Ubuntu, Debian, Linux Mint, Pop!_OS
- Fedora, RHEL, CentOS
- openSUSE

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/uninstall.sh | sudo sh
```

This removes all files, desktop entries, and launchers.

---

## Usage

### GUI

**Option 1:** Open your application launcher and search for "SimpleDownloader"

**Option 2:** Run from terminal:
```bash
simpledownloader-gui
```

**Steps:**
1. Paste video URL into the input field
2. Click "Fetch Info" to preview video details
3. Select format:
   - `best` - Highest quality video and audio
   - `resolution` - Choose specific resolution (2160p, 1440p, 1080p, 720p, 480p, 360p)
   - `audio-only` - Extract audio (MP3, M4A, OPUS, FLAC, AAC)
4. Select save location
5. Click Download

### CLI

**Interactive mode:**
```bash
simpledownloader https://youtube.com/watch?v=VIDEO_ID --interactive
```

**Direct download:**
```bash
# Download best quality
simpledownloader https://youtube.com/watch?v=VIDEO_ID

# Specific resolution with audio
simpledownloader https://youtube.com/watch?v=VIDEO_ID --resolution 1080 --with-audio

# Audio only
simpledownloader https://youtube.com/watch?v=VIDEO_ID --audio-only --audio-format mp3

# List available formats
simpledownloader https://youtube.com/watch?v=VIDEO_ID --list

# Custom output directory
simpledownloader https://youtube.com/watch?v=VIDEO_ID --outdir ~/Videos

# Specify container format
simpledownloader https://youtube.com/watch?v=VIDEO_ID --prefer-container mkv
```

**Available options:**
```
--interactive              Interactive format selection
--list                     List all formats and exit
--resolution HEIGHT        Target resolution (e.g., 1080)
--with-audio              Include audio (with --resolution)
--video-only              Video only (with --resolution)
--audio-only              Download audio only
--audio-format FORMAT     mp3, m4a, opus, flac, aac (default: m4a)
--prefer-container TYPE   mp4, mkv, webm
--outdir DIR              Output directory
--output TEMPLATE         Custom filename template
--allow-playlist          Process playlists
```

---

## Building from Source

### Install Dependencies

**Arch Linux:**
```bash
sudo pacman -S python python-pip tk ffmpeg git
```

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv python3-tk ffmpeg git
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip python3-tkinter ffmpeg git
```

**openSUSE:**
```bash
sudo zypper install python3 python3-pip python3-tk ffmpeg git
```

### Clone and Setup

```bash
git clone https://github.com/tempox777/SimpleDownloader.git
cd SimpleDownloader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

**GUI mode:**
```bash
python3 DownloaderGUI.py
```

**CLI mode:**
```bash
python3 Downloader.py <URL>
```

### Create Desktop Entry (Optional)

```bash
sudo cp simpledownloader.desktop /usr/share/applications/
sudo update-desktop-database /usr/share/applications/
```

Edit the desktop file to update the `Exec` path to your installation location.

---

## Troubleshooting

### Application not in launcher after install

**Solution 1:** Log out and log back in

**Solution 2:** Manually update the desktop database:
```bash
sudo update-desktop-database /usr/share/applications/
```

**Solution 3:** If using Wayland/Hyprland, restart your compositor

### "ffmpeg not found" error

ffmpeg is required for audio extraction and merging video/audio streams.

**Install ffmpeg:**
```bash
# Arch
sudo pacman -S ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

### "tkinter not found" error

**Arch:**
```bash
sudo pacman -S tk
```

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Verify installation:**
```bash
python3 -c "import tkinter"
```

If no error appears, tkinter is installed correctly.

### Download fails with error

**Update yt-dlp:**

If installed system-wide:
```bash
sudo /opt/SimpleDownloader/.venv/bin/pip install --upgrade yt-dlp
```

If running from source:
```bash
source .venv/bin/activate
pip install --upgrade yt-dlp
```

**Check if site is supported:**

Visit the [yt-dlp supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

### Permission errors during installation

The install script must be run with sudo:
```bash
curl -fsSL https://raw.githubusercontent.com/tempox777/SimpleDownloader/main/install.sh | sudo sh
```

### Installation fails on unknown distribution

Manually install dependencies:
```bash
# Install these packages using your package manager:
- python3
- python3-pip
- python3-venv
- python3-tk (or python3-tkinter)
- ffmpeg
- git
```

Then run the install script, which will skip dependency installation but continue with the application setup.

### CLI commands not found after installation

Add `/usr/local/bin` to your PATH:

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

For zsh users:
```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### GUI shows blank window or crashes

**Check Python version:**
```bash
python3 --version
```

Requires Python 3.7 or higher.

**Check CustomTkinter installation:**
```bash
/opt/SimpleDownloader/.venv/bin/python -c "import customtkinter"
```

If error occurs, reinstall:
```bash
sudo /opt/SimpleDownloader/.venv/bin/pip install --upgrade customtkinter
```

### Cannot download age-restricted or private videos

This is a limitation of yt-dlp. Options:

1. Use browser cookies:
```bash
simpledownloader URL --cookies-from-browser firefox
```

2. Provide authentication (site-dependent):
```bash
simpledownloader URL --username YOUR_USERNAME --password YOUR_PASSWORD
```

---

## Supported Sites

Over 1000 sites supported including:
- YouTube
- Vimeo
- Dailymotion
- Twitter/X
- Reddit
- TikTok
- Twitch
- SoundCloud
- Instagram
- Facebook

Full list: [yt-dlp supported sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Requirements

- Python 3.7+
- ffmpeg (for audio extraction and merging)
- tkinter (for GUI)
- Internet connection
- Sufficient disk space

---

## Technical Details

**Components:**
- `DownloaderGUI.py` - GUI application using CustomTkinter
- `Downloader.py` - CLI tool with yt-dlp wrapper
- `install.sh` - System-wide installation script
- `uninstall.sh` - Removal script
- `requirements.txt` - Python dependencies

**Dependencies:**
- yt-dlp (download engine)
- customtkinter (GUI framework)
- Pillow (image processing)

**Installation locations:**
- Application: `/opt/SimpleDownloader`
- Launchers: `/usr/local/bin/simpledownloader`, `/usr/local/bin/simpledownloader-gui`
- Desktop entry: `/usr/share/applications/simpledownloader.desktop`

---

## License

MIT License

---

## Contributing

Bug reports, feature requests, and pull requests are welcome at:
https://github.com/tempox777/SimpleDownloader

---

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://python-pillow.org/)
