import os
import re
import cloudscraper
import logging
from bs4 import BeautifulSoup

# Từ khóa cần kiểm tra trong văn bản
keywords = ["APK", "universal", "nodpi"]

# Tạo một scraper với thông tin trình duyệt tùy chỉnh
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)
base_url = "https://www.apkmirror.com"

def get_download_page(version: str) -> str:
    url = f"{base_url}/apk/x-corp/twitter/twitter-{version.replace('.', '-')}-release/"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    for href_content in soup.find_all('a', class_='accent_color'):
        parent = href_content.find_parent('div', class_='table-cell')
        if parent:
            infos = [parent.get_text(strip=True)] + [sib.get_text(strip=True) for sib in parent.find_next_siblings('div')]
            if all(any(keyword in info for info in infos) for keyword in keywords):
                return base_url + href_content['href']

    return None

def extract_download_link(page: str) -> str:
    response = scraper.get(page)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    href_content = soup.find('a', class_='downloadButton')
    if href_content:
        download_page_url = base_url + href_content['href']
        response = scraper.get(download_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        href_content = soup.select_one('a[rel="nofollow"]')['href']
        if href_content:
            return base_url + href_content

    return None

def get_latest_version() -> str:
    url = f"{base_url}/uploads/?appcategory=twitter"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    app_rows = soup.find_all("div", class_="appRow")
    version_pattern = re.compile(r'\d+(\.\d+)*(-[a-zA-Z0-9]+(\.\d+)*)*')

    for row in app_rows:
        version_text = row.find("h5", class_="appRowTitle").a.text.strip()
        if "alpha" not in version_text.lower() and "beta" not in version_text.lower():
            match = version_pattern.search(version_text)
            if match:
                return match.group()

    return None

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
  
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
version = get_latest_version()
download_page = get_download_page(version)
download_link = extract_download_link(download_page)
filename = f"twitter-v{version}.apk"
download_resource(download_link,file_name)           
