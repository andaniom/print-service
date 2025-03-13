import threading
from queue import Queue

from api.logger import logger
from api.services.printer_service import print_pdf, print_image
from api.utils.pdf_util import convert_pdf_to_images


class PrintJobQueue:
    def __init__(self, maxsize=2000):
        self.queue = Queue(maxsize=maxsize)
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
    
    def process_queue_item(self, item):
        pdf_file, job_type, data = item
        if not pdf_file:
            return
        try:
            if job_type == "print":
                logger.info(f"Processing print job for {pdf_file} with key {data}")
                self._print_pdf(pdf_file, 1, data)
            elif job_type == "eticket":
                logger.info(f"Processing e-ticket print job for {pdf_file} with metadata {data}")
                for entry in data['data']:
                    self._print_pdf(pdf_file, entry['page'], entry['printer'])
        except Exception as e:
            logger.error(f"Failed to print {pdf_file}: {e}")

    def _print_pdf(self, pdf_file, page_number, printer_label):
        images = convert_pdf_to_images(pdf_file)
        print_image(images[page_number-1], printer_label)
        # print_pdf(pdf_file, page_number, printer_label)

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

    def enqueue_print_job(self, pdf_file, key):
        self.queue.put((pdf_file, "print", key))
        logger.info(f"Added job to print queue: {pdf_file}")

    def enqueue_eticket_job(self, pdf_file, metadata_json):
        self.queue.put((pdf_file, "eticket", metadata_json))
        logger.info(f"Added job to e-ticket queue: {pdf_file}")

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

def enqueue_print_job(pdf_file, key):
    print_job_queue.enqueue_print_job(pdf_file, key)

def enqueue_eticket_job(pdf_file, metadata_json):
    print_job_queue.enqueue_eticket_job(pdf_file, metadata_json)

def get_queue_status():
    return print_job_queue.get_queue_status()

def shutdown_workers():
    print_job_queue.shutdown()