import os
import re
import cloudscraper
import logging
from bs4 import BeautifulSoup

# Từ khóa cần kiểm tra trong văn bản
keywords = ["APK", "x86", "nodpi"]

# Tạo một scraper với thông tin trình duyệt tùy chỉnh
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_page(version: str) -> str:
    base_url = "https://www.apkmirror.com"
    url = f"{base_url}/apk/facebook-2/messenger/messenger-{version.replace('.', '-')}-release/"

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
    base_url = "https://www.apkmirror.com"

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

def get_latest_version():
    url = f"https://www.apkmirror.com/uploads/?appcategory=messenger"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    app_rows = soup.find_all("div", class_="appRow")
    version_pattern = re.compile(r'\d+(\.\d+)+')

    latest_version = None
    for row in app_rows:
        version_text = row.find("h5", class_="appRowTitle").a.text.strip()
        if "alpha" not in version_text.lower() and "beta" not in version_text.lower():
            match = version_pattern.search(version_text)
            if match:
                latest_version = match.group()
                break

# Ví dụ sử dụng
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
version = get_latest_version()
download_page = get_download_page(version)
if download_page:
    download_link = extract_download_link(download_page)
    print("Valid URL:", download_link)
    if download_link:
        filename = f"messenger-v{version}.apk"
        with open(filename, 'wb') as f:
            response = scraper.get(download_link)
            f.write(response.content)
        print("File downloaded successfully as", filename)
else:
    print("No valid download page found.")
