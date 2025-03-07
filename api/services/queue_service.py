import queue
import threading

from api.logger import logger
from api.services.printer_service import print_pdf

print_queue = queue.Queue()


def process_queue_item(item):
    pdf_file, key, metadata_json = item
    if pdf_file is None:
        return

    try:
        if key:
            printer_label = key
            print_pdf(pdf_file, 1, printer_label)
        elif metadata_json:
            data = metadata_json['data']
            for item in data:
                printer_label = item['printer']
                print_pdf(pdf_file, item['page'], printer_label)
        else:
            logger.error("key empty. Skipping print job.")
    except Exception as e:
        logger.error(f"Failed to print {pdf_file}: {e}")


def process_queue():
    while True:
        item = print_queue.get()
        process_queue_item(item)
        print_queue.task_done()


threading.Thread(target=process_queue, daemon=True).start()