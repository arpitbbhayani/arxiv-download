import asyncio

from asyncio import Queue

from utils import get_logger
from download_utils import download_file_async


class JobQueue:
    def __init__(self, loop):
        self.loop = loop

        # The amount of parallelism
        self.max_workers = 25

        # Logger for the object instance
        self.logger = get_logger()

        # Asynchronous Queue to store job entry
        self.queue = Queue(loop=loop)

    def submit(self, entry):
        self.logger.debug("Submitting job {}".format(entry))

        # Adding entry to Queue
        self.queue.put_nowait(entry)

    @asyncio.coroutine
    def process(self):
        while True:
            # Infinite loop to process all items in the queue

            # Blocking call to Get
            queue_item = yield from self.queue.get()
            self.logger.debug('Processing Item {}'.format(queue_item))

            # Downloading file asynchronously
            yield from download_file_async(queue_item['link'],
                                           queue_item['file'])

            # Marking task as done
            self.queue.task_done()

    @asyncio.coroutine
    def start(self):
        # Creating Workers
        workers = [ asyncio.Task(self.process(), loop=self.loop)
                    for _ in range(self.max_workers) ]

        # Wait for some time before calling join
        yield from asyncio.sleep(3)

        # Waiting for queue to join
        yield from self.queue.join()

        # Cleaning up all workers
        for w in workers:
            w.cancel()
