import json
import time
import os
import re
from selenium import webdriver
from src.colorlog import logger
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
import random

# Configuration
base_url = "https://www.apkmirror.com"

# List of user agents for randomness
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    # Add more user agents as needed
]

def get_selenium_response(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    
    #time.sleep(10)  # Increased time to allow for page load and JS execution
    
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
    
    logger.info(f"URL: {url} -> \"-\" [1]")
    
    soup = BeautifulSoup(response, "html.parser")
    rows = soup.find_all('div', class_='table-row headerFont')
    
    for row in rows:
        row_text = row.get_text()
        if all(criterion in row_text for criterion in criteria):
            sub_url = row.find('a', class_='accent_color')
            if sub_url:
                return base_url + sub_url['href']
    
    return None

def extract_download_link(page: str) -> str:
    response = get_selenium_response(page)
    
    logger.info(f"URL: {page} -> \"-\" [1]")
    
    soup = BeautifulSoup(response, "html.parser")
    sub_url = soup.find('a', class_='downloadButton')
    
    if sub_url:
        download_page_url = base_url + sub_url['href']
        response = get_selenium_response(download_page_url)

        soup = BeautifulSoup(response, "html.parser")
        button = soup.find('a', id='download-link')
        if button:
            return base_url + button['href']

    return None  # Return None if no download link is found

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"{base_url}/uploads/?appcategory={config['name']}"
    response = get_selenium_response(url)

    logger.info(f"URL: {url} -> \"-\" [1]")

    soup = BeautifulSoup(response, "html.parser")
    app_rows = soup.find_all("div", class_="appRow")
    version_pattern = re.compile(r'\d+(\.\d+)*(-[a-zA-Z0-9]+(\.\d+)*)*')

    for row in app_rows:
        version_text = row.find("h5", class_="appRowTitle").a.text.strip()
        if "alpha" not in version_text.lower() and "beta" not in version_text.lower():
            match = version_pattern.search(version_text)
            if match:
                return match.group()

    return None

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"
    response = requests.get(url, stream=True)
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            downloaded_size += len(chunk)

    logger.info(f"Downloaded {name}: {url} [{downloaded_size}/{total_size}]")
    return filepath

def download_apkmirror(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_page = get_download_page(version, app_name)
    download_link = extract_download_link(download_page)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
