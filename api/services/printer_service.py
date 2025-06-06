import logging
import os
import subprocess
from pathlib import Path

from api.repo.mapping_printer import get_mapping_printer_by_label


def print_pdf_file(file: str, page_number: int, printer_label: str):
    # Get printer mapping by label
    mapping = get_mapping_printer_by_label(printer_label)
    if mapping is None:
        logging.error(f"Printer label '{printer_label}' not found. Skipping print job.")
        return
    printer_name = mapping[1]

    # Validate file
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"The file '{file}' does not exist.")

    print(path)
    # Validate page number
    if not isinstance(page_number, int) or page_number < 1:
        raise ValueError("Page number must be a positive integer.")

    # Linux/Mac printing
    if os.name == 'posix':
        try:
            command = [
                "lp",
                "-o", f"page-ranges={page_number}",
                "-d", printer_name,
                str(path)
            ]
            print(command)
            logging.debug(f"Executing command: {' '.join(command)}")
            subprocess.run(command, check=True)
        except subprocess.SubprocessError as e:
            raise Exception(f"An error occurred while printing on Linux/Mac: {e}")

    elif os.name == 'nt':
        try:
            logging.info("Using Windows printing method.")
            # exec_path = get_resource_path("print.exe")  # Path to printer executable
            # logging.debug(f"Executable path: {exec_path}")
            #
            # # command: print specific pages to the printer
            # command = f'"{exec_path}" "{file}" "{printer_name}" pages={page_number} /s'

            gs_print_path = get_resource_path("GSPRINT\\gsprint.exe")
            gs_path = get_resource_path("GHOSTSCRIPT\\gswin32c.exe")
            logging.debug(f"Executable path: {gs_print_path} {gs_path}")

            page_range_options = f"-from {page_number} -to {page_number}"

            # Construct the command to print the
            command = f'"{gs_print_path}" -ghostscript "{gs_path}" -printer "{printer_name}" {page_range_options} -quiet "{str(path)}"'

            print(command)
            logging.info(f"Executing command: {command}")

            result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                logging.info(f"Print successful: {result.stdout}")
            elif result.returncode == 1:
                logging.error(f"Print failed: {result.stderr}")
            elif result.returncode == 2:
                logging.error(f"Print failed: Print.exe is already running. Waiting for it to finish.")
                while result.returncode == 2:
                    result = subprocess.run(command, capture_output=True, text=True)
        except PermissionError:
            logging.error("Permission error: Check file and user permissions.")
        except subprocess.SubprocessError as e:
            raise Exception(f"An error occurred while printing on Windows: {e}")
        except Exception as e:
            raise Exception(f"An error occurred while printing on Windows: {e}")

    else:
        raise Exception("Unsupported operating system")


def print_zpl_file(file: str, printer_label: str):
    # Get printer mapping by label
    mapping = get_mapping_printer_by_label(printer_label)
    if mapping is None:
        logging.error(f"Printer label '{printer_label}' not found. Skipping print job.")
        return
    printer_name = mapping[1]

    # Validate file
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(f"The file '{file}' does not exist.")

    if "//" not in printer_name:
        printer_name = f"//localhost/{printer_name}"

    try:
        command = f'copy "{str(path)} "{printer_name}"'
        subprocess.run(command, check=True)
    except subprocess.SubprocessError as e:
        raise Exception(f"An error occurred while printing on Linux/Mac: {e}")


def get_resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a bundled resource.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: Absolute path to the resource.
    """
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
