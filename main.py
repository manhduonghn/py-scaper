import json
import logging
import cloudscraper 
from bs4 import BeautifulSoup

# Configuration
scraper = cloudscraper.create_scraper()
scraper.headers.update(
    {'User-Agent': 'Mozilla/5.0'}
)
logging.basicConfig(
  level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def get_download_link(version: str) -> str:
    url = f"https://apkcombo.com/vi/youtube/com.google.android.youtube/download/phone-{version}-apk"
    response = scraper.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    soup = BeautifulSoup(response.content, "html.parser")
    download_link = soup.find(
        'a', href=lambda href: href and f"com.apk?" in href
    )
    if download_link:
        return download_link['href']
    
    return None

version = '19.23.33'
url = get_download_link(version)

logging.info(url)
