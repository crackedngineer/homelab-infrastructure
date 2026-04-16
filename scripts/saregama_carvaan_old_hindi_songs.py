##########
# Script to download old Hindi songs from YouTube based on a markdown table.
# The markdown file should have a table with columns: Title, Artiste, Movie.
# The script uses yt-dlp to search and download the audio in mp3 format.
# It also creates an M3U playlist with the downloaded songs.
# Install yt-dlp: pip install yt-dlp
# Install pandas: pip install pandas
##########

import re
import os
import requests
import subprocess
import pandas as pd

# ---------- CONFIG ----------
OUTPUT_DIR = "downloads"
PLAYLIST_NAME = "playlist.m3u"
AUDIO_FORMAT = "mp3"
# ----------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_markdown_table(content: str):
    lines = content.splitlines()

    table_lines = [line.strip() for line in lines if "|" in line]

    # Remove separator line (---)
    table_lines = [line for line in table_lines if not re.match(r'^\|\s*-', line)]

    rows = []
    for line in table_lines[2:]:  # skip header
        cols = [c.strip() for c in line.strip("|").split("|")]
        song_name_match = re.search(r'\[([^\]]+)\]', cols[1])
        if len(cols) >= 3:
            rows.append({
                "song": song_name_match.group(1).lstrip() if song_name_match else cols[1],  # Remove markdown links
                "singer": cols[3],
                "film": cols[2]
            })

    return pd.DataFrame(rows)

def download_song(song, singer, film):
    query = f"{song} {singer} {film} audio"
    output_template = os.path.join(os.path.join(OUTPUT_DIR, singer, film), "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--extract-audio",
        "--audio-format", AUDIO_FORMAT,
        "--audio-quality", "0",
        "-o", output_template,
        "--quiet",
        "--no-warnings"
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"Failed: {song}")

def get_downloaded_files():
    return [
        os.path.join(OUTPUT_DIR, f)
        for f in os.listdir(OUTPUT_DIR)
        if f.endswith(f".{AUDIO_FORMAT}")
    ]

def create_playlist(files, playlist_path):
    with open(playlist_path, "w", encoding="utf-8") as f:
        for file in files:
            f.write(file + "\n")

def main():
    # Get markdown from GitHub
    songs_url = "https://raw.githubusercontent.com/labnol/saregama-carvaan/refs/heads/master/artistes/songs.md"
    response = requests.get(songs_url)
    if response.status_code == 200:
        content = response.text
    else:
        print("Failed to fetch songs list")
        return
    df = parse_markdown_table(content)

    print(f"Found {len(df)} songs")

    for _, row in df.iterrows():
        print(f"Downloading: {row['song']} by {row['singer']} from {row['film']}")
        download_song(row['song'], row['singer'], row['film'])

    files = get_downloaded_files()
    create_playlist(files, PLAYLIST_NAME)

    print("\nDone!")
    print(f"Playlist created: {PLAYLIST_NAME}")
    print("Move files + playlist into your Navidrome music folder.")

if __name__ == "__main__":
    main()