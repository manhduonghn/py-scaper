import json
import time
import os
import re
import requests
import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup

# Configuration
base_url = "https://www.apkmirror.com"

def get_selenium_response(url):
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # Chạy ở chế độ không có giao diện
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")

    driver = uc.Chrome(options=options)
    driver.get(url)
    
    # Cho thời gian để các JavaScript có thể thực thi
    time.sleep(10)  
    
    response = driver.page_source
    driver.quit()
    return response

def get_download_page(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    criteria = [config['type'], config['arch'], config['dpi']]
    url = (f"{base_url}/apk/{config['org']}/{config['name']}/"
           f"{config['name']}-{version.replace('.', '-')}-release/")
    
    response = get_selenium_response(url)
    soup = BeautifulSoup(response, "html.parser")
    rows = soup.find_all('div', class_='table-row headerFont')
    
    for row in rows:
        row_text = row.get_text()
        if all(criterion in row_text for criterion in criteria):
            sub_url = row.find('a', class_='accent_color')
            if sub_url:
                return base_url + sub_url['href']
    
    print(f"Failed to find the download page for version {version} of {app_name}.")
    return None

def extract_download_link(page: str) -> str:
    response = get_selenium_response(page)
    soup = BeautifulSoup(response, "html.parser")
    sub_url = soup.find('a', class_='downloadButton')
    
    if sub_url:
        download_page_url = base_url + sub_url['href']
        response = get_selenium_response(download_page_url)

        soup = BeautifulSoup(response, "html.parser")
        button = soup.find('a', id='download-link')
        if button:
            return base_url + button['href']

    print(f"Failed to extract download link from page: {page}")
    return None

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"{base_url}/uploads/?appcategory={config['name']}"
    response = get_selenium_response(url)

    soup = BeautifulSoup(response, "html.parser")
    app_rows = soup.find_all("div", class_="appRow")
    version_pattern = re.compile(r'\d+(\.\d+)*(-[a-zA-Z0-9]+(\.\d+)*)*')

    for row in app_rows:
        version_text = row.find("h5", class_="appRowTitle").a.text.strip()
        if "alpha" not in version_text.lower() and "beta" not in version_text.lower():
            match = version_pattern.search(version_text)
            if match:
                return match.group()

    print(f"Failed to find the latest version for {app_name}.")
    return None

def download_resource(url: str, name: str) -> str:
    if url is None:
        print("No URL provided for downloading resource.")
        return None
    
    filepath = f"./{name}"
    response = requests.get(url, stream=True)
    
    if response.status_code != 200:
        print(f"Failed to download resource: {url}")
        return None

    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            downloaded_size += len(chunk)

    print(f"Downloaded {name}: {url} [{downloaded_size}/{total_size}]")
    return filepath

def download_apkmirror(app_name: str) -> str:
    version = get_latest_version(app_name)
    if version is None:
        print(f"Could not get the latest version for {app_name}.")
        return None

    download_page = get_download_page(version, app_name)
    if download_page is None:
        print(f"Failed to get download page for version {version} of {app_name}.")
        return None

    download_link = extract_download_link(download_page)
    if download_link is None:
        print(f"Failed to extract download link for {app_name}.")
        return None

    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
