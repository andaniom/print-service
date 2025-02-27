import sqlite3


def get_printers_from_db(db_name='local.db'):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Query to select all printers from the table
        cursor.execute('SELECT * FROM printer')

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


def save_printers_to_db(printers, db_name='local.db'):
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        # Insert the new printers into the table
        for printer in printers:
            cursor.execute('INSERT INTO printer (printer_name, vendor_id, product_id) VALUES (?, ?, ?, ?, ?)', printer)

        # Commit the changes to the database
        connection.commit()

        print("Mapping printers saved to the database successfully.")

    except sqlite3.Error as e:
        print(f"Error saving mapping printers to SQLite: {e}")

    finally:
        if connection:
            connection.close()

