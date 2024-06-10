import json
import logging
from requests_html import HTMLSession

# Configuration
session = HTMLSession()
logging.basicConfig(
  level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def get_download_link(version: str) -> str:
    url = f"https://apkcombo.com/youtube/com.google.android.youtube/download/phone-{version}-apk"
    response = session.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    download_link = response.html.find('a', containing="com.apk?", first=True)
    if download_link:
        return download_link.attrs['href']
    return None

version = '19.23.33'
url = get_download_link(version)

logging.info(url)
