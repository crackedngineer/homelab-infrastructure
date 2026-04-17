import subprocess

url = "https://youtu.be/t822he3vtLE"

cmd = [
    "yt-dlp",
    "--download-sections", "*0-57",
    "-f", "bv*+ba/b",
    "--merge-output-format", "mp4",
    "--force-keyframes-at-cuts",
    "-o", "%(title)s_clip.%(ext)s",
    url
]

subprocess.run(cmd)