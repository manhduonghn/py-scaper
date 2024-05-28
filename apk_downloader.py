import cloudscraper
import logging
from bs4 import BeautifulSoup
import os

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
    yt_url = f"{base_url}/apk/facebook-2/messenger/messenger-{version.replace('.', '-')}-release/"

    response = scraper.get(yt_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    for sub_link in soup.find_all('a', class_='accent_color'):
        #print (sub_link)
        parent = sub_link.find_parent('div', class_='table-cell')
        # print (parent)
        if parent:
            texts = [parent.get_text(strip=True)] + [sib.get_text(strip=True) for sib in parent.find_next_siblings('div')]
            print (texts)
            if all(any(keyword in text for text in texts) for keyword in keywords):
                return base_url + sub_link['href']

    return None

def extract_download_link(page: str) -> str:
    base_url = "https://www.apkmirror.com"

    response = scraper.get(page)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    download_button = soup.find('a', class_='downloadButton')
    if download_button:
        download_page_url = base_url + download_button['href']
        response = scraper.get(download_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Sử dụng logic từ pup -p --charset utf-8 'a[rel="nofollow"] attr{href}'
        link = soup.select_one('a[rel="nofollow"]')['href']
        if link:
            return base_url + link

    return None

# Ví dụ sử dụng
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
version = "458.0.0.54.108"
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
