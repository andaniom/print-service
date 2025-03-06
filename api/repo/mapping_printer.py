import sqlite3

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
