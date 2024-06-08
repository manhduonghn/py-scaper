import os
import sys
import json
import logging
from src import downloader

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    apps = ["reddit", "x", "tiktok", "youtube", "youtube-music"]

    for app in apps:
        downloader.download_apkmirror(app)
        downloader.download_uptodown(app)
        downloader.download_apkpure(app)
