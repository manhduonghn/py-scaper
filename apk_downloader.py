import cloudscraper
import logging
from bs4 import BeautifulSoup
import os
import re

# Tạo một scraper với thông tin trình duyệt tùy chỉnh
scraper = cloudscraper.create_scraper(
    browser={
        'custom': 'Mozilla/5.0'
    }
)

url = f"https://www.apkmirror.com/uploads/?appcategory=youtube"

response = scraper.get(url)
response.raise_for_status()
soup = BeautifulSoup(response.content, "html.parser")

# Tìm tất cả các phiên bản ứng dụng
app_rows = soup.find_all("div", class_="appRow")

# Chuẩn bị biểu thức chính quy để tìm số phiên bản
version_pattern = re.compile(r'\d+(\.\d+)+')

# Duyệt qua từng phiên bản để tìm phiên bản cao nhất không phải alpha hoặc beta
latest_version = None
for row in app_rows:
    version_text = row.find("h5", class_="appRowTitle").a.text.strip()
    if "alpha" not in version_text.lower() and "beta" not in version_text.lower():
        match = version_pattern.search(version_text)
        if match:
            latest_version = match.group()
            break

print("Phiên bản mới nhất không phải alpha hoặc beta là:", latest_version)
