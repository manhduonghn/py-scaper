import glob
import fnmatch
import logging
import subprocess

from src.uptodown import (
    download_uptodown,
    download_assets_from_repo
)

input_apk = download_uptodown('youtube')

url = f'https://github.com/REAndroid/APKEditor/releases/latest'

editor = download_assets_from_repo(url)

find_file = lambda pattern: next(
    filter(
        lambda file: glob.fnmatch.fnmatch(file, pattern), editor
    )
)

apk_editor = find_file('APKEditor*.jar')

logging.info(f"{apk_editor}")

lib_command = [
    'java',
    '-jar',
    apk_editor,
    'm',
    '-i',
    input_apk,
]

logging.info(f"Remove some architectures...")
# Thêm bufsize=1 và universal_newlines=True
process_lib = subprocess.Popen(lib_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)
        
# In stdout theo thời gian thực
for line in iter(process_lib.stdout.readline, ''):
    print(line.strip(), flush=True)  # In stdout với flush
        
# In stderr theo thời gian thực
for line in iter(process_lib.stderr.readline, ''):
    print(f"ERROR: {line.strip()}", flush=True)  # In stderr với flush
        
process_lib.stdout.close()
process_lib.stderr.close()
process_lib.wait()
