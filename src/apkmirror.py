import os
import re
import json
import cloudscraper
import time
from src.colorlog import logger
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage
import logging

base_url = "https://www.apkmirror.com"

# Tạo scraper với User-Agent của Chrome trên Android
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'android',
        'desktop': False
    }
)

# Bypass Cloudflare bằng cách dùng trình duyệt điều khiển Chromium
class CloudflareBypasser:
    def __init__(self, driver: ChromiumPage, max_retries=-1, log=True):
        self.driver = driver
        self.max_retries = max_retries
        self.log = log

    def is_bypassed(self):
        try:
            title = self.driver.title.lower()
            return "just a moment" not in title
        except Exception as e:
            logger.error(f"Error checking page title: {e}")
            return False

    def bypass(self):
        try_count = 0

        while not self.is_bypassed():
            if 0 < self.max_retries + 1 <= try_count:
                logger.error("Exceeded maximum retries. Bypass failed.")
                break

            logger.info(f"Attempt {try_count + 1}: Verification page detected. Trying to bypass...")
            time.sleep(2)
            try_count += 1

        if self.is_bypassed():
            logger.info("Bypass successful.")
        else:
            logger.error("Bypass failed.")

# Hàm dùng cloudscraper hoặc Chromium để lấy phản hồi
def get_response(url, method='get', **kwargs):
    """Get a single response using cloudscraper or Chromium bypass."""
    try:
        response = scraper.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except cloudscraper.exceptions.CloudflareChallengeError:
        logger.warning(f"Cloudflare challenge detected. Trying Chromium bypass for URL: {url}")
        return bypass_cloudflare_with_chromium(url)
    except cloudscraper.exceptions.CloudflareCaptchaError:
        logger.error(f"CAPTCHA encountered at {url}. Unable to proceed.")
    except Exception as e:
        logger.error(f"Error: {e} occurred while trying to retrieve URL: {url}")
    
    return None

def bypass_cloudflare_with_chromium(url, max_retries=3):
    driver = ChromiumPage(headless=True)  # Khởi tạo ChromiumPage
    driver.get(url)

    bypasser = CloudflareBypasser(driver, max_retries=max_retries)
    bypasser.bypass()

    if bypasser.is_bypassed():
        html = driver.page_source
        driver.close()
        return html
    else:
        driver.close()
        return None

# Hàm lấy trang tải về
def get_download_page(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    criteria = [config['type'], config['arch'], config['dpi']]
    url = (f"{base_url}/apk/{config['org']}/{config['name']}/"
           f"{config['name']}-{version.replace('.', '-')}-release/")
    
    response = get_response(url)
    if not response:
        return None

    content_size = len(response.content)
    logger.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all('div', class_='table-row headerFont')
    for row in rows:
        row_text = row.get_text()
        if all(criterion in row_text for criterion in criteria):
            sub_url = row.find('a', class_='accent_color')
            if sub_url:
                return base_url + sub_url['href']
    return None

def extract_download_link(page: str) -> str:
    response = get_response(page)
    if not response:
        return None

    content_size = len(response.content)
    logger.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    soup = BeautifulSoup(response.content, "html.parser")
    sub_url = soup.find('a', class_='downloadButton')
    if sub_url:
        download_page_url = base_url + sub_url['href']
        response = get_response(download_page_url)
        if not response:
            return None

        content_size = len(response.content)
        logger.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

        soup = BeautifulSoup(response.content, "html.parser")
        button = soup.find('a', id='download-link')
        if button:
            return base_url + button['href']
    return None

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"{base_url}/uploads/?appcategory={config['name']}"
    response = get_response(url)
    if not response:
        return None

    content_size = len(response.content)
    logger.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")

    soup = BeautifulSoup(response.content, "html.parser")
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
    response = get_response(url, stream=True)
    if not response:
        return None

    final_url = response.url
    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            downloaded_size += len(chunk)

    logger.info(f"URL:{final_url} [{downloaded_size}/{total_size}] -> \"{name}\" [1]")
    return filepath

def download_apkmirror(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_page = get_download_page(version, app_name)
    download_link = extract_download_link(download_page)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
