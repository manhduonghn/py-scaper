import os
import logging
from src import downloader

def run_build(app_name: str) -> str:
    if source == "apkmirror":
        return downloader.download_apkmirror(app_name)
    elif source == "apkpure":
        return downloader.download_apkpure(app_name)
    elif source == "uptodown":
        return downloader.download_uptodown(app_name)
    else:
        logging.error("Unknown source")
        return None

if __name__ == "__main__":
    apk_filepath = run_build("youtube")
