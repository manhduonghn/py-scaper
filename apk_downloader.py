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
    parent = link.find_parent('div', class_='table-cell')
    if parent:
        siblings = parent.find_next_siblings('div')
        if len(siblings) >= 3:
            if 'APK' in siblings[0].get_text() and ('arm64-v8a' in siblings[1].get_text() or 'nodpi' in siblings[2].get_text()):
                valid_urls.append(link['href'])

print(valid_urls)
