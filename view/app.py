import subprocess

import threading

import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from PIL import Image
import pystray
import sqlite3


class SystemTrayApp:

    def __init__(self, root):
        self.root = root
        self.root.title("System Print")
        self.root.geometry('500x250')
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.base_url = "http://localhost:8002"

        self.create_widgets()

    def create_widgets(self):
        # Input port and hostname
        self.service_frame = tk.LabelFrame(self.root, text="Service Setting", padx=10, pady=10)
        self.service_frame.pack(fill=tk.X, padx=10, pady=5)

        self.input_frame = tk.Frame(self.service_frame)
        self.input_frame.pack(fill=tk.X)
        self.hostname_label = tk.Label(self.input_frame, text="Hostname    ")
        self.hostname_label.pack(side=tk.LEFT)
        self.hostname_entry = tk.Entry(self.input_frame, width=20)
        self.hostname_entry.insert(0, "localhost")
        self.hostname_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.port_frame = tk.Frame(self.service_frame)
        self.port_frame.pack(fill=tk.X)
        self.port_label = tk.Label(self.port_frame, text="Port              ")
        self.port_label.pack(side=tk.LEFT)
        self.port_entry = tk.Entry(self.port_frame, width=20)
        self.port_entry.insert(0, "2212")
        self.port_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Add Start Service
        self.add_pdf_button = tk.Button(self.service_frame, text="Start Service", command=self.start_backend)
        self.add_pdf_button.pack(pady=10)
        # Printer selection
        self.printer_frame = tk.LabelFrame(self.root, text="Select Printer", padx=10, pady=10)
        self.printer_frame.pack(fill=tk.X, padx=10, pady=5)

        self.printer_listbox = tk.Listbox(self.printer_frame, height=5)
        self.printer_listbox.pack(fill=tk.X)

        self.refresh_printers_button = tk.Button(self.printer_frame, text="Refresh Printers",
                                                 command=self.list_mapping_printers)
        self.refresh_printers_button.pack(pady=5)

        self.select_printer_button = tk.Button(self.printer_frame, text="List Printer", command=self.select_printer)
        self.select_printer_button.pack(pady=5)

        # Print queue
        self.queue_frame = tk.LabelFrame(self.root, text="Print Queue", padx=10, pady=10)
        self.queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.queue_listbox = tk.Listbox(self.queue_frame)
        self.queue_listbox.pack(fill=tk.BOTH, expand=True)

        self.refresh_queue_button = tk.Button(self.queue_frame, text="Refresh Queue", command=self.refresh_queue)
        self.refresh_queue_button.pack(pady=5)

        # Combobox to select printer
        # self.printer_combobox = tk.Combobox(self.root, values=[])
        # self.printer_combobox.pack(pady=10)
        # self.printer_combobox.bind("<<ComboboxSelected>>", self.update_label_from_combobox)

        # Add PDF to queue
        self.add_pdf_button = tk.Button(self.root, text="Add PDF to Queue", command=self.add_to_queue)
        self.add_pdf_button.pack(pady=10)

    def list_printers(self):
        response = requests.get(f"{self.base_url}/printers")
        if response.status_code == 200:
            printers = response.json()["printers"]
            self.printer_listbox.delete(0, tk.END)
            for printer in printers:
                self.printer_listbox.insert(tk.END,
                                            f"{printer['manufacturer']} {printer['product']} (Vendor ID: {printer['vendor_id']}, Product ID: {printer['product_id']})")
        else:
            messagebox.showerror("Error", "Failed to fetch printers")

    def list_mapping_printers(self):
        response = requests.get(f"{self.base_url}/mapping-printer")
        if response.status_code == 200:
            printers = response.json()["printers"]
            self.printer_listbox.delete(0, tk.END)
            for printer in printers:
                printer_name = printer[0]
                self.printer_listbox.insert(tk.END, printer_name)
                self.printer_combobox['values'] = self.printer_combobox['values'] + (printer_name,)
        else:
            messagebox.showerror("Error", "Failed to fetch printers")

    def select_printer(self):
        selected = self.printer_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No printer selected")
            return
        selected_printer = self.printer_listbox.get(selected)
        vendor_id = int(selected_printer.split("Vendor ID: ")[1].split(",")[0])
        product_id = int(selected_printer.split("Product ID: ")[1].split(")")[0])
        response = requests.post(f"{self.base_url}/select-printer",
                                 json={"vendor_id": vendor_id, "product_id": product_id})
        if response.status_code == 200:
            messagebox.showinfo("Success", "Printer selected successfully")
        else:
            messagebox.showerror("Error", "Failed to select printer")

    def update_label_from_combobox(self, event):
        # Get the selected printer from the Combobox
        selected_printer = self.printer_combobox.get()
        # self.selected_printer_label.config(text=f"Selected Printer: {selected_printer}")
        # Optionally, you can also select the corresponding item in the Listbox
        index = self.printer_combobox.current()
        if index >= 0:
            self.printer_listbox.select_set(index)

    def add_to_queue(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        with open(file_path, "rb") as file:
            response = requests.post(f"{self.base_url}/print", files={"file": file})
        if response.status_code == 200:
            messagebox.showinfo("Success", "PDF added to print queue")
        else:
            messagebox.showerror("Error", "Failed to add PDF to queue")

    def refresh_queue(self):
        response = requests.get(f"{self.base_url}/queue")
        if response.status_code == 200:
            queue_list = response.json()["queue"]
            self.queue_listbox.delete(0, tk.END)
            for item in queue_list:
                self.queue_listbox.insert(tk.END, item)
        else:
            messagebox.showerror("Error", "Failed to fetch print queue")

    def minimize_to_tray(self):
        """Minimize the window to the system tray."""
        self.root.withdraw()
        image = Image.open("app.ico")
        menu = (pystray.MenuItem('Quit', self.quit_window),
                pystray.MenuItem('Show', self.show_window))
        icon = pystray.Icon("name", image, "System Tray App", menu)
        icon.run()

    def quit_window(self, icon):
        """Stop the system tray icon and destroy the window."""
        icon.stop()
        self.root.destroy()

    def show_window(self, icon):
        """Stop the system tray icon and show the window."""
        icon.stop()
        self.root.after(0, self.root.deiconify)

    def start_backend(self, host = "0.0.0.0", port = "2212"):
        """
        Starts the backend server.

        Args:
            host (str): The host to bind to. Defaults to "0.0.0.0".
            port (str): The port to bind to. Defaults to "2212".
        """
        backend_thread = threading.Thread(target=subprocess.run(["uvicorn", "api.app:app", "--host", host, "--port", port]), daemon=True)
        backend_thread.start()


def start_frontend():
    root = tk.Tk()
    SystemTrayApp(root)
    root.mainloop()

if __name__ == "__main__":
    start_frontend()