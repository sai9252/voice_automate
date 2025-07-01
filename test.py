from pathlib import Path
import os

directory_path = r"C:\Users\M sai\Downloads"


audio_extensions = ['.mp3']
audio_files = []

directory = Path(directory_path)
if not directory.exists():
    raise FileNotFoundError(f"Directory not found: {directory_path}")

first_audio_files = [i for i in directory.glob("*.mp3")][0]
# print(f"Found {len(all_audio_files)} audio files in directory: {directory_path}")
print("Audio file:", first_audio_files)
print(first_audio_files.suffix)
print(first_audio_files.stat())
# print(first_audio_files)


# for ext in audio_extensions:
#     audio_files.extend(directory.glob(f"*{ext}"))
#     audio_files.extend(directory.glob(f"*{ext.upper()}"))

# if not audio_files:
#     raise FileNotFoundError(f"No audio files found in directory: {directory_path}")

# # Sort files for consistent ordering
# audio_files.sort()
