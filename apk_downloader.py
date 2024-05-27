import logging
import cloudscraper
from bs4 import BeautifulSoup

# Tạo một scraper với headers
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
)

version = "7.02.51"
apkmirror_url = "https://www.apkmirror.com"
apkmirror_yt_url = (
    f"https://www.apkmirror.com/apk/google-inc/youtube-music/youtube-music"
    + f"-{version.replace('.', '-')}-release/"
)

response = scraper.get(apkmirror_yt_url)
response.raise_for_status()

soup = BeautifulSoup(response.content, "html.parser")
links = soup.find_all('a', class_='accent_color')

# Khởi tạo danh sách lưu các URL hợp lệ
valid_urls = []

for link in links:
    # Kiểm tra phần tử tiếp theo của thẻ <a>
    next_sibling = link.find_next_sibling()
    if next_sibling and next_sibling.get_text() == 'APK':
        next_next_sibling = next_sibling.find_next_sibling()
        if next_next_sibling and (next_next_sibling.get_text() == 'arm64-v8a' or next_next_sibling.get_text() == 'nodpi'):
            valid_urls.append(link['href'])

print(valid_urls)
