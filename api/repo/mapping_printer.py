

import sqlite3


def get_mapping_printers_from_db(db_name='local.db'):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Query to select all printers from the table
        cursor.execute('SELECT * FROM mapping_printer')

        # Fetch all rows from the executed query
        printers = cursor.fetchall()

        # Check if any printers were found
        if not printers:
            print("No printers found in the database.")
            return []

        # Print the list of printers
        print("List of Printers:")
        return printers

    except sqlite3.Error as e:
        print(f"Error retrieving printers from SQLite: {e}")
        return []

    finally:
        if connection:
            connection.close()

def get_mapping_printer_by_label(label, db_name='local.db'):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Query to select all printers from the table
        cursor.execute('SELECT * FROM mapping_printer WHERE label = ?', (label,))

        # Fetch all rows from the executed query
        printer = cursor.fetchone()

        # Check if any printers were found
        if not printer:
            print("No printer found in the database.")
            return None

        # Print the list of printer
        return printer

    except sqlite3.Error as e:
        print(f"Error retrieving printers from SQLite: {e}")
        return []

    finally:
        if connection:
            connection.close()


def save_mapping_printers_to_db(printers, db_name='local.db'):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Insert the new printers into the table
        for printer in printers:
            cursor.execute('INSERT INTO mapping_printer (label, printer_name, printer_id, vendor_id, product_id) VALUES (?, ?, ?, ?, ?)', printer)

        # Commit the changes to the database
        connection.commit()

        print("Mapping printers saved to the database successfully.")

    except sqlite3.Error as e:
        print(f"Error saving mapping printers to SQLite: {e}")

    finally:
        if connection:
            connection.close()