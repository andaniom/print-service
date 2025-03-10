import threading
from queue import Queue

from api.logger import logger
from api.services.printer_service import print_pdf

# Queue
print_queue = Queue()

# Worker threads
threads = []

# Worker functions
def process_queue_item(item):
    pdf_file, key, metadata_json = item
    if not pdf_file:
        return
    try:
        logger.info(f"Processing print job for {pdf_file} with key {key} and metadata {metadata_json}")
        if metadata_json:
            for entry in metadata_json['data']:
                printer_label = entry['printer']
                page_number = entry['page']
                print_pdf(pdf_file, page_number, printer_label)
        else:
            printer_label = key
            print_pdf(pdf_file, 1, printer_label)
    except Exception as e:
        logger.error(f"Failed to print {pdf_file}: {e}")

# Worker thread logic
def worker(queue):
    while True:
        item = queue.get()
        if item is None:  # Shutdown signal
            logger.info("Worker received shutdown signal.")
            break
        try:
            process_queue_item(item)
        finally:
            queue.task_done()

# Public functions
def initialize_workers():
    global threads
    logger.info("Initializing workers...")
    for _ in range(4):  # Workers
        t = threading.Thread(target=worker, args=(print_queue,), daemon=True)
        t.start()
        threads.append(t)

def enqueue_print_job(pdf_file, key):
    print_queue.put((pdf_file, key, None))
    logger.info(f"Added job to print queue: {pdf_file}")

def enqueue_eticket_job(pdf_file, metadata_json):
    print_queue.put((pdf_file, None, metadata_json))
    logger.info(f"Added job to e-ticket queue: {pdf_file}")

def get_queue_status():
    return {
        "queue_size": print_queue.qsize(),
    }

def shutdown_workers():
    logger.info("Shutting down workers...")
    print_queue.put(None)
    for thread in threads:
        thread.join(timeout=10)
    logger.info("All workers have shut down.")