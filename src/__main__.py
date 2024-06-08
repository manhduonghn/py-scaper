import logging
from src import downloader

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    apps = ["reddit", "x", "tiktok", "youtube", "youtube-music"]

    for app in apps:
        result = downloader.download_apkmirror(app)
        if result:
            logging.info(f"Downloaded {app} from APKMirror successfully.")
        else:
            logging.error(f"Failed to download {app} from APKMirror.")
        
        result = downloader.download_uptodown(app)
        if result:
            logging.info(f"Downloaded {app} from Uptodown successfully.")
        else:
            logging.error(f"Failed to download {app} from Uptodown.")
        
        result = downloader.download_apkpure(app)
        if result:
            logging.info(f"Downloaded {app} from APKPure successfully.")
        else:
            logging.error(f"Failed to download {app} from APKPure.")
