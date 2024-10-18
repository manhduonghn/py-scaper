import logging 

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
