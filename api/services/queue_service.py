import queue
import threading

from api.logger import logger
from api.services.printer_service import print_pdf
print_queue = queue.Queue()

def process_queue():
    while True:
        pdf_file, key, metadata_json = print_queue.get()
        if pdf_file is None:
            break
        if key:
            try:
                printer_label = key
                print_pdf(pdf_file, 1, printer_label)
            except Exception as e:
                logger.error(f"Failed to print {pdf_file}: {e}")
        elif metadata_json:
            try:
                data = metadata_json['data']
                for item in data:
                    printer_label = item['printer']
                    print_pdf(pdf_file, item['page'], printer_label)
            except Exception as e:
                logger.error(f"Failed to print {pdf_file}: {e}")
        else:
            logger.error("key empty. Skipping print job.")
        print_queue.task_done()


threading.Thread(target=process_queue, daemon=True).start()
