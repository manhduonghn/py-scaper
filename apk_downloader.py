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
        # Tìm tất cả các thẻ <span> bên trong thẻ cha và kiểm tra xem có chứa "APK" không
        spans = parent.find_all('span')
        apk_found = any('APK' in span.get_text(strip=True) for span in spans)
        
        if apk_found:
            siblings = parent.find_next_siblings('div')
            # Kiểm tra các phần tử liền kề
            arm64_v8a_found = any('arm64-v8a' in sibling.get_text(strip=True) for sibling in siblings)
            nodpi_found = any('nodpi' in sibling.get_text(strip=True) for sibling in siblings)
            
            if arm64_v8a_found and nodpi_found:
                valid_urls.append(link['href'])

print("Valid URLs:", valid_urls)
