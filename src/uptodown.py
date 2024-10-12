import json
import logging
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import os

# Configuration
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    # Add more user agents as needed
]

# Create Chrome driver with headless options
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Chạy ở chế độ headless
    chrome_options.add_argument("--no-sandbox")  # Bỏ qua sandbox mode
    chrome_options.add_argument("--disable-dev-shm-usage")  # Khắc phục lỗi thiếu bộ nhớ
    chrome_options.add_argument("--remote-debugging-port=9222")  # Cấu hình remote debugging
    chrome_options.add_argument("start-maximized")  # Khởi chạy tối đa kích thước
    chrome_options.add_argument("disable-infobars")  # Tắt thanh thông tin
    chrome_options.add_argument("--disable-extensions")  # Vô hiệu hóa các extension
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

# Click on 'See more' button up to 4 times if it exists
def click_see_more(driver):
    max_clicks = 4  # Số lần click tối đa
    clicks = 0

    while clicks < max_clicks:
        try:
            see_more_button = driver.find_element(By.ID, "button-list-more")
            if see_more_button:
                see_more_button.click()
                logging.info(f"Clicked 'See more' button {clicks + 1} times.")
                time.sleep(2)  # Đợi trang tải thêm nội dung
                clicks += 1
            else:
                logging.info("'See more' button not found or no more content to load.")
                break
        except NoSuchElementException:
            logging.info("'See more' button not found or no more content to load.")
            break


# Get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'
    
    # Kiểm tra file cấu hình tồn tại không
    if not os.path.exists(conf_file_path):
        logging.error(f"Configuration file not found for {app_name}")
        return None

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    
    driver = create_chrome_driver()  # Tạo driver
    driver.get(url)
    
    click_see_more(driver)  # Click vào "See more" nếu có
    
    soup = BeautifulSoup(driver.page_source, "html.parser")  # Parse HTML từ Selenium
    driver.quit()

    # Lấy danh sách phiên bản từ trang
    version_spans = soup.select('#versions-items-list .version')
    
    if not version_spans:
        logging.error(f"No versions found for {app_name} on Uptodown.")
        return None
    
    versions = [span.text for span in version_spans]
    highest_version = max(versions)
    logging.info(f"Latest version: {highest_version}")
    return highest_version

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'
    
    # Kiểm tra file cấu hình tồn tại không
    if not os.path.exists(conf_file_path):
        logging.error(f"Configuration file not found for {app_name}")
        return None

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    driver = create_chrome_driver()  # Tạo driver
    driver.get(url)
    
    click_see_more(driver)  # Click vào "See more" nếu có
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    divs = soup.find_all("div", {"data-url": True})

    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text == version:
            dl_url = div["data-url"]
            logging.info(f"Download URL: {dl_url}")
            return dl_url

    logging.error(f"Download link for version {version} not found for {app_name}.")
    return None

# Download resource from URL
def download_resource(url: str, name: str) -> str:
    if not url:
        logging.error(f"Download URL is None. Cannot download {name}.")
        return None

    filepath = f"./{name}.apk"

    driver = create_chrome_driver()
    driver.get(url)

    with open(filepath, "wb") as file:
        file.write(driver.page_source.encode('utf-8'))

    driver.quit()

    logging.info(f"Downloaded {name} to {filepath}")
    return filepath

# Main function to download app from Uptodown
def download_uptodown(app_name: str) -> str:
    version = "19.04.36"
    # version = get_latest_version(app_name)
    
    if not version:
        logging.error(f"Failed to get the latest version for {app_name}.")
        return None
    
    download_link = get_download_link(version, app_name)
    
    if not download_link:
        logging.error(f"Failed to get the download link for {app_name} version {version}.")
        return None
    
    filename = f"{app_name}-v{version}"
    return download_resource(download_link, filename)
