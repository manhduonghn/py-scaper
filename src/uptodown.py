from requests_html import HTMLSession
import logging

# Tạo session với user-agent
def create_html_session():
    session = HTMLSession()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Android 13; Mobile; rv:125.0) Gecko/125.0 Firefox/125.0'
    })
    return session

# Lấy đường dẫn tải cho phiên bản cụ thể
def get_download_link(version: str, app_name: str) -> str:
    conf_file_path = f'./apps/uptodown/{app_name}.json'

    with open(conf_file_path, 'r') as json_file:
        config = json.load(json_file)
    
    url = f"https://{config['name']}.en.uptodown.com/android/versions"

    session = create_html_session()  # Tạo session
    response = session.get(url)
    response.html.render()  # Render trang để xử lý JavaScript

    # Tìm tất cả div chứa "data-url"
    divs = response.html.find("div[data-url]")
    
    # Lặp qua các div để tìm phiên bản mong muốn
    for div in divs:
        version_span = div.find("span.version", first=True)
        if version_span and version_span.text.strip() == version:
            dl_url = div.attrs['data-url']
            logging.info(f"Found download link for version {version}: {dl_url}")
            return dl_url
    
    logging.info("No matching version found.")
    return None

# Hàm chính để tải app từ Uptodown
def download_uptodown(app_name: str) -> str:
    version = "17.30.33"  # Thử lấy một phiên bản cụ thể
    download_link = get_download_link(version, app_name)
    
    if download_link:
        filename = f"{app_name}-v{version}.apk"
        # Tải tệp APK về
        session = create_html_session()
        response = session.get(download_link)

        with open(filename, 'wb') as file:
            file.write(response.content)
        
        logging.info(f"Downloaded {filename}")
        return filename
    else:
        logging.error("Failed to download the app.")
        return None

# Test hàm download
download_uptodown('youtube')
