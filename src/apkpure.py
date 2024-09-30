import json
import logging
import cronet
from bs4 import BeautifulSoup

# Configuration
client = cronet.CronetClient()
client.user_agent = 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0'

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://apkpure.net/{config['name']}/{config['package']}/versions"

    # Gửi yêu cầu với cronet
    response = client.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve URL: {url}")
        return None

    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    
    # Phân tích HTML để tìm phiên bản mới nhất
    soup = BeautifulSoup(response.content, "html.parser")
    version_info = soup.find('div', class_='ver-top-down')

    if version_info:
        version = version_info['data-dt-version']
        if version:
            return version
            
    return None

def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://apkpure.net/{config['name']}/{config['package']}/download/{version}"

    response = client.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve URL: {url}")
        return None

    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    soup = BeautifulSoup(response.content, "html.parser")
    download_link = soup.find('a', id='download_link')
    if download_link:
        return download_link['href']
    
    return None

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with client.get(url, stream=True) as res:
        if res.status_code != 200:
            logging.error(f"Failed to download resource from URL: {url}")
            return None

        final_url = res.url
        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)

        logging.info(
            f"URL:{final_url} [{downloaded_size}/{total_size}] -> \"{name}\" [1]"
        )

    return filepath

def download_apkpure(app_name: str) -> str:
    version = get_latest_version(app_name)
    if not version:
        logging.error(f"Failed to find latest version for app: {app_name}")
        return None

    download_link = get_download_link(version, app_name)
    if not download_link:
        logging.error(f"Failed to get download link for version {version} of app: {app_name}")
        return None

    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
