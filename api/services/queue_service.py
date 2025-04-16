import threading
from queue import Queue

from api.logger import logger
from api.services.printer_service import print_file


class PrintJobQueue:
    def __init__(self, maxsize=2000):
        self.queue = Queue(maxsize=maxsize)
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)

    def process_queue_item(self, item):
        file, job_type, data = item
        if not file:
            return
        try:
            if job_type == "print":
                logger.info(f"Processing print job for {file} with key {data}")
                self._print(file, 1, data)
            elif job_type == "eticket":
                logger.info(f"Processing e-ticket print job for {file} with metadata {data}")
                for entry in data['data']:
                    self._print(file, entry['page'], entry['printer'])
            elif job_type == "print-pk":
                logger.info(f"Processing print job for {file} with key {data}")
                self._print(file, 1, data)
        except Exception as e:
            logger.error(f"Failed to print {file}: {e}")
        finally:
            logger.info(f"Finished processing {file}")

    def _print(self, file, page_number, printer_label):
        print_file(file, page_number, printer_label)

    def worker(self):
        while True:
            item = self.queue.get()
            if item is None:  # Shutdown signal
                logger.info("Worker received shutdown signal.")
                break
            try:
                self.process_queue_item(item)
            finally:
                self.queue.task_done()

    def start(self):
        logger.info("Initializing workers...")
        self.worker_thread.start()

    def enqueue_print_job(self, file, key):
        self.queue.put((file, "print", key))
        logger.info(f"Added job to print queue: {file}")

    def enqueue_eticket_job(self, file, metadata_json):
        self.queue.put((file, "eticket", metadata_json))
        logger.info(f"Added job to e-ticket queue: {file}")

    def enqueue_print_pk_job(self, file, key):
        self.queue.put((file, "print-pk", key))
        logger.info(f"Added job to pk queue: {file}")

    def get_queue_status(self):
        return {
            "print_queue_size": self.queue.qsize(),
        }

    def shutdown(self):
        logger.info("Shutting down workers...")
        self.queue.put(None)
        self.worker_thread.join()
        logger.info("All workers have shut down.")


# Public functions
print_job_queue = PrintJobQueue()


def initialize_workers():
    print_job_queue.start()


def enqueue_print_job(file, key):
    print_job_queue.enqueue_print_job(file, key)


def enqueue_eticket_job(file, metadata_json):
    print_job_queue.enqueue_eticket_job(file, metadata_json)

def enqueue_print_pk_job(file, key):
    print_job_queue.enqueue_print_pk_job(file, key)


def get_queue_status():
    return print_job_queue.get_queue_status()


def shutdown_workers():
    print_job_queue.shutdown()