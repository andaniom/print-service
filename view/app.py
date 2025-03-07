import multiprocessing
import os
import sqlite3
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import fasteners
import pystray
from PIL import Image

from view.config import Config


class SystemTrayApp:

    def __init__(self, root):
        self.icon = None
        self.menu = None
        self.header_frame = None
        self.printer_frame = None
        self.add_frame = None
        self.service_button = None
        self.db_path = "local.db"
        self.list_device = self.fetch_data_from_db()
        self.port_label = None
        self.port_entry = None
        self.service_frame = None
        self.hostname_entry = None
        self.hostname_label = None
        self.root = root
        self.root.configure(bg="#FFFFFF")
        self.root.title("Ecalyptus Printer Manager")
        self.root.geometry('600x650')
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.service_status = False
        self.backend_process = None
        self.update_device = False
        self.label_entry = None
        self.name_entry = None
        self.id_entry = None
        self.submit_button = None
        self.cancel_button = None

        self.create_widgets()
        self.refresh_list()
        self.refresh_status()

    def create_widgets(self):
        # Input port and hostname
        self.header_app()
        self.printer_frame = tk.LabelFrame(self.root, text="List Printer", padx=10, pady=10)
        self.printer_frame.pack(fill=tk.X, padx=10, pady=5)
        self.create_editable_table()
        self.log_frame = tk.LabelFrame(self.root, text="Log", padx=10, pady=10)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(self.log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("green", foreground="green")
        self.update_log()

    def update_log(self):
        """Update the log from the file."""
        file_path = "backend.log"
        if not os.path.exists(file_path):
            with open(file_path, "w"):
                pass
        with open(file_path, "r") as file:
            lines = file.readlines()
            self.log_text.delete("1.0", tk.END)
            for line in lines[-10:]:
                if "ERROR" in line:
                    self.log_text.insert(tk.END, line, "red")
                else:
                    self.log_text.insert(tk.END, line, "green")
        self.log_text.after(1000, self.update_log)

    def fetch_data_from_db(self):
        """Fetch data from the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS mapping_printer (id TEXT PRIMARY KEY, name TEXT UNIQUE, label TEXT UNIQUE)")
        cursor.execute("SELECT * FROM mapping_printer")
        rows = cursor.fetchall()
        conn.close()

        # Convert rows to a list of dictionaries
        return [{"id": row[0], "name": row[1], "label": row[2]} for row in rows]

    def create_editable_table(self):
        """Create an editable table using ttk.Treeview."""
        self.tree = ttk.Treeview(self.printer_frame, columns=("ID", "Name", "Label"), show="headings")
        self.tree.column("ID", width=20, anchor="center")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Label", text="Label")
        self.tree.pack(fill=tk.X, padx=5, pady=5)

        # Insert data into the Treeview
        self.update_treeview()

    def update_treeview(self):
        """Update the Treeview with the latest data from the database."""
        # Clear the current Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert the latest data
        for device in self.list_device:
            self.tree.insert("", "end", values=(device["id"], device["name"], device["label"]))

        self.tree.bind("<Button-3>", self.on_right_click)
        self.tree.bind("<Button-2>", self.on_right_click)
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_right_click(self, event):
        """Handle right click and show delete option."""
        row_id = self.tree.identify_row(event.y)
        if row_id:
            menu = tk.Menu(self.tree, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_row(row_id))
            menu.add_command(label="Delete", command=lambda: self.delete_row(row_id))
            menu.tk_popup(event.x_root, event.y_root)

    def header_app(self):
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)

        left_frame = tk.Frame(self.header_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.create_service_setting(left_frame)

        right_frame = tk.Frame(self.header_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.create_add_printer_form(right_frame)

    def create_service_setting(self, parent):
        self.service_frame = tk.LabelFrame(parent, text="Service Setting", padx=5, pady=5)
        self.service_frame.pack(fill=tk.X, padx=5, pady=5)

        self.hostname_label = tk.Label(self.service_frame, text="Hostname")
        self.hostname_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.hostname_entry = tk.Entry(self.service_frame, width=20)
        self.hostname_entry.insert(0, "localhost")
        self.hostname_entry.grid(row=0, column=1, padx=5, pady=5)

        self.port_label = tk.Label(self.service_frame, text="Port")
        self.port_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.port_entry = tk.Entry(self.service_frame, width=20)
        self.port_entry.insert(0, "2212")
        self.port_entry.grid(row=1, column=1, padx=5, pady=5)

        # Add Start Service
        self.service_button = tk.Button(self.service_frame, text="Start Service", command=self.toggle_service)
        self.service_button.grid(row=2, column=1, padx=5, pady=5)

        self.service_frame.grid_rowconfigure(3, minsize=38)

    def create_add_printer_form(self, parent):
        """Create a form to add a new printer."""
        self.add_frame = tk.LabelFrame(parent, text="New Printer", padx=5, pady=5)
        self.add_frame.pack(fill=tk.X, padx=5, pady=5)

        # ID Field
        tk.Label(self.add_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.id_entry = tk.Entry(self.add_frame)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5)

        # Name Field
        tk.Label(self.add_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = tk.Entry(self.add_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Label Field
        tk.Label(self.add_frame, text="Label:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.label_entry = tk.Entry(self.add_frame)
        self.label_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Buttons
        button_frame = tk.Frame(self.add_frame)
        button_frame.grid(row=3, column=1, columnspan=2, pady=5)

        self.cancel_button = tk.Button(button_frame, text="Cancel", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT)

        self.submit_button = tk.Button(button_frame, text="Add Printer", command=self.submit_printer)
        self.submit_button.pack(side=tk.LEFT, padx=5)

    def submit_printer(self):
        if self.update_device:
            self.update_printer()
        else:
            self.add_printer()

    def add_printer(self):
        """Add a new printer to the database and update the Treeview."""
        id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        label = self.label_entry.get().strip()

        if not id or not name or not label:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        # Check if the ID, Name, or Label already exists
        if self.is_id_exists(id):
            messagebox.showwarning("Duplicate ID", "A printer with this ID already exists.")
            return

        # Insert into the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO mapping_printer (id, name, label) VALUES (?, ?, ?)", (id, name, label))
            conn.commit()
        except sqlite3.IntegrityError as e:
            messagebox.showwarning("Database Error", str(e))
            return
        finally:
            conn.close()

        # Refresh the list and update the Treeview
        self.list_device = self.fetch_data_from_db()
        self.update_treeview()

        # Clear the form fields
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)

    def update_printer(self):
        id = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        label = self.label_entry.get().strip()

        if not id or not name or not label:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        # Update the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE mapping_printer SET id = ?, name = ?, label = ? WHERE id = ?", (id, name, label, id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            messagebox.showwarning("Database Error", str(e))
            return
        finally:
            conn.close()

        # Refresh the list and update the Treeview
        self.list_device = self.fetch_data_from_db()
        self.update_treeview()

        # Clear the form fields
        self.id_entry.config(state="normal")
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)
        self.update_device = False
        self.submit_button.config(text="Add Printer")
        self.add_frame.config(text="New Printer")

    def is_id_exists(self, id):
        """Check if the ID already exists in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM mapping_printer WHERE id = ?", (id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def is_name_exists(self, name):
        """Check if the Name already exists in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM mapping_printer WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def is_label_exists(self, label):
        """Check if the Label already exists in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT label FROM mapping_printer WHERE label = ?", (label,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def on_double_click(self, event):
        """Handle double-click events to edit cells."""
        self.edit_row(self.tree.identify_row(event.y))
        # region_clicked = self.tree.identify_region(event.x, event.y)
        # if region_clicked not in ("tree", "cell"):
        #     return
        #
        # column = self.tree.identify_column(event.x)
        # row_id = self.tree.identify_row(event.y)
        #
        # # Get the column position
        # column_index = int(column[1]) - 1
        # if column_index == 3:
        #     return
        #
        # # Get the current value of the cell
        # current_value = self.tree.item(row_id, "values")[column_index]
        #
        # # Create an entry widget for editing
        # entry_edit = ttk.Entry(self.tree, width=20)
        # entry_edit.insert(0, current_value)
        # entry_edit.bind("<FocusOut>", lambda e: self.save_edit(entry_edit, row_id, column_index))
        # entry_edit.bind("<Return>", lambda e: self.save_edit(entry_edit, row_id, column_index))
        #
        # # Place the entry widget in the correct position
        # entry_edit.place(x=event.x, y=event.y, anchor="w")

    def clear_form(self):
        self.id_entry.config(state="normal")
        self.submit_button.config(text="Add Printer")
        self.add_frame.config(text="New Printer")
        self.update_device = False
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)

    def edit_row(self, row_id):
        """Edit a row in the Treeview."""
        current_values = list(self.tree.item(row_id, "values"))
        id = current_values[0]  # ID is the first column
        name = current_values[1]
        label = current_values[2]
        self.clear_form()
        self.update_device = True
        self.id_entry.insert(0, id)
        self.name_entry.insert(0, name)
        self.label_entry.insert(0, label)
        self.id_entry.configure(state="readonly")
        self.submit_button.config(text="Update Printer")
        self.add_frame.config(text="Update Printer")

    def delete_row(self, row_id):
        """Delete a row from the Treeview and SQLite database."""
        # Get the current values of the row
        current_values = list(self.tree.item(row_id, "values"))
        id = current_values[0]  # ID is the first column

        # Delete from the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM mapping_printer WHERE id = ?", (id,))
        conn.commit()
        conn.close()

        # Delete from the Treeview
        self.tree.delete(row_id)

    def save_edit(self, entry_edit, row_id, column_index):
        """Save the edited value to the Treeview and SQLite database."""
        # Get the new value from the entry widget
        new_value = entry_edit.get()

        # Get the current values of the row
        current_values = list(self.tree.item(row_id, "values"))
        device_id = current_values[0]  # ID is the first column
        column_name = ["id", "name", "label"][column_index]  # Map column index to column name

        # Validate the new value
        if column_name == "name" and self.is_name_exists(new_value) and new_value != current_values[1]:
            messagebox.showwarning("Duplicate Name", "A printer with this Name already exists.")
            return
        if column_name == "label" and self.is_label_exists(new_value) and new_value != current_values[2]:
            messagebox.showwarning("Duplicate Label", "A printer with this Label already exists.")
            return

        # Update the Treeview with the new value
        current_values[column_index] = new_value
        self.tree.item(row_id, values=current_values)

        # Update the SQLite database
        self.update_db(device_id, column_name, new_value)

        # Destroy the entry widget
        entry_edit.destroy()

    def update_db(self, device_id, column_name, new_value):
        """Update the SQLite database with the new value."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"UPDATE mapping_printer SET {column_name} = ? WHERE id = ?", (new_value, device_id))
        conn.commit()
        conn.close()

    def refresh_list(self):
        """Refresh the list of mapping_printer every 1 minute."""
        # Fetch the latest data from the database
        self.list_device = self.fetch_data_from_db()

        # Update the Treeview
        self.update_treeview()

        # Schedule the next refresh
        self.root.after(10000, self.refresh_list)

    def refresh_status(self):
        """Refresh the status of the backend server."""
        if self.service_status:
            import requests

            try:
                host = self.hostname_entry.get().strip()
                port = self.port_entry.get().strip()
                response = requests.get(f"http://{host}:{port}")
                if response.status_code != 200:
                    self.service_status = False
                    self.service_button.config(text="Start Service")
            except requests.exceptions.RequestException:
                self.service_status = False
                self.service_button.config(text="Start Service")

        self.root.after(10000, self.refresh_status)

    def minimize_to_tray(self):
        """Minimize the window to the system tray."""
        self.root.withdraw()
        image = Image.open("app.ico")  # Ensure this file exists
        self.menu = (pystray.MenuItem('Show', self.show_window),
                pystray.MenuItem('Quit', self.quit_window))
        self.icon = pystray.Icon("name", image, "Ecalyptus Printer Manager", self.menu)
        self.icon.run()

    def quit_window(self, icon):
        """Stop the system tray icon and destroy the window."""
        icon.stop()
        self.root.destroy()

    def show_window(self, icon):
        """Stop the system tray icon and show the window."""
        icon.stop()
        self.root.after(0, self.root.deiconify)

    def stop_backend(self):
        """Stop the backend server."""
        if self.backend_process:
            self.backend_process.terminate()
            subprocess.run(['taskkill', '/im', 'api.exe', '/f'])
            self.backend_process = None
            self.service_status = False
            self.service_button.config(text="Start Service")
            messagebox.showinfo("Backend Stopped", "Backend server stopped.")

    def toggle_service(self):
        """Start or stop the backend service."""
        if self.service_status:
            self.stop_backend()
        else:
            self.stop_backend()
            self.start_backend()

    def start_backend(self):
        """Start the backend server in a separate thread."""
        host = self.hostname_entry.get().strip()
        port = self.port_entry.get().strip()

        if not host or not port:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        def run_server():
            try:
                # Set the working directory to the project directory
                import os
                if Config.DEBUG:
                    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                    self.backend_process = subprocess.Popen(
                        ["uvicorn", "api.api:app", "--host", host, "--port", port],
                        cwd=project_dir  # Set the working directory to the project directory
                    )
                else:
                    self.backend_process = subprocess.Popen(
                        ["./api.exe", "--host", host, "--port", port],  # Pass host and port
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                self.service_status = True
                self.service_button.config(text="Stop Service")
                messagebox.showinfo("Backend Started", f"Backend server started at {host}:{port}")
            except Exception as e:
                messagebox.showerror("Backend Error", f"Failed to start backend: {e}")

        backend_thread = threading.Thread(target=run_server, daemon=True)
        backend_thread.start()


def start_frontend():
    mutex_name = 'ecal_print.lock'
    lock = fasteners.InterProcessLock(mutex_name)

    if lock.acquire(blocking=False):  # Non-blocking lock
        try:
            root = tk.Tk()
            SystemTrayApp(root)
            root.mainloop()
        finally:
            lock.release()
    else:
        messagebox.showwarning("Ecalyptus Printer Manager",
                               "The application is already running.")

if __name__ == "__main__":
    start_frontend()
