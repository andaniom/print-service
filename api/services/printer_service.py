import logging
import os
import subprocess
from pathlib import Path

from api.repo.mapping_printer import get_mapping_printer_by_label


# def initialize_printer(vendor_id, product_id):
#     try:
#         printer = Usb(int(vendor_id, 16), int(product_id, 16))
#         logger.info("Printer initialized successfully.")
#         return printer
#     except Exception as e:
#         logger.error(f"Failed to initialize printer: {e}")
#         return None
#
#
# def print_pdf(pdf_file, label):
#     try:
#         images = convert_pdf_to_images(pdf_file)
#         mapping = get_mapping_printer_by_label(label)
#         printer = initialize_printer(mapping['vendor_id'], mapping['product_id'])
#
#         for image in images:
#             printer.image(image)
#             printer.text("\n")
#
#         printer.cut()
#         logger.info(f"Printed: {pdf_file}")
#     except Exception as e:
#         logger.error(f"Failed to print {pdf_file}: {e}")
#     finally:
#         os.remove(pdf_file)
#
#
# def print_image(image, label):
#     try:
#         mapping = get_mapping_printer_by_label(label)
#         printer = initialize_printer(mapping[3], mapping[4])
#
#         if printer is None:
#             raise Exception("Printer not found")
#         printer.open()
#
#         # printer.image(image)
#         # printer.text("\n")
#         printer.text("Hello, TSC TTP 244 Pro!\n")
#         printer.close()
#
#         # printer.cut()
#         logger.info(f"Printed: {label}")
#     except Exception as e:
#         logger.error(f"Failed to print {label}: {e}")
#     # finally:
#     #     os.remove(pdf_file)


def print_pdf(pdf_file: str, page_number: int, printer_label: str):
    # Validate input
    mapping = get_mapping_printer_by_label(printer_label)
    if mapping is None:
        logging.error("No printer selected. Skipping print job.")
        return
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
            logging.info("print: windows")
            exec_path = get_resource_path("print.exe")
            logging.info(f"path exe: {exec_path}")

            command = [
                exec_path,
                '-print-to', printer_name,
                '-silent',
                '-print-settings', f'{page_number}, landscape',
                pdf_file
            ]

            # Log the command being executed
            logging.debug(f"Executing command: {' '.join(command)}")

            # Run the command
            result = subprocess.run(command, capture_output=True, text=True)

            # Check for errors
            if result.returncode != 0:
                logging.error(f"Failed to print PDF: {result.stderr}")
            else:
                logging.info("PDF sent to printer successfully!")
        except Exception as e:
            raise Exception(f"An error occurred while printing: {e}")
    else:
        raise Exception("Unsupported operating system")


def get_resource_path(relative_path):
    """Get the absolute path to a bundled resource."""
    # if hasattr(sys, '_MEIPASS'):
        # Running in a PyInstaller bundle
    #     base_path = sys._MEIPASS
    # else:
    # Running in a normal Python environment
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# def print_image_to_printer(image, printer_port):
#     # Configure the serial connection
#     printer = serial.Serial(port=printer_port, baudrate=9600, timeout=1)
#
#     # Save the image temporarily
#     temp_image_path = "temp_image.bmp"
#     image.save(temp_image_path, "BMP")
#
#     # TSPL commands to print the image
#     tspl_commands = f"""
#     SIZE 50 mm, 30 mm
#     GAP 0 mm, 0 mm
#     CLS
#     BITMAP 0,0,"{temp_image_path}"
#     PRINT 1
#     """
#
#     try:
#         # Open the serial port
#         printer.open()
#         time.sleep(2)  # Wait for the printer to initialize
#
#         # Send the TSPL commands to the printer
#         printer.write(tspl_commands.encode('utf-8'))
#
#         print("Image sent to printer.")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         # Close the serial connection
#         printer.close()
#         # Remove the temporary image file
#         if os.path.exists(temp_image_path):
#             os.remove(temp_image_path)
