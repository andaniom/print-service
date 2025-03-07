import logging
import os
import subprocess
from pathlib import Path

from api.repo.mapping_printer import get_mapping_printer_by_label

def print_pdf(pdf_file: str, page_number: int, printer_label: str):
    # Validate input
    mapping = get_mapping_printer_by_label(printer_label)
    if mapping is None:
        logging.error(f"Label printer_label {printer_label} not found. Skipping print job.")
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

            # command = [
            #     exec_path,
            #     '-print-to', printer_name,
            #     '-silent',
            #     '-print-settings', f'{page_number}, {orientation}',
            #     pdf_file
            # ]

            command = f'"{exec_path}" "{pdf_file}" "{printer_name}" pages={page_number} /s'

            logging.info(f"Executing command: {command}")

            try:
                result = subprocess.run(command, capture_output=True, text=True)
                logging.info(f"Print successful: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logging.error(f"Print failed: {e.stderr}")
            except PermissionError:
                logging.error("Permission error: Please check file and user permissions.")
        except Exception as e:
            raise Exception(f"An error occurred while printing: {e}")
    else:
        raise Exception("Unsupported operating system")


def get_resource_path(relative_path):
    """Get the absolute path to a bundled resource."""
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)