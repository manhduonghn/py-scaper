import glob
import fnmatch
import subprocess
import os

# Định nghĩa hàm find_file với xử lý lỗi
def find_file(pattern, directory='.'):
    files = glob.glob(f"{directory}/**", recursive=True)
    found_files = list(filter(lambda file: fnmatch.fnmatch(file, pattern), files))
    
    if not found_files:
        raise FileNotFoundError(f"No file found matching pattern {pattern} in directory {directory}")
    
    return found_files[0]  # Trả về file đầu tiên tìm thấy

# Hàm tải xuống APK từ uptodown
from src.uptodown import download_uptodown, download_assets_from_repo

# Tải xuống file APK từ uptodown
input_apk = download_uptodown('youtube')

# Tải xuống Apktool từ GitHub
url_apktool = 'https://github.com/iBotPeaches/Apktool/releases/latest'
apktool_jar = download_assets_from_repo(url_apktool)

# Tải xuống uber-apk-signer từ GitHub
url_signer = 'https://github.com/patrickfav/uber-apk-signer/releases/latest'
apk_signer_jar = download_assets_from_repo(url_signer)

# Kiểm tra xem thư mục có tồn tại không
if not os.path.exists(apktool_jar):
    raise FileNotFoundError(f"Directory {apktool_jar} does not exist. Check if the download was successful.")
if not os.path.exists(apk_signer_jar):
    raise FileNotFoundError(f"Directory {apk_signer_jar} does not exist. Check if the download was successful.")

# Sử dụng find_file để tìm các file .jar đã tải xuống
try:
    apktool = find_file('apktool*.jar', apktool_jar)
    apk_signer = find_file('uber-apk-signer*.jar', apk_signer_jar)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)  # Kết thúc chương trình nếu không tìm thấy tệp .jar

# Giải nén APK bằng Apktool
subprocess.run(['java', '-jar', apktool, 'd', '-f', '-o', 'output_dir', input_apk])

# Biên dịch lại APK
subprocess.run(['java', '-jar', apktool, 'b', 'output_dir', '-o', 'output_recompiled.apk'])

# Ký lại APK bằng uber-apk-signer
subprocess.run(['java', '-jar', apk_signer, '--apks', 'output_recompiled.apk'])
