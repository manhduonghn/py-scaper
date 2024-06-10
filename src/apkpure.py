import json
import logging
from requests_html import HTMLSession

# Configuration
session = HTMLSession()
session.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0'}
)

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://apkpure.net/{config['name']}/{config['package']}/versions"

    response = session.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    version_info = response.html.find('div.ver-top-down', first=True)

    if version_info:
        version = version_info.attrs.get('data-dt-version')
        if version:
            return version

    return None

def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/apkpure/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://apkpure.net/{config['name']}/{config['package']}/download/{version}"

    response = session.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    download_link = response.html.find(
        f'a[href*="/APK/{config["package"]}"]', first=True
    )
    if download_link:
        return download_link.attrs['href']

    return None

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with session.get(url, stream=True) as res:
        res.raise_for_status()

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
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
