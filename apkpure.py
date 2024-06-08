import logging
import cloudscraper
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_latest_version(app_name: str, package: str) -> str:
    url = f"https://apkpure.net/{app_name}/{package}/versions"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    version_info = soup.find('div', class_='ver-top-down')

    if version_info:
        version = version_info['data-dt-version']
        if version:
            return version
    return None

def get_download_link(app_name: str, package: str, version: str) -> str:
    url = f"https://apkpure.net/{app_name}/{package}/download/{version}"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    download_link = soup.find(
        'a', href=lambda href: href and '/APK/com.google.android.apps.youtube.music' in href
    )
    if download_link:
        return download_link['href']
    
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

app_name = 'youtube-music'
package = 'com.google.android.apps.youtube.music'
version = get_latest_version(app_name, package)
download_link = get_download_link(app_name, package, version)
file_name = f"{app_name}-v{version}.apk"
download_resource(download_link, file_name)
    
