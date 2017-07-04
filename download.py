import os
import asyncio
import argparse
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlencode

from utils import get_logger, get_filepath
import download_utils


def download_arxiv_papers(url, all=False, quiet=False, verbose=False, output_dir="", loop=None):
    logger = get_logger()
    logger.info("URL: {}".format(url))
    logger.info("Download All? {}".format(all))
    logger.info("Output Directory? {}".format(output_dir))
    logger.info("Quiet? {}".format(quiet))
    logger.info("Verbose? {}".format(verbose))

    if not all:
        download_one(url, output_dir=output_dir, loop=loop)
        return

    skip = 0
    count = True  # Simulate do-while loop

    while count != 0:
        u = urlsplit(url)
        q = parse_qs(u.query)
        q['skip'] = skip
        q['per_page'] = 3
        q['query_id'] = q['query_id'][0]

        url = urlunsplit((u.scheme, u.netloc, u.path, urlencode(q), u.fragment))
        count = download_one(url, output_dir=output_dir, loop=loop)

        skip += 3


def download_one(url, output_dir="", loop=None):
    logger = get_logger()
    logger.info("Requesting URL: " + url)
    r = requests.get(url)

    logger.debug("Response status code {}".format(r.status_code))

    if r.status_code != 200:
        logger.error("Received {} while hitting URL {}".format(r.status_code, url))

    soup = BeautifulSoup(r.content, "html.parser")
    links = ['https://arxiv.org' + dt.find("a", text="pdf").get("href") for dt in soup.findAll("dt")]
    titles = [dd.find("div", {"class": "list-title"}).contents[2] for dd in soup.findAll("dd")]

    if len(links) != len(titles):
        logger.error("Number of links and titles do not match.")
        logger.error("links = {} and titles = {}".format(len(links), len(titles)))
        return

    batch = [{'link': x[0],
              'title': x[1],
              'file': get_filepath(output_dir, x[1])
             } for x in zip(links, titles)]

    logger.info("Found {} pdfs".format(len(batch)))
    download_utils.download_batch(batch, loop=loop)

    return len(batch)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    parser = argparse.ArgumentParser(description='Download all research papers (pdfs) from arxiv')
    parser.add_argument('url', type=str, help='search url')
    parser.add_argument('--output-dir', type=str, help='Output Directory where all PDFs should be saved', default="")
    parser.add_argument('--all', help='go through all pages and download all', action="store_true")
    parser.add_argument('-q', '--quiet', help='No output', action="store_true")
    parser.add_argument('-v', '--verbose', help='All sort of output', action="store_true")

    args = parser.parse_args().__dict__
    url = args.pop('url')

    # Initializing logger
    get_logger(quiet=args.get('quiet'), verbose=args.get('verbose'))

    download_arxiv_papers(url, loop=loop, **args)
