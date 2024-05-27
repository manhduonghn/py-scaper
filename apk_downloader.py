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
        f"https://www.apkmirror.com/apk/google-inc/youtube/youtube"
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

# Ví dụ sử dụng:
version = "18.45.43"  # Thay đổi phiên bản YouTube tùy theo nhu cầu
try:
    download_page_url = get_download_page(version)
    download_link = extract_download_link(download_page_url)
    print(f"Download link for YouTube version {version}: {download_link}")
except Exception as e:
    print(f"Error: {e}")
