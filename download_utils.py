import os
import aiohttp

from utils import get_logger


def download_file_async(url, filepath):
    """Downloads file at url asynchronously and stores it to filepath
    """
    logger = get_logger()

    logger.info("Downloading {}".format(url))

    session = aiohttp.ClientSession()
    r = yield from session.get(url)

    logger.debug("Response Status Code {}".format(r.status))
    if r.status != 200:
        logger.warn("Unable to download from URL {}".format(url))

    content = yield from r.read()
    r.close()
    session.close()

    logger.debug("Writing to file {}".format(filepath))

    with open(filepath, 'wb') as f:
        f.write(content)

    logger.info("Download complete. File saved at {}".format(filepath))

    return True
