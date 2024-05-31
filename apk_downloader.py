import os
import re
import cloudscraper
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_page(version: str) -> str:
    url = f"https://youtube.en.uptodown.com/android/versions"

    response = scraper.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Tìm tất cả các thẻ div có thuộc tính data-url
    divs = soup.find_all("div", {"data-url": True})

    # Biến để kiểm soát việc dừng tìm kiếm
    found = False

    # Duyệt qua từng thẻ div để tìm version tương ứng
    for div in divs:
        version_span = div.find("span", class_="version")
        if version_span and version_span.text.strip() == version:
            data_url = div["data-url"]
            logging.debug("Data URL của phiên bản %s là: %s", version, data_url)
            found = True
            break

    # Nếu tìm thấy data-url, trả về nó
    if found:
        return data_url
    else:
        logging.debug("Không tìm thấy data-url cho phiên bản %s", version)
        return ""

version="19.20.32"
get_download_page(version)
