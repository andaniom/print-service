import os

from escpos.printer import Usb

from api.logger import logger
from api.repo.mapping_printer import get_mapping_printer_by_label
from api.utils.pdf_util import convert_pdf_to_images


def initialize_printer(vendor_id, product_id):
    try:
        printer = Usb(int(vendor_id, 16), int(product_id, 16))
        logger.info("Printer initialized successfully.")
        return printer
    except Exception as e:
        logger.error(f"Failed to initialize printer: {e}")
        return None

def print_pdf(pdf_file, label):
    try:
        images = convert_pdf_to_images(pdf_file)
        mapping = get_mapping_printer_by_label(label)
        printer = initialize_printer(mapping['vendor_id'], mapping['product_id'])

        for image in images:
            printer.image(image)
            printer.text("\n")

        printer.cut()
        logger.info(f"Printed: {pdf_file}")
    except Exception as e:
        logger.error(f"Failed to print {pdf_file}: {e}")
    finally:
        os.remove(pdf_file)

def print_image(image, label):
    try:
        mapping = get_mapping_printer_by_label(label)
        printer = initialize_printer(mapping[3], mapping[4])

        if printer is None:
            raise Exception("Printer not found")

        printer.image(image)
        printer.text("\n")

        printer.cut()
        logger.info(f"Printed: {label}")
    except Exception as e:
        logger.error(f"Failed to print {label}: {e}")
    # finally:
    #     os.remove(pdf_file)
