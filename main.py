import logging 
from src.apkmirror import download_apkmirror
from src.apkpure import download_apkpure
from src.uptodown import download_uptodown

logging.basicConfig(
  level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

download_apkpure('x')
download_apkpure('youtube')
download_apkpure('youtube-music')
download_uptodown('youtube')
download_uptodown('youtube-music')
download_uptodown('tiktok')
download_apkmirror('youtube')
download_apkmirror('youtube-music')
download_apkmirror('x')
