import os
import queue
import threading
import usb.core
import usb.util
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from escpos.printer import Usb
from pdf2image import convert_from_path

from api.repo.mapping_printer import get_mapping_printer_by_label, get_mapping_printers_from_db, \
    save_mapping_printers_to_db
from api.repo.printer import get_printers_from_db

app = FastAPI()

print_queue = queue.Queue()

selected_printer = None

def list_usb_printers():
    devices = usb.core.find(find_all=True)
    printers = []
    for device in devices:
        try:
            vendor_id = device.idVendor
            product_id = device.idProduct
            manufacturer = usb.util.get_string(device, device.iManufacturer)
            product = usb.util.get_string(device, device.iProduct)
            printers.append({
                "vendor_id": vendor_id,
                "product_id": product_id,
                "manufacturer": manufacturer,
                "product": product,
            })
        except usb.core.USBError as e:
            print(f"Error accessing device: {e}")
    return printers

def initialize_printer(vendor_id, product_id):
    try:
        printer = Usb(vendor_id, product_id)
        print("Printer initialized successfully.")
        return printer
    except Exception as e:
        print(f"Failed to initialize printer: {e}")
        return None

def process_queue():
    global selected_printer
    while True:
        pdf_file, printer_label = print_queue.get()
        if pdf_file is None:
            break
        if printer_label:
            print_pdf(pdf_file, printer_label)
        else:
            print("No printer selected. Skipping print job.")
        print_queue.task_done()

def print_pdf(pdf_file, label):
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_file, fmt="jpeg")
        mapping = get_mapping_printer_by_label(label)
        printer = Usb(mapping[3], mapping[4])

        # Print each image
        for image in images:
            printer.image(image)
            printer.text("\n")

        # Cut the paper (if supported by the printer)
        printer.cut()

        print(f"Printed: {pdf_file}")
    except Exception as e:
        print(f"Failed to print {pdf_file}: {e}")
    finally:
        # Clean up the file after printing
        os.remove(pdf_file)

threading.Thread(target=process_queue, daemon=True).start()

@app.get("/mapping-printer")
def get_mapping_printers():
    printers = get_mapping_printers_from_db()
    return JSONResponse(content={"printers": printers})

@app.post("/mapping-printer")
def save_mapping_printers(printers = []):
    printers = [
        ("Printer 1", "Printer 1", "USB Printer 1", "0x1a86", "0x5523"),
        ("Printer 2", "Printer 2", "USB Printer 2", "0x1a86", "0x5523"),
    ]
    save_mapping_printers_to_db(printers)
    return JSONResponse(content={"message": "Printers saved successfully"})

@app.get("/printer-device")
def get_printer_device():
    printers = list_usb_printers()
    return JSONResponse(content={"printers": printers})

@app.get("/printers")
def get_printers():
    printers = get_printers_from_db()
    return JSONResponse(content={"printers": printers})

# API endpoint to select a printer
@app.post("/select-printer")
def select_printer(vendor_id: int, product_id: int):
    global selected_printer
    selected_printer = initialize_printer(vendor_id, product_id)
    if selected_printer:
        return JSONResponse(content={"message": "Printer selected successfully"})
    else:
        raise HTTPException(status_code=400, detail="Failed to select printer")

# API endpoint to add a PDF to the print queue
@app.post("/print")
async def add_to_queue(file: UploadFile = File(...), printer_label: str = None):
    if not printer_label:
        raise HTTPException(status_code=400, detail="No printer label")

    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Save the file temporarily
    temp_dir = os.path.join("/tmp", "print-service")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    temp_file = os.path.join(temp_dir, file.filename)
    with open(temp_file, "wb") as f:
        f.write(await file.read())

    print_queue.put((temp_file, printer_label))
    return JSONResponse(content={"message": "PDF added to print queue"})

# API endpoint to get the current print queue status
@app.get("/queue")
def get_queue():
    queue_list = list(print_queue.queue)
    return JSONResponse(content={"queue": queue_list})

@app.get("/")
def index():
    return {"message": "Print Queue API"}

# Shutdown handler to stop the queue processing thread
@app.on_event("shutdown")
def shutdown():
    print_queue.put(None)

# Run the application
if __name__ == "__main__":
    import uvicorn
    import multiprocessing
    multiprocessing.freeze_support()  # For Windows support
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False, workers=1)