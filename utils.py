import os
import sys
import logging
from slugify import slugify

logger = None


def to_slug(name):
    return slugify(name).lower()


def get_filepath(output_dir, title):
    filename = to_slug(title) + ".pdf"
    return os.path.join(output_dir, filename)


def get_logger(quiet=False, verbose=False):
    global logger

    if logger is None:
        logger = logging.getLogger('arxiv-scrapper')
        _configure_logger(logger)

        if quiet:
            logger.setLevel(logging.ERROR)
        else:
            if verbose:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)

    return logger


def _configure_logger(logger):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
