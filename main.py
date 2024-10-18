import logging 

from src.uptodown import (
    download_uptodown,
    download_assets_from_repo
)

download_uptodown('youtube')

url = f'https://github.com/REAndroid/APKEditor/releases/latest'

editor = download_assets_from_repo(url)
logging.info(f"{editor}")
