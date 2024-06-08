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
      
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'   
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://apkpure.net/{config['name']}/{config['package']}/versions"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    version_info = soup.find('div', class_='ver-top-down')

    if version_info:
        version = version_info['data-dt-version']
        if version:
            return version
            
    return None

def get_download_link(version: str, app_name: str) ->str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'   
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://apkpure.net/{config['name']}/{config['package']}/download/{version}"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    download_link = soup.find(
        'a', href=lambda href: href and f"/APK/{config['package']}" in href
    )
    if download_link:
        return download_link['href']
    
    return None

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with scraper.get(url, stream=True) as res:
        res.raise_for_status()

        final_url = res.url  # Get the final URL after any redirects
        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)
                
        logger.success(
            f"URL: {final_url} [{downloaded_size}/{total_size}] -> {name}"
        )

    return filepath
    
def download_apkpure(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}.apk"
    download_resource(download_link, filename)
    
