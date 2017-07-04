import os
import sys
import logging

from slugify import slugify
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

logger = None


def to_slug(name):
    """Converts a string to its slug
    """
    return slugify(name).lower()


def get_url(url, skip, page_size):
    """Returns the url with updated skip and per_page as required by arxiv.org
    """
    u = urlsplit(url)
    q = parse_qs(u.query)
    q['skip'] = skip
    q['per_page'] = page_size
    q['query_id'] = q['query_id'][0]

    return urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), u.fragment))


def get_filepath(output_dir, title):
    """Returns the filepath for Research paper title.
    """
    filename = to_slug(title) + ".pdf"
    return os.path.join(output_dir, filename)


def get_logger(quiet=False, verbose=False):
    """Returns the logger
    """
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
    """Configring the logger
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
