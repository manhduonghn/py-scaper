import subprocess
import glob
import fnmatch

# Hàm tải xuống APK từ uptodown
from src.uptodown import download_uptodown, download_assets_from_repo

input_apk = download_uptodown('youtube')

# Tìm file Apktool và uber-apk-signer từ repo hoặc thư mục
url_apktool = 'https://github.com/iBotPeaches/Apktool/releases/latest'
apktool_jar = download_assets_from_repo(url_apktool)

url_signer = 'https://github.com/patrickfav/uber-apk-signer/releases/latest'
apk_signer_jar = download_assets_from_repo(url_signer)

# Tìm các file jar đã tải về
apktool = find_file('apktool*.jar', apktool_jar)
apk_signer = find_file('uber-apk-signer*.jar', apk_signer_jar)

# Giải nén APK
subprocess.run(['java', '-jar', apktool, 'd', '-f', '-o', 'output_dir', input_apk])

# Biên dịch lại APK
subprocess.run(['java', '-jar', apktool, 'b', 'output_dir', '-o', 'output_recompiled.apk'])

# Ký lại APK
subprocess.run(['java', '-jar', apk_signer, '--apks', 'output_recompiled.apk'])
