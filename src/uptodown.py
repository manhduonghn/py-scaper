import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os

# Configuration
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

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
    chrome_options.add_argument(f"user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Click on 'See more' button if necessary
def click_see_more(driver):
    try:
        see_more_button = driver.find_element(By.ID, "button-list-more")
        if see_more_button:
            see_more_button.click()
            
    except NoSuchElementException:
        pass

# Get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    
    driver = create_chrome_driver()  # Tạo driver
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")  # Parse HTML từ Selenium
    driver.quit()

    version_spans = soup.select('#versions-items-list .version')
    
    versions = [span.text for span in version_spans]
    highest_version = max(versions)
    logging.info(f"Latest version: {highest_version}")
    return highest_version

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    driver = create_chrome_driver()  # Tạo driver
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    while True:
        divs = soup.find_all("div", {"data-url": True})
        for div in divs:
            version_span = div.find("span", class_="version")
            if version_span and version_span.text == version:
                dl_url = div["data-url"]
                driver.quit()
                return dl_url
        
        click_see_more(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()
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
    version = get_latest_version(app_name)
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}"
    return download_resource(download_link, filename)
