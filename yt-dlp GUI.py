import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser
import yt_dlp
import subprocess
import os
import json
import sys
import threading

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.json")
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "settings.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "history.json")
version = "Yt-dlp GUI 1.1"
logo = "logo.ico"

class SettingsWindow:
    def __init__(self, root, apply_theme_callback=None):
        self.root = root
        self.apply_theme_callback = apply_theme_callback
        self.settings_window = tk.Toplevel(root)
        self.settings_window.title("Settings")
        self.settings_window.geometry("400x300")
        
        self.logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo)

        # Ensure the file exists before setting the icon
        if os.path.exists(self.logo):
            self.settings_window.iconbitmap(self.logo)
        else:
            print("Warning: logo.ico not found. Skipping icon setup.")
        
        self.load_settings()
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        self.download_limit_var = tk.BooleanVar(value=self.settings.get("download_limit_enabled", False))
        self.download_limit_value = tk.StringVar(value=str(self.settings.get("download_limit", 1)))
        self.ffmpeg_format_var = tk.StringVar(value=self.settings.get("ffmpeg_format", "mp4"))
        
        ttk.Label(self.settings_window, text="Theme:").pack(pady=5)
        ttk.Radiobutton(self.settings_window, text="Light Mode", variable=self.theme_var, value="light").pack()
        ttk.Radiobutton(self.settings_window, text="Dark Mode", variable=self.theme_var, value="dark").pack()
        
        self.download_limit_check = ttk.Checkbutton(
            self.settings_window, text="Enable Download Limit", variable=self.download_limit_var, command=self.toggle_limit_input
        )
        self.download_limit_check.pack(pady=5)
        
        self.download_limit_entry = ttk.Entry(self.settings_window, textvariable=self.download_limit_value, state="disabled")
        self.download_limit_entry.pack(pady=5)
        
        ttk.Label(self.settings_window, text="FFmpeg Format:").pack(pady=5)
        self.ffmpeg_format_menu = ttk.Combobox(
            self.settings_window, textvariable=self.ffmpeg_format_var, values=["mp4", "mp3", "webm"], state="readonly"
        )
        self.ffmpeg_format_menu.pack()
        
        ttk.Button(self.settings_window, text="Save Settings", command=self.save_settings).pack(pady=10)
    
    def toggle_limit_input(self):
        if self.download_limit_var.get():
            self.download_limit_entry.config(state="normal")
        else:
            self.download_limit_entry.config(state="disabled")
    
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
    
    def save_settings(self):
        self.settings["theme"] = self.theme_var.get()
        self.settings["download_limit_enabled"] = self.download_limit_var.get()
        self.settings["download_limit"] = int(self.download_limit_value.get()) if self.download_limit_var.get() else None
        self.settings["ffmpeg_format"] = self.ffmpeg_format_var.get()
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)
        
        self.apply_theme_callback(self.theme_var.get())
        self.settings_window.destroy()
    
    def apply_theme(self):
        self.apply_theme_callback(self.theme_var.get())

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title(version)
        self.root.geometry("500x550")
        self.root.configure(bg="#2e2e2e")
        
        self.logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo)

        # Ensure the file exists before setting the icon
        if os.path.exists(self.logo):
            self.root.iconbitmap(self.logo)
        else:
            print("Warning: logo.ico not found. Skipping icon setup.")

        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", background="#444", foreground="white")
        style.configure("TLabel", background="#2e2e2e", foreground="white")
        style.configure("TEntry", fieldbackground="#444", foreground="white")
        
        self.load_config()

        self.load_settings()
        self.apply_theme(self.settings.get("theme", "dark"))
        
        self.create_widgets()
    
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = {}
    
    def apply_theme(self, theme):
        style = ttk.Style()
        if theme == "light":
            self.root.configure(bg="white")
            style.configure("TButton", background="#ddd", foreground="black")
            style.configure("TLabel", background="white", foreground="black")
            style.configure("TEntry", fieldbackground="#ddd", foreground="black")
        else:
            self.root.configure(bg="#2e2e2e")
            style.configure("TButton", background="#444", foreground="white")
            style.configure("TLabel", background="#2e2e2e", foreground="white")
            style.configure("TEntry", fieldbackground="#444", foreground="white")

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
    
    def save_config(self):
        self.config["save_path"] = self.path_entry.get()
        self.config["yt_dlp_path"] = self.exe_entry.get()
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def create_widgets(self):
        self.settings_button = ttk.Button(self.root, text="Settings", command=self.open_settings)
        self.settings_button.place(x=10, y=10, anchor="nw")

        self.history_button = ttk.Button(self.root, text="History", command=self.show_history)
        self.history_button.pack(side="top", pady=10)
        
        self.url_label = ttk.Label(self.root, text="Video URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = ttk.Entry(self.root, width=50)
        self.url_entry.pack(pady=5)
        
        self.path_label = ttk.Label(self.root, text="Save Location:")
        self.path_label.pack(pady=5)
        
        self.path_entry = ttk.Entry(self.root, width=50)
        self.path_entry.insert(0, self.config.get("save_path", ""))
        self.path_entry.pack(pady=5)
        
        self.browse_button = ttk.Button(self.root, text="Browse", command=self.browse_path)
        self.browse_button.pack(pady=5)
        
        self.format_label = ttk.Label(self.root, text="Select Format:")
        self.format_label.pack(pady=5)
        
        self.format_var = tk.StringVar(value="mp4")
        self.format_menu = ttk.Combobox(self.root, textvariable=self.format_var, values=["mp4", "mp3"], state="readonly")
        self.format_menu.pack(pady=5)
        self.format_menu.bind("<<ComboboxSelected>>", self.toggle_resolution_options)
        
        self.resolution_label = ttk.Label(self.root, text="Select Resolution:")
        self.resolution_label.pack(pady=5)
        
        self.resolution_var = tk.StringVar(value="best")
        self.resolution_menu = ttk.Combobox(self.root, textvariable=self.resolution_var, values=["144p", "360p", "480p", "720p", "1080p", "best"], state="readonly")
        self.resolution_menu.pack(pady=5)
        
        self.download_button = ttk.Button(self.root, text="Download", command=self.download_video)
        self.download_button.pack(pady=10)
        
        self.exe_label = ttk.Label(self.root, text="yt-dlp.exe Path (Optional):")
        self.exe_label.pack(pady=5)
        
        self.exe_entry = ttk.Entry(self.root, width=50)
        self.exe_entry.insert(0, self.config.get("yt_dlp_path", ""))
        self.exe_entry.pack(pady=5)
        
        self.browse_exe_button = ttk.Button(self.root, text="Browse", command=self.browse_exe)
        self.browse_exe_button.pack(pady=5)
        
        self.credit_button = ttk.Button(self.root, text="Credits", command=self.show_credits)
        self.credit_button.place(x=10, rely=1.0, anchor="sw")
    
    def browse_path(self):
        folder_selected = filedialog.askdirectory()
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, folder_selected)
        self.save_config()
    
    def browse_exe(self):
        file_selected = filedialog.askopenfilename(filetypes=[["Executable", "*.exe"]])
        self.exe_entry.delete(0, tk.END)
        self.exe_entry.insert(0, file_selected)
        self.save_config()
    
    def toggle_resolution_options(self, event=None):
        if self.format_var.get() == "mp3":
            self.resolution_label.pack_forget()
            self.resolution_menu.pack_forget()
        else:
            self.resolution_label.pack(pady=5)
            self.resolution_menu.pack(pady=5)
    
    def show_success_window(self, file_path):
        success_window = tk.Toplevel(self.root)
        success_window.title("Download Complete")
        success_window.geometry("350x150")

        ttk.Label(success_window, text="Download Complete!", font=("Arial", 12)).pack(pady=10)

        def open_folder():
            folder_path = os.path.dirname(file_path)
            if os.name == "nt":
                os.startfile(folder_path)  # Windows
            else:
                subprocess.run(["xdg-open", folder_path] if os.name == "posix" else ["open", folder_path])

        def play_video():
            if os.path.exists(file_path):
                if os.name == "nt":
                    os.startfile(file_path)
                else:
                    subprocess.run(["xdg-open", file_path] if os.name == "posix" else ["open", file_path])
            else:
                messagebox.showerror("Error", "File not found!")

          # ✅ Create a frame to align buttons horizontally
        button_frame = ttk.Frame(success_window)
        button_frame.pack(pady=5)  # Add some space below the label

        ttk.Button(success_window, text="Open Folder", command=open_folder).pack(side="left", padx=5, pady=5)
        ttk.Button(success_window, text="Play Video", command=play_video).pack(side="left", padx=5, pady=5)
        ttk.Button(success_window, text="Close", command=success_window.destroy).pack(side="left", padx=5, pady=5)

    def show_progress_window(self):
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Downloading...")
        self.progress_window.geometry("300x120")
    
        self.progress_label = ttk.Label(self.progress_window, text="Downloading...", font=("Arial", 10))
        self.progress_label.pack(pady=10)

        self.info_label = ttk.Label(self.progress_window, 
                                text="The video will turn into a WebM video as of this GUI's version.\nFuture updates coming soon!", 
                                font=("Arial", 9), wraplength=320, justify="center")
        self.info_label.pack(pady=5)
    

        self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=250, mode="indeterminate")
        self.progress_bar.pack(pady=5)
        self.progress_bar.start()
    
    def download_video(self):
        # Start the download process in a separate thread
        threading.Thread(target=self.download_process, daemon=True).start()

    def download_process(self):
        # The actual download logic, running in a separate thread
        url = self.url_entry.get().split(",")
        save_path = self.path_entry.get()
        resolution = self.resolution_var.get()

        if not url or not save_path:
            messagebox.showerror("Error", "Please provide both URL and save location")
            return

        self.show_progress_window()  # Show progress before downloading

        format_map = {
           "144p": "bestvideo[height<=144]+bestaudio/best",
           "360p": "bestvideo[height<=360]+bestaudio/best",
           "480p": "bestvideo[height<=480]+bestaudio/best",
           "720p": "bestvideo[height<=720]+bestaudio/best",
           "1080p": "bestvideo[height<=1080]+bestaudio/best",
           "best": "best"
    }

        output_template = os.path.join(save_path, "%(title)s.%(ext)s")
        ydl_opts = {
           'outtmpl': output_template,
           'format': format_map.get(resolution, "best"),
           'noplaylist': True
    }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = output_template % {'title': info['title'], 'ext': info['ext']}

            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, self.progress_window.destroy)
            self.root.after(0, lambda: self.show_success_window(file_path))

        except Exception as e:
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, self.progress_window.destroy)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to download: {e}"))

    def open_settings(self):
        SettingsWindow(self.root, self.apply_theme)

    def save_history(self):
        history_entry = {"video_url": self.url_entry.get()}
        try:
            with open(HISTORY_FILE, "r") as f:
                history_data = json.load(f)
        except FileNotFoundError:
            history_data = []
        
        history_data.append(history_entry)
        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Download History")
        history_window.geometry("400x300")
        
        history_window.logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), logo)

        # Ensure the file exists before setting the icon
        if os.path.exists(self.logo):
            history_window.iconbitmap(self.logo)
        else:
            print("Warning: logo.ico not found. Skipping icon setup.")
        
        try:
            with open(HISTORY_FILE, "r") as f:
                history_data = json.load(f)
        except FileNotFoundError:
            history_data = []
        
        history_text = "\n".join([entry["video_url"] for entry in history_data]) if history_data else "No history available."
        
        history_label = tk.Label(history_window, text=history_text, justify="left")
        history_label.pack(pady=10)
    
    def show_credits(self):
        messagebox.showinfo("Credits", version + "\nDeveloped by: Nofal Samadi\nSpecial thanks to: Myself and the yt-dll for moral support")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
