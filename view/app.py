import sqlite3
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import pystray
from PIL import Image


class SystemTrayApp:

    def __init__(self, root):
        self.service_button = None
        self.db_path = "local.db"
        self.list_device = self.fetch_data_from_db()
        self.port_label = None
        self.service_frame = None
        self.hostname_entry = None
        self.hostname_label = None
        self.root = root
        self.root.configure(bg="#FFFFFF")
        self.root.title("System Print")
        self.root.geometry('1000x650')
        self.root.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.service_status = False
        self.backend_process = None

        self.create_widgets()
        self.refresh_list()
        self.refresh_status()

    def create_widgets(self):
        # Input port and hostname
        self.service_frame = tk.LabelFrame(self.root, text="Service Setting", padx=10, pady=10)
        self.service_frame.pack(fill=tk.X, padx=10, pady=5)

        self.hostname_label = tk.Label(self.service_frame, text="Hostname    ")
        self.hostname_label.grid(row=0, column=0, sticky=tk.W)
        self.hostname_entry = tk.Entry(self.service_frame, width=20)
        self.hostname_entry.insert(0, "localhost")
        self.hostname_entry.grid(row=0, column=1, sticky=tk.E)

        self.port_label = tk.Label(self.service_frame, text="Port              ")
        self.port_label.grid(row=1, column=0, sticky=tk.W)
        self.port_entry = tk.Entry(self.service_frame, width=20)
        self.port_entry.insert(0, "2212")
        self.port_entry.grid(row=1, column=1, sticky=tk.E)

        # Add Start Service
        self.service_button = tk.Button(self.service_frame, text="Start Service", command=self.toggle_service)
        self.service_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.printer_frame = tk.LabelFrame(self.root, text="List Printer", padx=10, pady=10)
        self.printer_frame.pack(fill=tk.X, padx=10, pady=5)
        self.create_editable_table()
        self.create_add_printer_form()

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
        self.tree = ttk.Treeview(self.printer_frame, columns=("Printer Name", "Printer Label"), show="headings")
        self.tree.heading("Printer Name", text="Printer Name")
        self.tree.heading("Printer Label", text="Printer Label")
        self.tree.pack(fill=tk.X, padx=10, pady=5)

        # Insert data into the Treeview
        self.update_treeview()

    def update_treeview(self):
        """Update the Treeview with the latest data from the database."""
        # Clear the current Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert the latest data
        for device in self.list_device:
            self.tree.insert("", "end", values=(device["name"], device["label"]))

        self.tree.bind("<Double-1>", self.on_double_click)

    def create_add_printer_form(self):
        """Create a form to add a new printer."""
        add_frame = tk.LabelFrame(self.root, text="Add New Printer", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        # Name Field
        tk.Label(add_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(add_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        # Label Field
        tk.Label(add_frame, text="Label:").grid(row=2, column=0, padx=5, pady=5)
        self.label_entry = tk.Entry(add_frame)
        self.label_entry.grid(row=2, column=1, padx=5, pady=5)

        # Add Button
        add_button = tk.Button(add_frame, text="Add Printer", command=self.add_printer)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

    def add_printer(self):
        """Add a new printer to the database and update the Treeview."""
        name = self.name_entry.get().strip()
        label = self.label_entry.get().strip()

        # Check if the Name, or Label already exists
        if self.is_name_exists(name):
            messagebox.showwarning("Duplicate Name", "A printer with this Name already exists.")
            return
        if self.is_label_exists(label):
            messagebox.showwarning("Duplicate Label", "A printer with this Label already exists.")
            return

        # Insert into the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO mapping_printer (name, label) VALUES (?, ?)", (name, label))
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
        self.name_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)

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
        region_clicked = self.tree.identify_region(event.x, event.y)
        if region_clicked not in ("tree", "cell"):
            return

        column = self.tree.identify_column(event.x)
        row_id = self.tree.identify_row(event.y)

        # Get the column position
        column_index = int(column[1]) - 1

        # Get the current value of the cell
        current_value = self.tree.item(row_id, "values")[column_index]

        # Create an entry widget for editing
        entry_edit = ttk.Entry(self.tree, width=20)
        entry_edit.insert(0, current_value)
        entry_edit.bind("<FocusOut>", lambda e: self.save_edit(entry_edit, row_id, column_index))
        entry_edit.bind("<Return>", lambda e: self.save_edit(entry_edit, row_id, column_index))

        # Place the entry widget in the correct position
        entry_edit.place(x=event.x, y=event.y, anchor="w")

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
        menu = (pystray.MenuItem('Show', self.show_window),
                pystray.MenuItem('Quit', self.quit_window))
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

    def stop_backend(self):
        """Stop the backend server."""
        if self.backend_process:
            self.backend_process.terminate()  # Terminate the backend process
            self.backend_process = None
            self.service_status = False
            self.service_button.config(text="Start Service")
            messagebox.showinfo("Backend Stopped", "Backend server stopped.")
        else:
            messagebox.showwarning("Backend Error", "No backend process is running.")

    def toggle_service(self):
        """Start or stop the backend service."""
        if self.service_status:
            self.stop_backend()
        else:
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
                project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                self.backend_process = subprocess.Popen(
                    ["uvicorn", "api.main:app", "--host", host, "--port", port],
                    cwd=project_dir  # Set the working directory to the project directory
                )
                self.service_status = True
                self.service_button.config(text="Stop Service")
                messagebox.showinfo("Backend Started", f"Backend server started at {host}:{port}")
            except Exception as e:
                messagebox.showerror("Backend Error", f"Failed to start backend: {e}")

        backend_thread = threading.Thread(target=run_server, daemon=True)
        backend_thread.start()


def start_frontend():
    root = tk.Tk()
    SystemTrayApp(root)
    root.mainloop()


if __name__ == "__main__":
    start_frontend()
