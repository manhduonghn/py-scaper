import cloudscraper
from bs4 import BeautifulSoup

keywords = ["APK", "universal", "nodpi"]
base_url = "https://www.apkmirror.com"

# Tạo một scraper với user agent tùy chỉnh
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

def get_download_page(version: str) -> str:
    """
    Lấy đường dẫn đến trang tải về dựa trên phiên bản YouTube.
    """
    yt_url = f"{base_url}/apk/google-inc/youtube/youtube-{version.replace('.', '-')}-release/"
    response = scraper.get(yt_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    # Duyệt qua tất cả các liên kết có lớp 'accent_color'
    for link in soup.find_all('a', class_='accent_color'):
        parent_div = link.find_parent('div', class_='table-cell')
        if not parent_div:
            continue

        texts = [parent_div.get_text(strip=True)] + \
                [sibling.get_text(strip=True) for sibling in parent_div.find_next_siblings('div')]

        # Kiểm tra nếu tất cả các từ khóa đều xuất hiện trong các văn bản
        if all(any(keyword.lower() in text.lower() for text in texts) for keyword in keywords):
            return f"{base_url}{link['href']}"

    return None

def extract_download_link(page_url: str) -> str:
    """
    Trích xuất liên kết tải về thực sự từ trang tải về.
    """
    response = scraper.get(page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    download_button = soup.find('a', class_='downloadButton')
    if not download_button:
        raise Exception("Không tìm thấy nút tải về trên trang")

    download_page_url = f"{base_url}{download_button['href']}"
    response = scraper.get(download_page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    direct_link = soup.select_one('a[rel="nofollow"]')
    if not direct_link:
        raise Exception("Không tìm thấy liên kết tải về cuối cùng")

    return f"{base_url}{direct_link['href']}"

# Ví dụ sử dụng
version = "17.03.35"
download_page = get_download_page(version)
if download_page:
    try:
        download_link = extract_download_link(download_page)
        print(f"Download link: {download_link}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Không tìm thấy trang tải về phù hợp")
