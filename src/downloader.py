import json
import logging

from src import (
    apkpure, 
    version, 
    scraper, 
    uptodown, 
    apkmirror 
)

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

def download_apkmirror(app_name: str) -> str:
    global version

    try:
        conf_file_path = f'./apps/apkmirror/{app_name}.json'
        version = config['version']
        type = config['type']

        if type == 'BUNDLE':
            ext = 'apkm'
        elif type == 'APK':
            ext = 'apk'
        else:
            ext = 'apk'

        if not version:
            version = apkmirror.get_latest_version(app_name)

        download_page = apkmirror.get_download_page(version, app_name)
        download_link = apkmirror.extract_download_link(download_page)

        filename = f"{app_name}-v{version}.apk"
        
        return download_resource(download_link, filename)
    except Exception as e:
        return None


def download_apkpure(app_name: str) -> str:
    global version

    try:
        conf_file_path = f'./apps/apkpure/{app_name}.json'
        version = config['version']

        if not version:
            version = apkpure.get_latest_version(app_name)

        download_link = apkpure.get_download_link(version, app_name)
        filename = f"{app_name}-v{version}.apk"
        
        return download_resource(download_link, filename)
    except Exception as e:
        return None


def download_uptodown(app_name: str) -> str:
    global version

    try:
        conf_file_path = f'./apps/uptodown/{app_name}.json'
        version = config['version']

        if not version:
            version = uptodown.get_latest_version(app_name)

        download_link = uptodown.get_download_link(version, app_name)
        filename = f"{app_name}-v{version}.apk"
        
        return download_resource(download_link, filename)
    except Exception as e:
        return None
