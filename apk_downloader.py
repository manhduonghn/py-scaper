import logging
import cloudscraper
from bs4 import BeautifulSoup

# Tạo một scraper với headers
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
)

def get_download_page(version: str) -> str:
    apkmirror_url = "https://www.apkmirror.com"
    apkmirror_yt_url = (
        f"https://www.apkmirror.com/apk/google-inc/youtube-music/youtube-music"
        + f"-{version.replace('.', '-')}-release/"
    )

    response = scraper.get(apkmirror_yt_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    yt_links = soup.find_all("div", attrs={"class": "table-row headerFont"})
    yt_apk_page = apkmirror_url

    for link in yt_links[1:]:
        if link.find_all("span", attrs={"class": "apkm-badge"})[0].text == "APK":
            yt_apk_page += link.find_all("a", attrs={"class": "accent_color"})[0]["href"]
            break

    return yt_apk_page

def extract_download_link(page: str) -> str:
    apkmirror_url = "https://www.apkmirror.com"

    res = scraper.get(page)
    res.raise_for_status()

    soup = BeautifulSoup(res.content, "html.parser")
    apk_dl_page = soup.find_all("a", attrs={"class": "accent_bg"})
    apk_dl_page_url = apkmirror_url + apk_dl_page[0]["href"]

    res = scraper.get(apk_dl_page_url)
    res.raise_for_status()

    soup = BeautifulSoup(res.content, "html.parser")
    apk_page_details = soup.find_all("a", attrs={"rel": "nofollow"})
    apk_link = apkmirror_url + apk_page_details[0]["href"]

    return apk_link

def download_file_with_cloudscraper(url: str, filename: str):
    with open(filename, "wb") as f:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, stream=True)
        if response.status_code == 200:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        else:
            logging.error(f"Failed to download file from {url}")

# Ví dụ sử dụng:
version = "7.02.51"
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
try:
    download_page_url = get_download_page(version)
    download_link = extract_download_link(download_page_url)
    logging.info(f"Download link for YouTube version {version}: {download_link}")

    # Tên file để lưu
    filename = f"YouTube_v{version}.apk"
    # Thực hiện tải tệp
    download_file_with_cloudscraper(download_link, filename)
    logging.info(f"File downloaded successfully as {filename}")
except Exception as e:
    logging.erro(f"Error: {e}")
