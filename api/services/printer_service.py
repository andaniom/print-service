import logging

from pathlib import Path

import subprocess

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
        printer.open()

        # printer.image(image)
        # printer.text("\n")
        printer.text("Hello, TSC TTP 244 Pro!\n")
        printer.close()


        # printer.cut()
        logger.info(f"Printed: {label}")
    except Exception as e:
        logger.error(f"Failed to print {label}: {e}")
    # finally:
    #     os.remove(pdf_file)


def print_pdf(pdf_file: str, page_number: int, printer_label: str):
    # Validate input
    mapping = get_mapping_printer_by_label(printer_label)
    printer_name = mapping[1]
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        raise FileNotFoundError(f"The file {pdf_file} does not exist.")

    if not isinstance(page_number, int) or page_number < 1:
        raise ValueError("Page number must be a positive integer.")

    if os.name == 'posix':  # Linux/Mac
        try:
            # Use 'lp' command if available
            command = [
                "lp",  # Command to print
                "-o", f"page-ranges={page_number} queue={printer_name}",  # Specify the page range
                pdf_file  # Specify the PDF file to print
            ]

            # Log the command being executed
            logging.info(f"Executing command: {' '.join(command)}")

            # Run the command
            subprocess.run(command, check=True)
        except Exception as e:
            raise Exception(f"An error occurred while printing: {e}")
    elif os.name == 'nt':  # Windows
        try:
            # Execute the ShellExecute command to print the PDF
            # /d: option specifies the printer name
            # /p option specifies the page number
            # "." specifies the working directory
            # 0 specifies the showCmd parameter
            print_command = f'/d:"{printer_name}" /p {page_number}'

            # Execute the print command
            import win32api
            win32api.ShellExecute(0, "print", pdf_file, print_command, ".", 0)
        except Exception as e:
            raise Exception(f"An error occurred while printing: {e}")
    else:
        raise Exception("Unsupported operating system")
