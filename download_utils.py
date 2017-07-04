import os
import asyncio
import requests
import concurrent.futures

from utils import get_logger


def _download_one(url, filepath):
    logger = get_logger()

    logger.info("Downloading {}".format(url))
    r = requests.get(url)

    if r.status_code != 200:
        logger.warn("Unable to download from URL {}".format(url))

    logger.debug("Response Status Code {}".format(r.status_code))
    logger.debug("Writing to file {}".format(filepath))

    with open(filepath, 'wb') as f:
        f.write(r.content)

    logger.info("Download complete. File saved at {}".format(filepath))


def _download_batch(batch, loop=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                _download_one,
                b['link'],
                b['file']
            )
            for b in batch
        ]
        yield from asyncio.gather(*futures)


def download_batch(batch, loop=None):
    loop.run_until_complete(_download_batch(batch, loop=loop))
