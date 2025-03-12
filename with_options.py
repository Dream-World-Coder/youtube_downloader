import logging
import yt_dlp
import tkinter as tk
from tkinter import messagebox, ttk
import os
import threading

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("450x500")

        self.label = tk.Label(root, text="\nEnter the YouTube URL:\n[press Enter/ Return to download]", font=('Arial', 10, 'bold'))
        self.label.pack(pady=10)

        self.url_entry = tk.Entry(root, width=40)
        self.url_entry.pack(pady=10)
        self.url_entry.bind("<Return>", lambda event: self.start_download_thread())

        # Download options frame
        self.options_frame = tk.Frame(root)
        self.options_frame.pack(pady=5)

        self.download_option = tk.StringVar(value="both")  # Default to both

        self.label_options = tk.Label(self.options_frame, text="Download Options:")
        self.label_options.pack(anchor=tk.W)

        self.radio_both = tk.Radiobutton(self.options_frame, text="Video & Audio", value="both", variable=self.download_option)
        self.radio_both.pack(anchor=tk.W)

        self.radio_video = tk.Radiobutton(self.options_frame, text="Video Only", value="video", variable=self.download_option)
        self.radio_video.pack(anchor=tk.W)

        self.radio_audio = tk.Radiobutton(self.options_frame, text="Audio Only", value="audio", variable=self.download_option)
        self.radio_audio.pack(anchor=tk.W)

        # Progress bar
        self.progress_frame = tk.Frame(root)
        self.progress_frame.pack(pady=10, fill=tk.X, padx=20)

        self.progress_label = tk.Label(self.progress_frame, text="Download Progress:")
        self.progress_label.pack(anchor=tk.W)

        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=350, mode='determinate')
        self.progress_bar.pack(fill=tk.X)

        self.percentage_label = tk.Label(self.progress_frame, text="0%")
        self.percentage_label.pack(anchor=tk.E, pady=2)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=5)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.download_button = tk.Button(self.button_frame, text="Download", command=self.start_download_thread)
        self.download_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = tk.Button(self.button_frame, text="Quit", command=root.destroy)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # Flag to track download status
        self.is_downloading = False
        self.download_size = 0
        self.downloaded_bytes = 0

    def start_download_thread(self):
        if self.is_downloading:
            messagebox.showinfo("Info", "A download is already in progress")
            return

        video_url = self.url_entry.get()
        if not video_url:
            messagebox.showwarning("Input Required", "Please enter a YouTube URL")
            return

        # Disable download button during download
        self.download_button.config(state=tk.DISABLED)

        # Reset progress bar
        self.progress_bar['value'] = 0
        self.percentage_label.config(text="0%")

        download_option = self.download_option.get()
        option_text = {"both": "Video & Audio", "video": "Video Only", "audio": "Audio Only"}
        self.status_label.config(text=f"Starting download: {option_text[download_option]}...")

        # Start download in a separate thread to keep UI responsive
        download_thread = threading.Thread(target=self.download_video)
        download_thread.daemon = True
        download_thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Update download size information
            if 'total_bytes' in d and d['total_bytes'] > 0:
                self.download_size = d['total_bytes']
                self.downloaded_bytes = d['downloaded_bytes']
                percentage = min(100, (self.downloaded_bytes / self.download_size) * 100)

                # Update UI from the main thread
                self.root.after(0, lambda: self.update_progress(percentage))

            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                self.download_size = d['total_bytes_estimate']
                self.downloaded_bytes = d['downloaded_bytes']
                percentage = min(100, (self.downloaded_bytes / self.download_size) * 100)

                # Update UI from the main thread
                self.root.after(0, lambda: self.update_progress(percentage))

            else:
                # If we can't determine the total size, use downloaded bytes to show some progress
                self.root.after(0, lambda: self.update_status(f"Downloaded: {d['downloaded_bytes'] / 1024 / 1024:.1f} MB"))

        elif d['status'] == 'finished':
            # Final processing stage
            self.root.after(0, lambda: self.update_status("Processing download..."))

    def update_progress(self, percentage):
        self.progress_bar['value'] = percentage
        self.percentage_label.config(text=f"{percentage:.1f}%")
        self.status_label.config(text=f"Downloading: {self.downloaded_bytes / 1024 / 1024:.1f} MB of {self.download_size / 1024 / 1024:.1f} MB")

    def update_status(self, message):
        self.status_label.config(text=message)

    def get_ydl_format(self):
        option = self.download_option.get()
        if option == "audio":
            return "bestaudio/best"
        elif option == "video":
            return "bestvideo/best"
        else:  # both
            return "best"

    def get_file_extension(self):
        option = self.download_option.get()
        if option == "audio":
            return "%(id)s_audio.%(ext)s"
        elif option == "video":
            return "%(id)s_video.%(ext)s"
        else:  # both
            return "%(id)s_%(resolution)s.%(ext)s"

    def download_video(self):
        self.is_downloading = True
        try:
            video_url = self.url_entry.get()
            download_directory = "yt_downloads"
            os.makedirs(download_directory, exist_ok=True)

            download_option = self.download_option.get()
            ydl_opts = {
                'format': self.get_ydl_format(),
                'outtmpl': os.path.join(download_directory, self.get_file_extension()),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'noprogress': False,
            }

            # Add audio extraction for audio only option
            if download_option == "audio":
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Starting download with option: {download_option}")
                info_dict = ydl.extract_info(video_url, download=True)
                download_path = ydl.prepare_filename(info_dict)
                print(f"Downloaded at: {download_path}")
                logging.info(f"Downloaded at: {download_path}")

                # Update UI from the main thread
                self.root.after(0, lambda: self.download_completed(download_path))

        except yt_dlp.DownloadError as e:
            error_message = f"Error downloading: {e}"
            print(error_message)
            logging.error(error_message)

            # Update UI from the main thread
            self.root.after(0, lambda: self.download_failed(error_message))

        except Exception as e:
            error_message = f"Unexpected error: {e}"
            print(error_message)
            logging.error(error_message)

            # Update UI from the main thread
            self.root.after(0, lambda: self.download_failed(error_message))

        finally:
            self.is_downloading = False

    def download_completed(self, download_path):
        self.progress_bar['value'] = 100
        self.percentage_label.config(text="100%")

        option_text = {"both": "Video & Audio", "video": "Video Only", "audio": "Audio Only"}
        download_option = self.download_option.get()

        self.status_label.config(text=f"{option_text[download_option]} download complete!")

        messagebox.showinfo("Download Complete", f"{option_text[download_option]} downloaded successfully to:\n{download_path}")

        # Clear the URL entry after successful download
        self.url_entry.delete(0, tk.END)

        # Re-enable download button
        self.download_button.config(state=tk.NORMAL)

    def download_failed(self, error_message):
        self.status_label.config(text="Download failed")
        messagebox.showerror("Error", error_message)

        # Re-enable download button
        self.download_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="download.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
