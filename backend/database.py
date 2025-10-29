import sqlite3
import os

DATABASE_PATH = 'purchase_slips.db'

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchase_slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            company_address TEXT,
            document_type TEXT DEFAULT 'Purchase Slip',
            vehicle_no TEXT,
            date TEXT NOT NULL,
            bill_no INTEGER NOT NULL,
            party_name TEXT,
            material_name TEXT,
            ticket_no TEXT,
            broker TEXT,
            terms_of_delivery TEXT,
            sup_inv_no TEXT,
            gst_no TEXT,
            bags REAL DEFAULT 0,
            avg_bag_weight REAL DEFAULT 0,
            net_weight REAL DEFAULT 0,
            rate REAL DEFAULT 0,
            amount REAL DEFAULT 0,
            bank_commission REAL DEFAULT 0,
            batav_percent REAL DEFAULT 1,
            batav REAL DEFAULT 0,
            shortage_percent REAL DEFAULT 1,
            shortage REAL DEFAULT 0,
            dalali_rate REAL DEFAULT 10,
            dalali REAL DEFAULT 0,
            hammali_rate REAL DEFAULT 10,
            hammali REAL DEFAULT 0,
            total_deduction REAL DEFAULT 0,
            payable_amount REAL DEFAULT 0,
            payment_method TEXT,
            payment_date TEXT,
            payment_amount REAL DEFAULT 0,
            prepared_by TEXT,
            authorised_sign TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_next_bill_no():
    """Get the next bill number"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(bill_no) as max_bill FROM purchase_slips')
    result = cursor.fetchone()
    conn.close()

    if result['max_bill'] is None:
        return 1
    return result['max_bill'] + 1
