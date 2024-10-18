import os
import zipfile
import shutil
import subprocess
from src.uptodown import download_uptodown

# Hàm giải nén XAPK và trả về danh sách các file APK
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

    # Tìm tất cả các file APK đã giải nén
    apk_paths = []
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith('.apk'):
                apk_path = os.path.join(root, file)
                apk_paths.append(apk_path)
                print(f"Found APK: {apk_path}")

    if not apk_paths:
        raise FileNotFoundError("No APK found in the XAPK.")
    
    return apk_paths

# Hàm hợp nhất APK
def merge_apks(apk_paths, output_path):
    if len(apk_paths) < 2:
        print("Not enough APKs to merge.")
        return apk_paths[0] if apk_paths else None

    temp_dir = './temp_apk_merge'
    os.makedirs(temp_dir, exist_ok=True)

    # Giải nén tất cả APK vào thư mục tạm
    for apk in apk_paths:
        output_dir = os.path.join(temp_dir, os.path.basename(apk).replace('.apk', ''))
        os.makedirs(output_dir, exist_ok=True)
        # Giải nén APK
        subprocess.run(['java', '-jar', 'apktool.jar', 'd', apk, '-o', output_dir], check=True)

    # Hợp nhất tài nguyên và mã
    merged_dir = os.path.join(temp_dir, 'merged')
    os.makedirs(merged_dir, exist_ok=True)

    # Kết hợp các thư mục
    for apk in os.listdir(temp_dir):
        if apk != 'merged' and os.path.isdir(os.path.join(temp_dir, apk)):
            for root, dirs, files in os.walk(os.path.join(temp_dir, apk)):
                for file in files:
                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(merged_dir, file)
                    if os.path.exists(dest_file):
                        # Nếu file đã tồn tại, bạn cần xử lý xung đột
                        print(f"Conflict found: {dest_file} exists. Skipping...")
                    else:
                        shutil.copy2(src_file, dest_file)

    # Tái tạo APK hợp nhất
    merged_apk_path = os.path.join(output_path, 'merged_app.apk')
    subprocess.run(['java', '-jar', 'apktool.jar', 'b', merged_dir, '-o', merged_apk_path], check=True)

    # Dọn dẹp
    shutil.rmtree(temp_dir)

    print(f"Merged APK created at: {merged_apk_path}")
    return merged_apk_path

# Tải xuống XAPK từ Uptodown
input_xapk = download_uptodown('youtube')

# Giải nén XAPK và lấy danh sách các file APK
apk_paths = extract_xapk(input_xapk, './extracted')

# Hợp nhất các APK
merged_apk_path = merge_apks(apk_paths, './merged_apks')

# Lưu kết quả APK vào GitHub Action artifact (nếu cần)
with open('apk_output.txt', 'w') as f:
    f.write(f"Merged APK path: {merged_apk_path}")
    print(f"Merged APK path saved to apk_output.txt")
