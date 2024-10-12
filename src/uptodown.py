import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configuration
logging.basicConfig(
  level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# Function to get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    # Initialize Selenium WebDriver (you can replace with any browser driver you want)
    driver = webdriver.Chrome()
    driver.get(url)

    # Click "See More" button 4 times to load more versions
    for _ in range(4):
        try:
            # Wait for the "See More" button to be clickable, then click it
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'See more')]"))
            )
            see_more_button.click()
            time.sleep(2)  # Wait for content to load after each click
        except Exception as e:
            logging.info("No more 'See More' button or error occurred: " + str(e))
            break

    # Get the page source after clicking "See More"
    html = driver.page_source
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    version_spans = soup.select('#versions-items-list .version')
    versions = [span.text.strip() for span in version_spans]
    highest_version = max(versions, key=lambda v: [int(x) for x in v.split('.')])

    logging.info(f"Highest version found: {highest_version}")
    return highest_version

# Function to get the download link for the specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    # Initialize Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(url)

    # Click "See More" button 4 times to load more versions
    for _ in range(4):
        try:
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'See more')]"))
            )
            see_more_button.click()
            time.sleep(2)
        except Exception as e:
            logging.info("No more 'See More' button or error occurred: " + str(e))
            break

    # Get the page source after clicking "See More"
    html = driver.page_source
    driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all("div", {"data-url": True})

    # Find the download link for the specified version
    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text.strip() == version:
            dl_url = div["data-url"]
            response = scraper.get(dl_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            button = soup.find('button', id='detail-download-button')
            data_url = button['data-url']
            if data_url:
                full_url = "https://dw.uptodown.com/dwn/" + data_url
                return full_url

    return None

# Function to download the APK file from the download link
def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with scraper.get(url, stream=True) as res:
        res.raise_for_status()

        final_url = res.url  # Get the final URL after any redirects
        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)
                
        logging.info(
            f"URL:{final_url} [{downloaded_size}/{total_size}] -> \"{name}\" [1]"
        )

    return filepath

# Main function to download the latest version of the app
def download_uptodown(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_link = get_download_link(version, app_name)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
