import os
import zipfile
import glob
import fnmatch
import logging

from src.uptodown import (
    download_uptodown,
)

# Hàm giải nén XAPK và trả về đường dẫn đến file APK
def extract_xapk(xapk_path, extract_to='.'):
    # Đổi tên file thành zip nếu cần thiết
    if xapk_path.endswith('.xapk'):
        new_zip_path = xapk_path.replace('.xapk', '.zip')
        os.rename(xapk_path, new_zip_path)
        xapk_path = new_zip_path

    # Giải nén file xapk (hoặc zip)
    with zipfile.ZipFile(xapk_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    print(f"Extracted {xapk_path} to {extract_to}")

    # Tìm file APK đã giải nén
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith('.apk'):
                apk_path = os.path.join(root, file)
                print(f"Found APK: {apk_path}")
                return apk_path

    raise FileNotFoundError("No APK found in the XAPK.")

# Tải xuống XAPK từ Uptodown
input_xapk = download_uptodown('youtube')

# Giải nén XAPK và lấy đường dẫn tới APK
apk_path = extract_xapk(input_xapk, './extracted')

# Lưu kết quả APK vào GitHub Action artifact (nếu cần)
with open('apk_output.txt', 'w') as f:
    f.write(f"APK path: {apk_path}")
    print(f"APK path saved to apk_output.txt")
