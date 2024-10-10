import os
import re
import json
import time
import logging
import cloudscraper
from urllib.parse import urljoin

from bs4 import BeautifulSoup

# Configuration
base_url = "https://www.apkmirror.com"
scraper = cloudscraper.create_scraper()
scraper.headers.update(
    {'User-Agent': 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0'}
)
logging.basicConfig(
  level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

    
def get_download_page(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'   
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)

    criteria = [config['type'], config['arch'], config['dpi']]
    url = (f"{base_url}/apk/{config['org']}/{config['name']}/"
           f"{config['name']}-{version.replace('.', '-')}-release/")
    response = scraper.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    
    soup = BeautifulSoup(response.content, "html.parser")

    rows = soup.find_all('div', class_='table-row headerFont')
    for row in rows:
        row_text = row.get_text()
        if all(criterion in row_text for criterion in criteria):
            sub_url = row.find('a', class_='accent_color')
            if sub_url:
                return base_url + sub_url['href']
    return None

def extract_download_link(page: str) -> str:
    response = scraper.get(page)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    
    soup = BeautifulSoup(response.content, "html.parser")

    sub_url = soup.find('a', class_='downloadButton')
    if sub_url:
        download_page_url = base_url + sub_url['href']
        response = scraper.get(download_page_url)
        response.raise_for_status()
        content_size = len(response.content)
        logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    
        soup = BeautifulSoup(response.content, "html.parser")

        button = soup.find('a', id='download-link')
        if button:
            return base_url + button['href']

    return None

def get_latest_version(app_name: str) -> str:
    conf_file_path = f'./apps/apkmirror/{app_name}.json'    
    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
        
    url = f"{base_url}/uploads/?appcategory={config['name']}"

    response = scraper.get(url)
    response.raise_for_status()
    content_size = len(response.content)
    logging.info(f"URL:{response.url} [{content_size}/{content_size}] -> \"-\" [1]")
    
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


def download_resource(url: str, name: str, wait_time: int = 10, max_retries: int = 3) -> str:
    filepath = f"./{name}"

    for attempt in range(max_retries):
        try:
            # Gửi yêu cầu ban đầu để bắt được quá trình chuyển hướng và xác thực
            logging.info(f"Starting request to {url}. Attempt {attempt + 1}/{max_retries}.")
            
            # Thực hiện yêu cầu và cho phép chuyển hướng
            res = scraper.get(url, stream=True, allow_redirects=True)
            
            # Kiểm tra nếu yêu cầu trả về trạng thái cần xác thực hoặc chuyển hướng
            if res.status_code in [301, 302, 303, 307, 308]:
                logging.info(f"Redirected to {res.headers['Location']}")
                # Theo dõi URL chuyển hướng mới
                url = urljoin(url, res.headers['Location'])

                # Đợi một khoảng thời gian trước khi tiếp tục
                logging.info(f"Waiting for {wait_time} seconds before following redirect.")
                time.sleep(wait_time)

            # Thực hiện yêu cầu tới URL cuối cùng sau khi đợi chuyển hướng
            with scraper.get(url, stream=True, allow_redirects=True) as final_res:
                final_res.raise_for_status()  # Kiểm tra mã trạng thái HTTP

                # Lấy URL cuối cùng sau khi xử lý chuyển hướng và log URL
                final_url = final_res.url
                total_size = int(final_res.headers.get('content-length', 0))
                downloaded_size = 0

                # Tải tệp xuống và ghi vào đĩa
                with open(filepath, "wb") as file:
                    for chunk in final_res.iter_content(chunk_size=8192):
                        if chunk:  # Ghi nếu chunk không rỗng
                            file.write(chunk)
                            downloaded_size += len(chunk)

                logging.info(
                    f"URL: {final_url} [{downloaded_size}/{total_size}] -> \"{name}\" [Success]"
                )
                return filepath

        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logging.error(f"Cloudflare challenge error at attempt {attempt + 1}/{max_retries}: {e}")
        except cloudscraper.exceptions.RequestException as e:
            logging.error(f"HTTP error at attempt {attempt + 1}/{max_retries}: {e}")

        # Đợi một chút trước khi thử lại
        logging.info(f"Retrying after {wait_time} seconds...")
        time.sleep(wait_time)

    # Nếu vượt quá số lần thử, thông báo lỗi
    raise Exception(f"Failed to download {url} after {max_retries} attempts")
    
def download_apkmirror(app_name: str) -> str:
    version = get_latest_version(app_name)
    download_page = get_download_page(version, app_name) 
    download_link = extract_download_link(download_page)
    filename = f"{app_name}-v{version}.apk"
    return download_resource(download_link, filename)
