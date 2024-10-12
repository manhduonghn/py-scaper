import json
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os

# Configuration for logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# Create Chrome driver with headless options
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument(f"user-agent=Mozilla/5.0")

    logging.info("Creating Chrome driver with headless options.")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Click on 'See more' button if necessary
def click_see_more(driver):
    try:
        logging.info("Attempting to click 'See more' button...")
        see_more_button = driver.find_element(By.ID, "button-list-more")
        if see_more_button:
            see_more_button.click()
            logging.info("'See more' button clicked.")
        else:
            logging.info("'See more' button not found.")
    except NoSuchElementException:
        logging.warning("'See more' button not found or no longer exists.")

# Get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    logging.info(f"Fetching latest version for {app_name} from {url}.")
    
    driver = create_chrome_driver()
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    
    version_spans = soup.select('#versions-items-list .version')
    versions = [span.text for span in version_spans]
    highest_version = max(versions)
    
    logging.info(f"Latest version for {app_name} is {highest_version}.")
    return highest_version

# Check if the version is on the page
def check_version_on_page(soup, version):
    logging.info(f"Checking if version {version} is on the page.")
    divs = soup.find_all("div", {"data-url": True})
    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text == version:
            dl_url = div["data-url"]
            logging.info(f"Found download URL for version {version}: {dl_url}")
            return dl_url
    logging.info(f"Version {version} not found on this page.")
    return None

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    logging.info(f"Fetching download link for version {version} of {app_name}.")
    
    driver = create_chrome_driver()
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    dl_url = check_version_on_page(soup, version)
    
    while not dl_url:
        logging.info(f"Version {version} not found, loading more versions...")
        click_see_more(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        dl_url = check_version_on_page(soup, version)
    
    driver.quit()
    return dl_url

# Download resource from URL
def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}.apk"
    logging.info(f"Starting download for {name} from {url}.")
    
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        logging.info(f"Downloaded {name} to {filepath}.")
    else:
        logging.error(f"Failed to download {name}. Status code: {response.status_code}")
    
    return filepath

# Main function to download app from Uptodown
def download_uptodown(app_name: str) -> str:
    version = "18.41.39"  # Hardcoded version, can be replaced with dynamic fetch
    # version = get_latest_version(app_name)
    
    logging.info(f"Initiating download for {app_name} version {version}.")
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}"
    return download_resource(download_link, filename)
