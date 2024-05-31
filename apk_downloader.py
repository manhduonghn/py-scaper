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
    url = "https://youtube-music.en.uptodown.com/android/versions"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    divs = soup.find_all("div", {"data-url": True})

    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text == version:
            dl_page = div["data-url"]
            dl_url = dl_page.replace('/download/', '/post-download/')
            response = scraper.get(dl_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            post_download_divs = soup.find_all("div", class_="post-download")
            for post_div in post_download_divs:
                data_url = post_div.get("data-url")
                if data_url:
                    full_url = "https://dw.uptodown.com/dwn/" + data_url
                    return full_url

    return None

def get_latest_version():
    url = "https://youtube-music.en.uptodown.com/android/versions"
    
    response = scraper.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    version_spans = soup.select('#versions-items-list .version')
    versions = [span.text for span in version_spans]
    highest_version = max(versions)
    
    return highest_version

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


version = get_latest_version()
download_link = get_download_link(version)
file_name = f"youtube-music-v{version}.apk"
download_resource(download_link, file_name)
