import logging
import cloudscraper
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Create a CloudScraper instance
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_link(version: str) -> str:
    url = "https://youtube-music.en.uptodown.com/android/versions"

    # Fetch the content from the URL
    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Find all divs with data-url attribute
    divs = soup.find_all("div", {"data-url": True})

    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text.strip() == version:
            dl_page = div["data-url"]
            dl_url = dl_page.replace('/download/', '/post-download/')
            response = scraper.get(dl_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            post_download_divs = soup.find_all("div", class_="post-download")
            for post_div in post_download_divs:
                data_url = post_div.get("data-url")
                if data_url:
                    full_url = "https://dw.uptodown.com/dwn/" + data_url
                    return full_url

    return None

def get_latest_version():
    url = "https://youtube-music.en.uptodown.com/android/versions"
    
    # Fetch the content from the URL
    response = scraper.get(url)
    response.raise_for_status()
    
    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Select all the version spans within the versions list
    version_spans = soup.select('#versions-items-list .version')
    
    # Extract the version text and convert it to a tuple of integers for comparison
    versions = []
    for span in version_spans:
        version_text = span.text.strip()
        version_tuple = tuple(map(int, version_text.split('.')))
        versions.append((version_tuple, version_text))
    
    # Find the maximum version tuple
    highest_version_tuple, highest_version_str = max(versions)
    
    return highest_version_str

def download_resource(url: str, name: str) -> str:
    filepath = f"./{name}"

    with scraper.get(url, stream=True) as res:
        res.raise_for_status()

        total_size = int(res.headers.get('content-length', 0))
        downloaded_size = 0

        with open(filepath, "wb") as file:
            for chunk in res.iter_content(chunk_size=8192):
                file.write(chunk)
                downloaded_size += len(chunk)

        logging.info(
            f"URL: {url} [{downloaded_size}/{total_size}] -> {name}"
        )

    return filepath

# Main execution flow
version = get_latest_version()
if version:
    logging.info(f"Latest version found: {version}")
    download_link = get_download_link(version)
    if download_link:
        file_name = f"youtube-music-v{version}.apk"
        download_resource(download_link, file_name)
    else:
        logging.error("Failed to find the download link.")
else:
    logging.error("Failed to find the latest version.")
