import cloudscraper
from bs4 import BeautifulSoup

def get_download_page(version: str) -> str:
    
    keywords = ["APK", "arm64-v8a", "nodpi"]
    
    scraper = cloudscraper.create_scraper(
        browser={
            'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )

    apkmirror_url = "https://www.apkmirror.com"
    apkmirror_yt_url = (
        f"https://www.apkmirror.com/apk/google-inc/youtube-music/youtube-music"
        + f"-{version.replace('.', '-')}-release/"
    )

    response = scraper.get(apkmirror_yt_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    sub_links = soup.find_all('a', class_='accent_color')

    # Khởi tạo danh sách lưu các URL hợp lệ
    sub_urls= []

    for sub_link in sub_links:
        parent = sub_link.find_parent('div', class_='table-cell')
        if parent:
            siblings = parent.find_next_siblings('div')
            # Kết hợp nội dung của thẻ cha và các phần tử liền kề để kiểm tra
            texts = [parent.get_text(strip=True)] + [sibling.get_text(strip=True) for sibling in siblings]

            # Kiểm tra xem tất cả các từ khóa đều có trong texts không
            if all(any(keyword in text for text in texts) for keyword in keywords):
                sub_urls.append(sub_link['href'])

    return apkmirror_url + sub_urls

# Ví dụ sử dụng
version = "7.02.51"
# Tùy chỉnh các từ khóa bạn muốn tìm
valid_urls = get_download_page(version)
print("Valid URLs:", valid_urls)
