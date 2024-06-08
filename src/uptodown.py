import json
import logging
import cloudscraper 

from bs4 import BeautifulSoup
from loguru import logger 

scraper = cloudscraper.create_scraper()
scraper.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0'}
)
logging.basicConfig(
  level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def get_download_link(version: str, app_name: str) ->str:
    
    conf_file_path = f'./apps/uptodown/{app_name}.json'   
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
  
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

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

def get_latest_version(app_name: str) -> str:
    
    conf_file_path = f'./apps/uptodown/{app_name}.json'   
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    
    response = scraper.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    version_spans = soup.select('#versions-items-list .version')
    versions = [span.text for span in version_spans]
    highest_version = max(versions)
    
    return highest_version

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with requests.get(url, stream=True) as res:
        res.raise_for_status()

        final_url = res.url  # Get the final URL after any redirects
        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)
                # Optionally, print progress
                logger.info(f"Downloaded {downloaded_size} of {total_size} bytes", end='\r')

        logger.success(f"URL: {final_url} [{downloaded_size}/{total_size}] -> {name}")

    return filepath

def download_uptodown(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}.apk"
    download_resource(download_link, filename)
