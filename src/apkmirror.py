import time
import cloudscraper
from bs4 import BeautifulSoup

# Tạo đối tượng Cloudscraper với xác thực tự động
scraper = cloudscraper.create_scraper()

# Các thông số cơ bản
base_url = "https://www.apkmirror.com"
download_page_url = "https://www.apkmirror.com/apk/google-inc/youtube-music/youtube-music-7-22-51-release/"
filename = "youtube-music-7-22-51.apk"
max_retries = 3
wait_time = 10

# Headers chuẩn
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
    'Referer': download_page_url
}

# Hàm trích xuất liên kết tải xuống từ trang ban đầu
def extract_download_link(page: str) -> str:
    response = scraper.get(page, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    sub_url = soup.find('a', class_='downloadButton')
    if sub_url:
        return base_url + sub_url['href']
    return None

# Hàm xử lý tải xuống với cập nhật `key` tự động
def download_resource(url: str, name: str, max_retries: int = 3, wait_time: int = 10) -> str:
    filepath = f"./{name}"
    for attempt in range(max_retries):
        try:
            # Gửi yêu cầu tải xuống
            logging.info(f"Starting request to {url}. Attempt {attempt + 1}/{max_retries}.")
            with scraper.get(url, stream=True, allow_redirects=True, headers=headers) as final_res:
                if final_res.status_code == 403:
                    logging.warning(f"Access forbidden (403) at attempt {attempt + 1}. Updating `key`...")
                    new_link = extract_download_link(download_page_url)  # Cập nhật key mới
                    url = new_link  # Cập nhật lại URL với key mới
                    continue
                
                final_res.raise_for_status()
                total_size = int(final_res.headers.get('content-length', 0))
                downloaded_size = 0

                # Tải xuống và ghi vào tệp
                with open(filepath, "wb") as file:
                    for chunk in final_res.iter_content(chunk_size=8192):
                        if chunk:  # Ghi nếu chunk không rỗng
                            file.write(chunk)
                            downloaded_size += len(chunk)

                logging.info(f"Downloaded {name} successfully: {downloaded_size}/{total_size}")
                return filepath

        except Exception as e:
            logging.error(f"HTTP error at attempt {attempt + 1}: {e}")

        logging.info(f"Retrying after {wait_time} seconds...")
        time.sleep(wait_time)

    raise Exception(f"Failed to download {url} after {max_retries} attempts")


def download_apkmirror(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_page = get_download_page(version, app_name) 
    download_link = extract_download_link(download_page)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
