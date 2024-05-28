import cloudscraper
from bs4 import BeautifulSoup

keywords = ["APK", "universal", "nodpi"]
base_url = "https://www.apkmirror.com"

# Create a scraper with a custom user agent
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_page(version: str) -> str:
    """
    Get the download page URL for a specific YouTube version.
    """
    yt_url = f"{base_url}/apk/google-inc/youtube/youtube-{version.replace('.', '-')}-release/"
    response = scraper.get(yt_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Iterate through all links with class 'accent_color'
    for link in soup.find_all('a', class_='accent_color'):
        parent_div = link.find_parent('div', class_='table-cell')
        if not parent_div:
            continue

        texts = [parent_div.get_text(strip=True)] + \
                [sibling.get_text(strip=True) for sibling in parent_div.find_next_siblings('div')]

        # Check if all keywords are present in the texts
        if all(any(keyword.lower() in text.lower() for text in texts) for keyword in keywords):
            return f"{base_url}{link['href']}"

    return None

def extract_download_link(page_url: str) -> str:
    """
    Extract the actual download link from the download page.
    """
    response = scraper.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    download_button = soup.find('a', class_='downloadButton')
    if not download_button:
        raise Exception("Download button not found on the page")

    download_page_url = f"{base_url}{download_button['href']}"
    response = scraper.get(download_page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    direct_link = soup.select_one('a[rel="nofollow"]')
    if not direct_link:
        raise Exception("No final download link found")

    return f"{base_url}{direct_link['href']}"

# Example usage
version = "17.03.35"
download_page = get_download_page(version)
if download_page:
    try:
        download_link = extract_download_link(download_page)
        print(f"Download link: {download_link}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No suitable download page found")
