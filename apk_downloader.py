import cloudscraper
from bs4 import BeautifulSoup

keywords = ["APK", "armeabi-v7a", "nodpi"]

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
    sub_links = soup.find_all('a', class_='accent_color')

    for sub_link in sub_links:
        parent = sub_link.find_parent('div', class_='table-cell')
        if parent:
            siblings = parent.find_next_siblings('div')
            # Combine text from parent and siblings to check
            texts = [parent.get_text(strip=True)] + [sibling.get_text(strip=True) for sibling in siblings]

            # Check if all keywords are present in the combined texts
            if all(any(keyword in text for text in texts) for keyword in keywords):
                return apkmirror_url + sub_link['href']

    return None

def extract_download_link(page: str) -> str:

    response = scraper.get(page)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    # Tìm liên kết đầu tiên có href chứa 'key='
    link = soup.find('a', href=lambda href: href and 'key=' in href)

    # Lấy giá trị href nếu tìm thấy liên kết hợp lệ
    valid_url = link['href'] if link else None

    return valid_url

# Example usage
version = "7.02.51"
# Call the function and print the valid URL
download_page = get_download_page(version)
if download_page:
    valid_url = extract_download_link(download_page)
    print("Valid URL:", valid_url)
else:
    print("No valid download page found.")
