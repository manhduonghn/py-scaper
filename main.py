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
    input_apk,
]

logging.info(f"Remove some architectures...")
process_lib = subprocess.Popen(lib_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
# Print stdout and stderr in real-time with flush
for line in iter(process_lib.stdout.readline, b''):
    print(line.decode().strip(), flush=True)  # Direct print for stdout with flush
        
for line in iter(process_lib.stderr.readline, b''):
    print(f"ERROR: {line.decode().strip()}", flush=True)  # Direct print for stderr with flush
        
process_lib.stdout.close()
process_lib.stderr.close()
process_lib.wait()
