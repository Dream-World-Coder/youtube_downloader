#!/usr/bin/env python3

import yt_dlp
import os
import subprocess
import sys

def update_ytdlp():
  """Update yt-dlp using pip."""
  print("Updating yt-dlp...")
  try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
    print("yt-dlp updated successfully.")
  except Exception as e:
    print(f"Failed to update yt-dlp: {e}")

def download_video():
  url = input("Enter YouTube URL: ").strip()
  video_choice = input("Download video? [0 = No, 1 = Yes]: ").strip()
  audio_choice = input("Download audio? [0 = No, 1 = Yes]: ").strip()

  out_dir = os.path.join(os.getcwd(), "downloads")
  os.makedirs(out_dir, exist_ok=True)

  if video_choice == "1" and audio_choice == "1":
    ydl_opts = {
      "format": "bestvideo+bestaudio/best",
      "merge_output_format": "mp4",
      "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
    }
  elif video_choice == "1" and audio_choice == "0":
    ydl_opts = {
      "format": "bestvideo",
      "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
    }
  elif video_choice == "0" and audio_choice == "1":
    ydl_opts = {
      "format": "bestaudio/best",
      "postprocessors": [
        {
          "key": "FFmpegExtractAudio",
          "preferredcodec": "mp3",
          "preferredquality": "192",
        }
      ],
      "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
    }
  else:
    print("Both video and audio set to 0. Nothing to download.")
    return

  # Try downloading once, update on failure, retry once
  for attempt in range(2):
    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
      print("Download completed successfully.")
      return
    except Exception as e:
      print(f"Download failed (attempt {attempt+1}): {e}")
      if attempt == 0:  # only update and retry once
        update_ytdlp()
      else:
        print("Second attempt failed. Quitting.")
        return

if __name__ == "__main__":
  download_video()
