"""
Satyajit Ray Films Downloader
------------------------------
This script scrapes and downloads Satyajit Ray films from a specified website.

pip install internetarchive

Run the script inside proxmox server. copy the files to the LXC file location.

"""
from internetarchive import download

identifier = "satyajit-ray-films"

download(
    identifier,
    glob_pattern="*1080p*.mp4",
    verbose=True,
    destdir="data/Satyajit Ray Films",
)