import json
import logging
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

# Check if the version is on the page
def check_version_on_page(soup, version):
    divs = soup.find_all("div", {"data-url": True})
    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text == version:
            dl_url = div["data-url"]
            logging.info(f"Download URL for version {version}: {dl_url}")
            return dl_url
    return None

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    driver = create_chrome_driver()  # Tạo driver
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    dl_url = check_version_on_page(soup, version)
    if dl_url:
        driver.quit()
        return dl_url
    
    while True:
        click_see_more(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        dl_url = check_version_on_page(soup, version)
        if dl_url:
            driver.quit()
            return dl_url

    driver.quit()
    return None

# Download resource from URL
def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}.apk"
    logging.info(f"Starting download for {name} from {url}.")
    
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        # Log the final URL (after redirects)
        final_url = response.url
        logging.info(f"Final download URL: {final_url}")
        
        # Save the file
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Downloaded {name} to {filepath}.")
    else:
        logging.error(f"Failed to download {name}. Status code: {response.status_code}")
    
    return filepath

# Main function to download app from Uptodown
def download_uptodown(app_name: str) -> str:
    version = "18.41.39"
    # version = get_latest_version(app_name)
    
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}"
    return download_resource(download_link, filename)
