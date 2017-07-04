import os
import aiohttp
import asyncio
import argparse

from bs4 import BeautifulSoup

from utils import get_logger, get_filepath, get_url
from job_queue import JobQueue


def submit_job(batch, queue, output_dir=""):
    """Adds file to batch entry and adds it to JobQueue
    """
    for b in batch:
        # Add output filepath to the batch entry
        b['file'] = get_filepath(output_dir, b['title'])

        # Submit the entry to JobQueue
        queue.submit(b)


@asyncio.coroutine
def extract_and_submit(url, queue, all=False, output_dir=""):
    """Extracts links to research papers and submits job to JobQueue
    """
    if all == False:
        links = yield from get_batch(url)
        submit_job(links, queue, output_dir=output_dir)
        return None

    skip = 0
    page_size = 25
    links = [True]  # do-while loop simulation

    while links:
        url = get_url(url, skip, page_size)
        links = yield from get_batch(url)
        submit_job(links, queue, output_dir=output_dir)
        skip += page_size

    return None


def get_batch(url):
    """Returns the batch containing the links and titles of the research paper
    to download
    """
    logger = get_logger()
    content = None

    logger.info("Requesting URL: " + url)

    # Grabbing the session
    session = aiohttp.ClientSession()

    # Hitting the URL
    r = yield from session.get(url)

    logger.debug("Response status code {}".format(r.status))
    if r.status != 200:
        logger.error("Received {} while hitting URL {}".format(r.status, url))

    # Reading Contents
    content = yield from r.text()

    # Closing and Cleaning
    r.close()
    session.close()

    # Extracting Links and Titles
    soup = BeautifulSoup(content, "html.parser")
    links = []
    for dt in soup.findAll("dt"):
        a = dt.find("a", text="pdf")
        if a:
            links.append('https://arxiv.org' + a.get('href'))
        else:
            links.append(None)

    titles = [ dd.find("div", {"class": "list-title"}).contents[2]
               for dd in soup.findAll("dd") ]

    # Error case - should not occur though!
    if len(links) != len(titles):
        logger.error("Number of links and titles do not match.")
        logger.error("links = {} and titles = {}".format(len(links),
                                                         len(titles)))
        raise Exception("Something is wrong with the script")

    # Compiling batch
    batch = [{'link': x[0], 'title': x[1]} for x in zip(links, titles) if x[0]]

    logger.info("Found {} pdfs".format(len(batch)))
    return batch


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Argument Parser
    parser = argparse.ArgumentParser(description='Download all research'
                                     ' papers (pdfs) from arxiv.org')
    parser.add_argument('url', type=str, help='search url; it should have'
                        ' query_id parameter in it. It will look something like'
                        ' this: "https://arxiv.org/find/all/1/all:+Wikipedia/0/'
                        '1/0/all/0/1?skip=0&query_id=a82ebfd0195719df"')
    parser.add_argument('--output-dir', type=str, help='Output directory where'
                        ' all PDFs should be saved', default="")
    parser.add_argument('--all', help='Go through all pages and download'
                        ' everything', action="store_true")
    parser.add_argument('-q', '--quiet', help='No output at all',
                        action="store_true")
    parser.add_argument('-v', '--verbose', help='All sort of output messages',
                        action="store_true")

    args = parser.parse_args().__dict__
    url = args['url']

    # Initializing logger
    get_logger(quiet=args.get('quiet'), verbose=args.get('verbose'))

    logger = get_logger()
    logger.info("URL: {}".format(url))
    logger.info("Download All? {}".format(args['all']))
    logger.info("Output Directory? {}".format(args['output_dir']))
    logger.info("Quiet? {}".format(args['quiet']))
    logger.info("Verbose? {}".format(args['verbose']))

    del args['url']
    del args['quiet']
    del args['verbose']

    queue = JobQueue(loop)

    loop.run_until_complete(asyncio.gather(
        queue.start(),
        extract_and_submit(url, queue, **args),
    ))
    loop.close()
