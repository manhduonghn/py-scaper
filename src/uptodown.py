import os
import re
import json
import logging
import requests
import subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC


# Configuration
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

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
    chrome_options.add_argument(
        f"user-agent=Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0"
    )

    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Click on 'See more' button if necessary
def click_see_more(driver):
    try:
        see_more_button = driver.find_element(By.ID, "button-list-more")
        if see_more_button:
            logging.info("Clicking 'See more' to load more versions.")
            see_more_button.click()
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

def download_uptodown(app_name: str) -> str:
    version = "19.33.35"  # Hardcoded version, you can use get_latest_version(app_name) instead
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}"
    
    if download_link:
        # Use requests to get the final URL after redirections
        response = requests.get(download_link, allow_redirects=True)
        final_url = response.url
        logging.info(f"Final URL after redirections: {final_url}")

        # Extract file extension from the final URL
        file_extension = os.path.splitext(final_url)[1]  # This will return .apk, .xapk, etc.

        # Dynamically adjust the filename with the correct extension
        filepath = f"./{filename}{file_extension}"

        # Now download the file using requests
        logging.info(f"Downloading the file from {final_url} to {filepath}")

        # Stream the download to avoid memory overload with large files
        with requests.get(final_url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        logging.info(f"Downloaded {filename} to {filepath}")
        return filepath
    else:
        logging.error("Failed to retrieve the download link.")
        return None

def download_assets_from_repo(release_url):
    driver = create_chrome_driver()
    driver.get(release_url)
    
    downloaded_files = []
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "repo-content-pjax-container"))
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        asset_links = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/releases/download/')]"))
        )

        for link in asset_links:
            asset_url = link.get_attribute('href')
            response = requests.head(asset_url, allow_redirects=True)
            if response.status_code == 200:
                download_response = requests.get(asset_url, allow_redirects=True, stream=True)
                final_url = download_response.url  # Get the final URL after any redirections
                filename = asset_url.split('/')[-1]
                total_size = int(download_response.headers.get('Content-Length', 0))
                downloaded_size = 0

                with open(filename, 'wb') as file:
                    for chunk in download_response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)

                # Logging the download progress with final_url
                logging.info(
                    f"URL:{final_url} [{downloaded_size}/{total_size}] -> \"{filename}\" [1]"
                )
                downloaded_files.append(filename)  # Store downloaded filename
    except Exception as e:
        logging.error(f"Error while downloading from {release_url}: {e}")
    finally:
        driver.quit()
    
    return downloaded_files  # Return the list of downloaded files
