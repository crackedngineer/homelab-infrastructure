"""
Cartoon Download Script

pip install bs4 requests pytube

Install yt-dlp


PENDING
- Younfg Justice Season 1 has some videos missing from the blogspot listing.
"""

import os
import subprocess
from bs4 import BeautifulSoup
import requests
import re
from ftplib import FTP


def scrape_blogger_listing(url) -> list[dict]:
    """
    Scrape a Blogger listing page for post links and titles.
    Args:
        url (str): The URL of the Blogger listing page.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    posts = soup.find_all("div", class_="post-outer")

    # Extract links and titles
    details = []
    for post in posts:
        post_detail = {}
        title_tag = post.find("h3", class_="post-title")
        if title_tag:
            link_tag = title_tag.find("a")
            if link_tag and link_tag.get("href"):
                post_detail["title"] = link_tag.text.strip()
                post_detail["link"] = link_tag["href"]
        post_body_div = post.find("div", class_="post-body")
        if post_body_div:
            iframe_tag = post_body_div.find("iframe")
            post_detail["iframe_src"] = iframe_tag.get("src", "") if iframe_tag else ""
            post_divs = post_body_div.find_all("div")
            post_detail["donwload_url"] = (
                post_divs[4].a.get("href", "")
                if len(post_divs) > 4 and post_divs[4].a
                else ""
            )
        if post_detail:
            details.append(post_detail)
    return details


def download_video(url, filename):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.blogger.com/"}
    with requests.get(url, headers=headers, stream=True, allow_redirects=True) as r:
        r.raise_for_status()

        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

    print("Download completed:", filename)


def ensure_dir(ftp, dirname):
    try:
        ftp.mkd(dirname)
    except:
        pass
    ftp.cwd(dirname)
    chmod(ftp, "755", dirname)


def chmod(ftp, mode, path):
    try:
        ftp.sendcmd(f"SITE CHMOD {mode} {path}")
    except:
        pass


def upload_folder(ftp, local_dir, remote_dir):
    ensure_dir(ftp, remote_dir)

    for item in os.listdir(local_dir):
        if "Satyajit ray" in item or "Justice league" in item:
            continue
        local_path = os.path.join(local_dir, item)

        if os.path.isfile(local_path):
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {item}", f)
            chmod(ftp, "644", item)
            print("Uploaded file:", item)

        elif os.path.isdir(local_path):
            upload_folder(ftp, local_path, item)
            ftp.cwd("..")


def clean(text):
    return re.sub(r'[\\/:*?"<>|]', "", text)


def run():
    print("Running cartoon download script...")
    # listing_url = "https://onlyjusticeleague.blogspot.com/search/label/Justice%20League%20Season%202"
    listing_url = "https://onlyjusticeleague.blogspot.com/search/label/Justice%20League%20Season%201?max-results=40&start=0"

    # listing_url = "https://onlyjusticeleague.blogspot.com/search/label/Justice%20League%20Unlimited%20Season%201?max-results=40&start=0"
    # listing_url = "https://onlyjusticeleague.blogspot.com/search/label/Young%20Justice%20Season%201?max-results=40&start=0"
    # listing_url = "https://onlyjusticeleague.blogspot.com/search/label/Young%20Justice%20Season%202"
    SHOW_YEAR = "2003"

    # Scrape the listing page for cartoon details
    cartoons = scrape_blogger_listing(listing_url)
    for cartoon in cartoons:
        title = cartoon["title"]
        video_url = cartoon["iframe_src"].replace("draft.blogger.com", "www.blogger.com")

        # Example title:
        # "Series Name A (2010) Season 02 Episode 26: Starcrossed: Part III"

        # ── Extract show name ─────────────────────────────
        show = re.split(r"\s+Season\s+\d+", title)[0].strip()

        # ── Extract season & episode ──────────────────────
        season_match = re.search(r"Season\s+(\d+)", title)
        season = season_match.group(1).zfill(2) if season_match else "00"

        episode_match = re.search(r"Episode\s+(\d+)", title)
        episode = episode_match.group(1).zfill(2) if episode_match else "00"

        # ── Extract episode title ─────────────────────────
        episode_title_match = re.search(r"Episode\s+\d+:\s*(.+)", title)
        episode_title = (
            episode_title_match.group(1) if episode_title_match else "Unknown"
        )

        # Further processing like downloading can be added here.

        # save the data inside data folder
        show_folder = clean(f"{show} ({SHOW_YEAR})")
        episode_title = clean(episode_title)

        # ── Build folder structure ────────────────────────────────
        base_dir = os.path.join(os.getcwd(), "data", show_folder, f"Season {season}")
        # folder_path = os.path.join(base_dir, f"Episode {episode} - {episode_title}")
        os.makedirs(base_dir, exist_ok=True)
        # ── Final filename ────────────────────────────────────────
        output_template = f"{show} S{season}E{episode} - {episode_title}.%(ext)s"

        # ── yt-dlp command ────────────────────────────────────────
        command = [
            "yt-dlp",
            "-f",
            "best",
            "--restrict-filenames",
            "-o",
            os.path.join(base_dir, output_template),
            video_url,
        ]
        subprocess.run(command)
        # break  # remove this break to download all episodes

    # push the data to FTP server
    # FTP_HOST = "192.168.31.75"
    # FTP_USER = "filezilla"
    # FTP_PASS = "filezilla2000"

    # LOCAL_FOLDER = os.path.join(os.getcwd(), "data", "Justice League Unlimited (2006)")
    # REMOTE_FOLDER = os.path.join("/mnt/media", "Animated Series", "Justice League Unlimited (2006)")

    # with FTP(FTP_HOST) as ftp:
    #     ftp.login(FTP_USER, FTP_PASS)
    #     upload_folder(ftp, LOCAL_FOLDER, REMOTE_FOLDER)


if __name__ == "__main__":
    run()
