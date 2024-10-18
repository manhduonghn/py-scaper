import glob
import fnmatch

# Định nghĩa hàm find_file để tìm file .jar theo pattern
find_file = lambda pattern: next(
    filter(
        lambda file: glob.fnmatch.fnmatch(file, pattern), editor
    )
)

import subprocess

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

# Sử dụng find_file để tìm các file .jar đã tải xuống
apktool = find_file('apktool*.jar', apktool_jar)
apk_signer = find_file('uber-apk-signer*.jar', apk_signer_jar)

# Giải nén APK bằng Apktool
subprocess.run(['java', '-jar', apktool, 'd', '-f', '-o', 'output_dir', input_apk])

# Biên dịch lại APK
subprocess.run(['java', '-jar', apktool, 'b', 'output_dir', '-o', 'output_recompiled.apk'])

# Ký lại APK bằng uber-apk-signer
subprocess.run(['java', '-jar', apk_signer, '--apks', 'output_recompiled.apk'])
