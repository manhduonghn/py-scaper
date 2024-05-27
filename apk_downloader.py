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

    print(f"Fetching URL: {apkmirror_yt_url}")
    response = scraper.get(apkmirror_yt_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    print("HTML content of the page fetched successfully.")
    
    yt_links = soup.find_all("div", attrs={"class": "table-row headerFont"})
    print(f"yt_links")
    exit (0)
    print(f"Found {len(yt_links)} links with class 'table-row headerFont'.")

    yt_apk_page = apkmirror_url

    for link in yt_links[1:]:
        badges = link.find_all("span", attrs={"class": "apkm-badge"})
        if not badges:
            continue
        print(f"Found badge: {badges[0].text.strip()}")
        if badges[0].text.strip() == "APK":
            accent_links = link.find_all("a", attrs={"class": "accent_color"})
            if accent_links:
                yt_apk_page += accent_links[0]["href"]
                print(f"Found APK page URL: {yt_apk_page}")
                break

    return yt_apk_page

def extract_download_link(page: str) -> str:
    apkmirror_url = "https://www.apkmirror.com"

    print(f"Fetching download page URL: {page}")
    res = scraper.get(page)
    res.raise_for_status()

    soup = BeautifulSoup(res.content, "html.parser")
    print("HTML content of the download page fetched successfully.")
    
    apk_dl_page = soup.find_all("a", attrs={"class": "accent_bg"})
    if not apk_dl_page:
        raise Exception("No download link found on the download page.")
    apk_dl_page_url = apkmirror_url + apk_dl_page[0]["href"]
    print(f"Found intermediate APK download page URL: {apk_dl_page_url}")

    res = scraper.get(apk_dl_page_url)
    res.raise_for_status()

    soup = BeautifulSoup(res.content, "html.parser")
    print("HTML content of the intermediate download page fetched successfully.")
    
    apk_page_details = soup.find_all("a", attrs={"rel": "nofollow"})
    if not apk_page_details:
        raise Exception("No APK download link found on the intermediate page.")
    apk_link = apkmirror_url + apk_page_details[0]["href"]
    print(f"Found final APK download link: {apk_link}")

    return apk_link

# Ví dụ sử dụng:
version = "18.45.43"  # Thay đổi phiên bản YouTube tùy theo nhu cầu
try:
    download_page_url = get_download_page(version)
    download_link = extract_download_link(download_page_url)
    print(f"Download link for YouTube version {version}: {download_link}")
except Exception as e:
    print(f"Error: {e}")
