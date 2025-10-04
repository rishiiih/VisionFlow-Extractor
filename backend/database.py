# database.py
import sqlite3
import json

DB_NAME = "invoices.db"

def init_db():
    """Initializes the database and creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            invoice_date TEXT,
            due_date TEXT,
            total_amount REAL,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_invoice(data: dict):
    """Adds a new extracted invoice to the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices (vendor_name, invoice_date, due_date, total_amount, raw_data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get('vendor_name'),
        data.get('invoice_date'),
        data.get('due_date'),
        data.get('total_amount'),
        json.dumps(data) # Store the full JSON for reference
    ))
    conn.commit()
    conn.close()

def get_all_invoices():
    """Retrieves all invoices from the database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    # Convert row objects to dictionaries
    return [dict(row) for row in rows]