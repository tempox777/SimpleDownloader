#!/usr/bin/env python3
"""
Modern macOS-style GUI for yt-dlp downloader
Beautiful, rounded, bubbly interface with dark mode
"""
import os
import sys
import threading
import shutil
from typing import Optional, Dict, Any, List
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import io
import urllib.request

try:
    import yt_dlp as ytdlp
except ImportError:
    print("Error: yt-dlp is not installed. Install with: pip install yt-dlp", file=sys.stderr)
    sys.exit(1)


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Custom color scheme - Deep black with white accents
COLORS = {
    "bg_primary": "#000000",      # Pure black
    "bg_secondary": "#0a0a0a",    # Very dark grey
    "bg_card": "#121212",         # Card background
    "border": "#ffffff",          # White border
    "text_primary": "#ffffff",    # White text
    "text_secondary": "#a0a0a0",  # Grey text
    "button_bg": "#000000",       # Black button
    "button_hover": "#2a2a2a",    # Light grey on hover
    "accent": "#ffffff",          # White accent
    "accent_hover": "#e0e0e0",    # Slightly dimmed white
}


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Downloader")
        self.geometry("900x750")
        self.minsize(800, 600)
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Variables
        self.output_dir = ctk.StringVar(value=str(Path.home() / "Downloads"))
        self.url_var = ctk.StringVar()
        self.format_choice = ctk.StringVar(value="best")
        self.resolution_var = ctk.StringVar(value="1080p")
        self.audio_format_var = ctk.StringVar(value="mp3")
        self.container_var = ctk.StringVar(value="mp4")
        self.video_info: Optional[Dict[str, Any]] = None
        self.downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with padding
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            main_frame, 
            text="🎬 SimpleDownloader",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.grid(row=0, column=0, pady=(0, 20))
        
        # URL Section
        url_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=15,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["bg_secondary"]
        )
        url_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        url_frame.grid_columnconfigure(0, weight=1)
        
        url_label = ctk.CTkLabel(
            url_frame,
            text="Video URL",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        url_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
        
        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="Paste YouTube or video URL here...",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_secondary"],
            border_width=1,
            border_color=COLORS["text_secondary"],
            text_color=COLORS["text_primary"]
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        
        paste_btn = ctk.CTkButton(
            url_frame,
            text="📋 Paste",
            width=80,
            height=40,
            corner_radius=10,
            command=self.paste_from_clipboard,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        paste_btn.grid(row=1, column=1, padx=(0, 20), pady=(0, 15))
        
        # Info Section (for video thumbnail and details)
        self.info_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=15,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["bg_secondary"]
        )
        self.info_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.info_frame.grid_columnconfigure(1, weight=1)
        
        self.thumbnail_label = ctk.CTkLabel(self.info_frame, text="")
        self.thumbnail_label.grid(row=0, column=0, padx=20, pady=15, rowspan=3)
        
        self.title_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
            wraplength=500,
            text_color=COLORS["text_primary"]
        )
        self.title_label.grid(row=0, column=1, sticky="w", padx=(10, 20), pady=(15, 5))
        
        self.duration_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color=COLORS["text_secondary"]
        )
        self.duration_label.grid(row=1, column=1, sticky="w", padx=(10, 20), pady=2)
        
        fetch_info_btn = ctk.CTkButton(
            self.info_frame,
            text="🔍 Fetch Info",
            height=35,
            corner_radius=10,
            command=self.fetch_video_info,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        fetch_info_btn.grid(row=2, column=1, sticky="w", padx=(10, 20), pady=(5, 15))
        
        # Options Section
        options_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=15,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["bg_secondary"]
        )
        options_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        options_frame.grid_columnconfigure((0, 1), weight=1)
        
        options_label = ctk.CTkLabel(
            options_frame,
            text="Download Options",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        options_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 10))
        
        # Format choice
        format_label = ctk.CTkLabel(
            options_frame, 
            text="Format:", 
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"]
        )
        format_label.grid(row=1, column=0, sticky="w", padx=(20, 10), pady=5)
        
        self.format_menu = ctk.CTkSegmentedButton(
            options_frame,
            values=["best", "resolution", "audio-only"],
            variable=self.format_choice,
            command=self.on_format_change,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_secondary"],
            selected_color=COLORS["button_hover"],
            selected_hover_color=COLORS["text_secondary"],
            unselected_color=COLORS["button_bg"],
            unselected_hover_color=COLORS["bg_secondary"],
            text_color=COLORS["text_primary"],
            border_width=1
        )
        self.format_menu.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=5)
        
        # Resolution selector (conditionally visible)
        self.resolution_label = ctk.CTkLabel(
            options_frame,
            text="Resolution:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"]
        )
        self.resolution_label.grid(row=2, column=0, sticky="w", padx=(20, 10), pady=5)
        
        self.resolution_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["2160p", "1440p", "1080p", "720p", "480p", "360p"],
            variable=self.resolution_var,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color=COLORS["button_bg"],
            button_color=COLORS["button_bg"],
            button_hover_color=COLORS["button_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["button_hover"],
            text_color=COLORS["text_primary"],
            dropdown_text_color=COLORS["text_primary"]
        )
        self.resolution_menu.grid(row=2, column=1, sticky="ew", padx=(0, 20), pady=5)
        self.resolution_label.grid_remove()
        self.resolution_menu.grid_remove()
        
        # Audio format selector (conditionally visible)
        self.audio_format_label = ctk.CTkLabel(
            options_frame,
            text="Audio Format:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"]
        )
        self.audio_format_label.grid(row=3, column=0, sticky="w", padx=(20, 10), pady=5)
        
        self.audio_format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["mp3", "m4a", "opus", "flac", "aac"],
            variable=self.audio_format_var,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color=COLORS["button_bg"],
            button_color=COLORS["button_bg"],
            button_hover_color=COLORS["button_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["button_hover"],
            text_color=COLORS["text_primary"],
            dropdown_text_color=COLORS["text_primary"]
        )
        self.audio_format_menu.grid(row=3, column=1, sticky="ew", padx=(0, 20), pady=5)
        self.audio_format_label.grid_remove()
        self.audio_format_menu.grid_remove()
        
        # Container format
        container_label = ctk.CTkLabel(
            options_frame,
            text="Container:",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_primary"]
        )
        container_label.grid(row=4, column=0, sticky="w", padx=(20, 10), pady=(5, 15))
        
        container_menu = ctk.CTkOptionMenu(
            options_frame,
            values=["mp4", "mkv", "webm"],
            variable=self.container_var,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color=COLORS["button_bg"],
            button_color=COLORS["button_bg"],
            button_hover_color=COLORS["button_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_hover_color=COLORS["button_hover"],
            text_color=COLORS["text_primary"],
            dropdown_text_color=COLORS["text_primary"]
        )
        container_menu.grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=(5, 15))
        
        # Output directory
        output_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=15,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["bg_secondary"]
        )
        output_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        output_frame.grid_columnconfigure(0, weight=1)
        
        output_label = ctk.CTkLabel(
            output_frame,
            text="Save Location",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        output_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
        
        output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["bg_secondary"],
            border_width=1,
            border_color=COLORS["text_secondary"],
            text_color=COLORS["text_primary"]
        )
        output_entry.grid(row=1, column=0, sticky="ew", padx=(20, 10), pady=(0, 15))
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="📁 Browse",
            width=100,
            height=40,
            corner_radius=10,
            command=self.browse_directory,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        browse_btn.grid(row=1, column=1, padx=(0, 20), pady=(0, 15))
        
        # Progress section
        progress_frame = ctk.CTkFrame(
            main_frame, 
            corner_radius=15,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["bg_secondary"]
        )
        progress_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            corner_radius=10,
            height=20,
            fg_color=COLORS["bg_secondary"],
            progress_color=COLORS["border"]
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 5))
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to download",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.grid(row=1, column=0, padx=20, pady=(0, 15))
        
        # Download button
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="⬇️ Download",
            height=50,
            corner_radius=12,
            command=self.start_download,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["button_bg"],
            hover_color=COLORS["button_hover"],
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.download_btn.grid(row=6, column=0, sticky="ew")
        
    def on_format_change(self, value):
        if value == "resolution":
            self.resolution_label.grid()
            self.resolution_menu.grid()
            self.audio_format_label.grid_remove()
            self.audio_format_menu.grid_remove()
        elif value == "audio-only":
            self.resolution_label.grid_remove()
            self.resolution_menu.grid_remove()
            self.audio_format_label.grid()
            self.audio_format_menu.grid()
        else:  # best
            self.resolution_label.grid_remove()
            self.resolution_menu.grid_remove()
            self.audio_format_label.grid_remove()
            self.audio_format_menu.grid_remove()
    
    def paste_from_clipboard(self):
        try:
            clipboard = self.clipboard_get()
            self.url_var.set(clipboard)
        except Exception:
            self.update_status("Failed to paste from clipboard", error=True)
    
    def browse_directory(self):
        directory = filedialog.askdirectory(initialdir=self.output_dir.get())
        if directory:
            self.output_dir.set(directory)
    
    def update_status(self, message: str, error: bool = False):
        color = ("#ef4444", "#ef4444") if error else COLORS["text_secondary"]
        self.status_label.configure(text=message, text_color=color)
    
    def fetch_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            self.update_status("Please enter a URL first", error=True)
            return
        
        self.update_status("Fetching video information...")
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()
    
    def _fetch_info_thread(self, url: str):
        try:
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "skip_download": True,
            }
            with ytdlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info
                
                # Update UI in main thread
                self.after(0, self._update_video_info_ui, info)
        except Exception as e:
            self.after(0, self.update_status, f"Error: {str(e)}", True)
    
    def _update_video_info_ui(self, info: Dict[str, Any]):
        # Update title
        title = info.get("title", "Unknown")
        self.title_label.configure(text=title)
        
        # Update duration
        duration = info.get("duration")
        if duration:
            minutes, seconds = divmod(int(duration), 60)
            hours, minutes = divmod(minutes, 60)
            if hours > 0:
                duration_str = f"Duration: {hours}h {minutes}m {seconds}s"
            else:
                duration_str = f"Duration: {minutes}m {seconds}s"
        else:
            duration_str = "Duration: Unknown"
        
        uploader = info.get("uploader", "")
        if uploader:
            duration_str += f" • {uploader}"
        
        self.duration_label.configure(text=duration_str)
        
        # Try to load thumbnail
        thumbnail_url = info.get("thumbnail")
        if thumbnail_url:
            threading.Thread(target=self._load_thumbnail, args=(thumbnail_url,), daemon=True).start()
        
        # Update available resolutions
        heights = self._get_available_heights(info)
        if heights:
            res_options = [f"{h}p" for h in heights]
            self.resolution_menu.configure(values=res_options)
            if res_options:
                self.resolution_var.set(res_options[0])
        
        self.update_status("Video information loaded successfully")
    
    def _get_available_heights(self, info: Dict[str, Any]) -> List[int]:
        heights = set()
        for f in info.get("formats", []):
            if (f.get("vcodec") not in (None, "none")) and f.get("height"):
                heights.add(int(f["height"]))
        return sorted(heights, reverse=True)
    
    def _load_thumbnail(self, url: str):
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                image_data = response.read()
            
            image = Image.open(io.BytesIO(image_data))
            # Resize to fit
            image.thumbnail((120, 90), Image.Resampling.LANCZOS)
            
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            self.after(0, self.thumbnail_label.configure, {"image": ctk_image})
        except Exception:
            pass  # Silently fail for thumbnails
    
    def start_download(self):
        if self.downloading:
            return
        
        url = self.url_var.get().strip()
        if not url:
            self.update_status("Please enter a URL", error=True)
            return
        
        output_dir = self.output_dir.get()
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.update_status(f"Error creating directory: {e}", error=True)
                return
        
        self.downloading = True
        self.download_btn.configure(state="disabled", text="⏳ Downloading...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._download_thread, args=(url, output_dir), daemon=True).start()
    
    def _download_thread(self, url: str, output_dir: str):
        try:
            ydl_opts = {
                "noplaylist": True,
                "outtmpl": os.path.join(output_dir, "%(title)s [%(id)s].%(ext)s"),
                "progress_hooks": [self._progress_hook],
                "quiet": False,
                "no_warnings": True,
            }
            
            # Configure format based on selection
            format_choice = self.format_choice.get()
            
            if format_choice == "best":
                ydl_opts["format"] = "bv*+ba/b"
                ydl_opts["merge_output_format"] = self.container_var.get()
            elif format_choice == "resolution":
                resolution = int(self.resolution_var.get().replace("p", ""))
                ydl_opts["format"] = f"bv*[height={resolution}]+ba/b[height={resolution}]"
                ydl_opts["merge_output_format"] = self.container_var.get()
                if not self._has_ffmpeg():
                    self.after(0, self.update_status, "Warning: ffmpeg not found, merging may fail", True)
            elif format_choice == "audio-only":
                if not self._has_ffmpeg():
                    self.after(0, self.update_status, "Error: ffmpeg required for audio extraction", True)
                    self.after(0, self._download_complete, False)
                    return
                
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format_var.get(),
                    "preferredquality": "0",
                }]
            
            with ytdlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.after(0, self._download_complete, True)
        except Exception as e:
            self.after(0, self.update_status, f"Download failed: {str(e)}", True)
            self.after(0, self._download_complete, False)
    
    def _progress_hook(self, d):
        if d["status"] == "downloading":
            try:
                if "total_bytes" in d:
                    progress = d["downloaded_bytes"] / d["total_bytes"]
                elif "total_bytes_estimate" in d:
                    progress = d["downloaded_bytes"] / d["total_bytes_estimate"]
                else:
                    progress = 0
                
                self.after(0, self.progress_bar.set, progress)
                
                # Update status with speed and ETA
                speed = d.get("speed")
                eta = d.get("eta")
                status_parts = []
                
                if speed:
                    speed_mb = speed / 1024 / 1024
                    status_parts.append(f"{speed_mb:.1f} MB/s")
                
                if eta:
                    minutes, seconds = divmod(int(eta), 60)
                    if minutes > 0:
                        status_parts.append(f"ETA: {minutes}m {seconds}s")
                    else:
                        status_parts.append(f"ETA: {seconds}s")
                
                if status_parts:
                    self.after(0, self.update_status, " • ".join(status_parts))
                else:
                    self.after(0, self.update_status, "Downloading...")
                    
            except Exception:
                pass
        elif d["status"] == "finished":
            self.after(0, self.update_status, "Processing...")
            self.after(0, self.progress_bar.set, 1.0)
    
    def _download_complete(self, success: bool):
        self.downloading = False
        self.download_btn.configure(state="normal", text="⬇️ Download")
        
        if success:
            self.progress_bar.set(1.0)
            self.update_status("✅ Download completed successfully!")
        else:
            self.progress_bar.set(0)
    
    @staticmethod
    def _has_ffmpeg() -> bool:
        return shutil.which("ffmpeg") is not None


def main():
    app = DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()

