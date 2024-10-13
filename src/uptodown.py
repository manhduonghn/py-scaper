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

# List of user agents for randomness
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0",
    # Add more user agents as needed
]

# Create Chrome driver with headless options
def create_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Bypass sandbox mode
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--remote-debugging-port=9222")  # Configure remote debugging
    chrome_options.add_argument("start-maximized")  # Maximize window
    chrome_options.add_argument("disable-infobars")  # Disable infobars
    chrome_options.add_argument("--disable-extensions")  # Disable extensions
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Click on 'See more' button if necessary
def click_see_more(driver):
    try:
        see_more_button = driver.find_element(By.ID, "button-list-more")
        if see_more_button:
            logging.info("Clicking 'See more' to load more versions.")
            see_more_button.click()
            time.sleep(2)  # Give it some time to load more versions
    except NoSuchElementException:
        logging.info("No 'See more' button found, all versions are already loaded.")
        pass

# Get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"
    
    driver = create_chrome_driver()  # Create driver
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")  # Parse HTML from Selenium
    driver.quit()

    version_spans = soup.select('#versions-items-list .version')
    
    versions = [span.text.strip() for span in version_spans]
    highest_version = max(versions)
    
    logging.info(f"Highest version found for {app_name}: {highest_version}")
    return highest_version

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    driver = create_chrome_driver()  # Create driver
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    while True:
        divs = soup.find_all("div", {"data-url": True})
        for div in divs:
            version_span = div.find("span", class_="version")
            if version_span and version_span.text.strip() == version:
                dl_url = div["data-url"]
                
                # Navigate to the version-specific download page
                logging.info(f"Found download page for version {version}, navigating to it...")
                driver.get(dl_url)

                # Parse the download page for the actual download link
                soup = BeautifulSoup(driver.page_source, "html.parser")
                download_button = soup.find('button', {'id': 'detail-download-button'})
                if download_button and download_button.get('data-url'):
                    data_url = download_button.get('data-url')
                    full_url = f"https://dw.uptodown.com/dwn/{data_url}"
                    logging.info(f"Found download link: {full_url}")
                    driver.quit()
                    return full_url

        # If the "See more" button is available, click to load more versions
        click_see_more(driver)
        soup = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()
    return None

# Download APK resource from URL
def download_resource(url: str, name: str) -> str:
    if not url:
        logging.error(f"Download URL is None. Cannot download {name}.")
        return None

    filepath = f"./{name}.apk"

    # Using Selenium to initiate download or requests could be better, but we're using Selenium here for consistency
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
