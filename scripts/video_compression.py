import os
import sys
import subprocess
from pathlib import Path

def compress_video(input_path: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{input_path.stem}_720p.mp4"

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", "scale=-2:720",
        # "-c:v", "libx264",
        "-c:v", "h264_nvenc",
        "-preset", "slow",
        "-crf", "24",
        "-maxrate", "2M",
        "-bufsize", "4M",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ac", "2",
        str(output_file)
    ]

    print(f"🎬 Compressing: {input_path.name}")
    subprocess.run(cmd, check=True)

def process_path(path: Path):
    output_dir = path.parent / "compressed"

    if path.is_file():
        if path.suffix.lower() in [".mp4", ".mkv"]:
            compress_video(path, output_dir)
        else:
            print(f"❌ Unsupported file: {path}")
    elif path.is_dir():
        for file in path.iterdir():
            if file.suffix.lower() in [".mp4", ".mkv"]:
                compress_video(file, output_dir)
    else:
        print("❌ Invalid path")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_videos.py <file_or_folder>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    process_path(input_path)
