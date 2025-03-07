import queue
import threading

from api.logger import logger
from api.services.printer_service import print_pdf

e_ticket_print_queue = queue.Queue()
print_queue = queue.Queue()


def process_e_ticket_queue():
    while True:
        pdf_file, metadata_json = e_ticket_print_queue.get()
        if pdf_file is None:
            break
        if metadata_json:
            try:
                data = metadata_json['data']
                for item in data:
                    printer_label = item['printer']
                    print_pdf(pdf_file, item['page'], printer_label)
            except Exception as e:
                logger.error(f"Failed to print {pdf_file}: {e}")
        else:
            logger.error("metadata_json empty. Skipping print job.")
        e_ticket_print_queue.task_done()


threading.Thread(target=process_e_ticket_queue, daemon=True).start()


def process_queue():
    while True:
        pdf_file, key = print_queue.get()
        if pdf_file is None:
            break
        if key:
            try:
                printer_label = key
                print_pdf(pdf_file, 1, printer_label)
            except Exception as e:
                logger.error(f"Failed to print {pdf_file}: {e}")
        else:
            logger.error("key empty. Skipping print job.")
        e_ticket_print_queue.task_done()


threading.Thread(target=process_queue, daemon=True).start()
