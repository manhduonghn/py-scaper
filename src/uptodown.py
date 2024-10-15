import json
import logging
from requests_html import HTMLSession

# Configuration
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

# Create an HTML session and load JavaScript
def create_html_session():
    session = HTMLSession()
    return session

# Get the latest version of the app
def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    session = create_html_session()  # Create session
    response = session.get(url)
    response.html.render()  # Render JavaScript (if any) to load all dynamic content
    
    version_spans = response.html.find('#versions-items-list .version')
    versions = [span.text.strip() for span in version_spans]
    
    if versions:
        highest_version = max(versions)
        logging.info(f"Highest version found for {app_name}: {highest_version}")
        return highest_version
    return None

# Get download link for a specific version
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    session = create_html_session()  # Create session
    response = session.get(url)
    response.html.render()  # Render JavaScript
    
    # Find all the divs with download links
    while True:
        divs = response.html.find("div[data-url]")
        for div in divs:
            version_span = div.find("span.version", first=True)
            if version_span and version_span.text.strip() == version:
                dl_url = div.attrs['data-url']

                # Navigate to the version-specific download page
                logging.info(f"Found download page for version {version}, navigating to it...")
                version_page = session.get(dl_url)
                version_page.html.render()

                # Parse the download page for the actual download link
                download_button = version_page.html.find('button#detail-download-button', first=True)
                if download_button and 'data-url' in download_button.attrs:
                    data_url = download_button.attrs['data-url']
                    full_url = f"https://dw.uptodown.com/dwn/{data_url}"
                    logging.info(f"Found download link: {full_url}")
                    return full_url

        # Click the "See more" button if available to load more versions
        see_more_button = response.html.find('#button-list-more', first=True)
        if see_more_button:
            logging.info("Clicking 'See more' to load more versions.")
            see_more_button.click()
            response.html.render()  # Re-render page after loading more content
        else:
            logging.info("No 'See more' button found, all versions are already loaded.")
            break

    return None

# Download APK resource from URL using requests
def download_resource(url: str, name: str) -> str:
    if not url:
        logging.error(f"Download URL is None. Cannot download {name}.")
        return None

    filepath = f"./{name}.apk"

    try:
        logging.info(f"Downloading {name} from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check if the request was successful

        with open(filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        logging.info(f"Downloaded {name} to {filepath}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {name}: {e}")
        return None

    return filepath

# Main function to download app from Uptodown
def download_uptodown(app_name: str) -> str:
    version = "17.30.33"
    # version = get_latest_version(app_name)  # Lấy phiên bản mới nhất
    download_link = get_download_link(version, app_name)
    if download_link:
        filename = f"{app_name}-v{version}"
        return download_resource(download_link, filename)
    else:
        logging.error(f"Could not find download link for {app_name} version {version}")
        return None
