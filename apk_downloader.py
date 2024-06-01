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
    url = f"https://apkpure.net/youtube/com.google.android.youtube/download/{version}"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    download_btn = soup.find('a', class_='download-btn')
    download_link = download_btn['href'] if download_btn else None
    
    if download_link:
        return download_link
    
    return None


def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with scraper.get(url, stream=True) as res:
        res.raise_for_status()

        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)

        logging.info(
            f"URL: {url} [{downloaded_size}/{total_size}] -> {name}"
        )

    return filepath

version = "19.21.37"
download_link = get_download_link(version)

if download_link:
    file_name = f"youtube-v{version}.apk"
    download_resource(download_link, file_name)
else:
    logging.error("Failed to obtain download link.")
