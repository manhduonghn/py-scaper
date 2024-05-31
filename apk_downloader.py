import logging 
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_link(version: str) -> str:
    url = f"https://youtube.en.uptodown.com/android/versions"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    divs = soup.find_all("div", {"data-url": True})

    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text.strip() == version:
            dl_page = div["data-url"]
            dl_url = dl_page.replace('/download/', '/post-download/')
            response = scraper.get(dl_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            post_download_divs = soup.find_all("div", class_="post-download")
            for div in post_download_divs:
                data_url = div["data-url"]
                full_url = "https://dw.uptodown.com/dwn/" + data_url
                return full_url

    return None

version = "19.20.32"
download_link = get_download_link(version)

if download_link:
    filename = f"youtube-music-v{version}.apk"
    response = scraper.get(download_link)
    with open(filename, 'wb') as f:
        f.write(response.content)
else:
    print("Không thể tải xuống file cho phiên bản", version)
