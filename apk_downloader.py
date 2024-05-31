import logging
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_page(version: str) -> str:
    url = "https://youtube.en.uptodown.com/android/versions"
    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    divs = soup.find_all("div", {"data-url": True})

    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text.strip() == version:
            data_url = div["data-url"].replace('/download/', '/post-download/')
            return data_url

    return None

version="19.20.32"
data-url = get_download_page(version)
print (data-url)
