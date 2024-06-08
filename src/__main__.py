import os
import sys
import json
import logging
from src import downloader

apk = downloader.download_apkmirror("reddit")
downloader.download_apkmirror("x")
downloader.download_apkmirror("tiktok")
downloader.download_apkmirror("youtube")
downloader.download_apkmirror("youtube-music")
downloader.download_uptodown("tiktok")
downloader.download_uptodown("youtube")
downloader.download_uptodown("youtube-music")
downloader.download_apkpure("reddit")
downloader.download_apkpure("x")
downloader.download_apkpure("tiktok")
downloader.download_apkpure("youtube")
downloader.download_apkpure("youtube-music")

  
