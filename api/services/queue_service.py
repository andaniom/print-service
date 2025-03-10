import threading
from queue import Queue

from api.logger import logger
from api.services.printer_service import print_pdf

# Queues
print_queue = Queue(maxsize=1000)
print_queue_eticket = Queue(maxsize=1000)

# Worker threads
threads = []

# Worker functions
def process_queue_item(item):
    pdf_file, key = item
    if not pdf_file:
        return
    try:
        logger.info(f"Processing print job for {pdf_file} with key {key}")
        printer_label = key
        print_pdf(pdf_file, 1, printer_label)
    except Exception as e:
        logger.error(f"Failed to print {pdf_file}: {e}")

def process_queue_item_eticket(item):
    pdf_file, metadata_json = item
    if not pdf_file:
        return
    try:
        logger.info(f"Processing e-ticket print job for {pdf_file} with metadata {metadata_json}")
        for entry in metadata_json['data']:
            printer_label = entry['printer']
            page_number = entry['page']
            print_pdf(pdf_file, page_number, printer_label)
    except Exception as e:
        logger.error(f"Failed to print e-ticket {pdf_file}: {e}")

# Worker thread logic
def worker(queue, process_function):
    while True:
        item = queue.get()
        if item is None:  # Shutdown signal
            logger.info("Worker received shutdown signal.")
            break
        try:
            process_function(item)
        finally:
            queue.task_done()

# Public functions
def initialize_workers():
    global threads
    logger.info("Initializing workers...")
    for _ in range(2):  # Workers for print queue
        t = threading.Thread(target=worker, args=(print_queue, process_queue_item), daemon=True)
        t.start()
        threads.append(t)

    for _ in range(2):  # Workers for e-ticket queue
        t = threading.Thread(target=worker, args=(print_queue_eticket, process_queue_item_eticket), daemon=True)
        t.start()
        threads.append(t)

def enqueue_print_job(pdf_file, key):
    print_queue.put((pdf_file, key))
    logger.info(f"Added job to print queue: {pdf_file}")

def enqueue_eticket_job(pdf_file, metadata_json):
    print_queue_eticket.put((pdf_file, metadata_json))
    logger.info(f"Added job to e-ticket queue: {pdf_file}")

def get_queue_status():
    return {
        "print_queue_size": print_queue.qsize(),
        "eticket_queue_size": print_queue_eticket.qsize(),
    }

def shutdown_workers():
    logger.info("Shutting down workers...")
    print_queue.put(None)
    print_queue_eticket.put(None)
    for thread in threads:
        thread.join(timeout=10)
    logger.info("All workers have shut down.")
