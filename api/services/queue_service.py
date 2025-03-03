import queue
import threading

from api.logger import logger
from api.services.printer_service import print_pdf

print_queue = queue.Queue()

def process_queue():
    while True:
        pdf_file, metadata_json = print_queue.get()
        if pdf_file is None:
            break
        if metadata_json:
            try :
                # images = convert_pdf_to_images(pdf_file)
                data = metadata_json['data']
                for item in data:
                    printer_label = item['printer']
                    # print_image(images[item['page'] - 1], printer_label)
                    print_pdf(pdf_file, item['page'], printer_label)
            except Exception as e:
                logger.error(f"Failed to print {pdf_file}: {e}")
            # finally:
            #     os.remove(pdf_file)
        else:
            logger.warning("No printer selected. Skipping print job.")
        print_queue.task_done()

threading.Thread(target=process_queue, daemon=True).start()
