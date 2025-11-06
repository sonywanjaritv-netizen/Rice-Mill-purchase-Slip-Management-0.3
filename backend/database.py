import mysql.connector
from mysql.connector import pooling
import os

DB_CONFIG = {
    'host': 'localhost',
    'port': 1396,
    'user': 'root',
    'password': 'root',
    'database': 'purchase_slips_db'
}

connection_pool = None

def init_connection_pool():
    """Initialize MySQL connection pool"""
    global connection_pool
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="purchase_pool",
            pool_size=5,
            pool_reset_session=True,
            **DB_CONFIG
        )
        print("✓ MySQL connection pool created successfully")
    except mysql.connector.Error as err:
        if err.errno == 1049:
            print("Database doesn't exist. Creating database...")
            create_database()
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="purchase_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG
            )
        else:
            print(f"Error creating connection pool: {err}")
            raise

def create_database():
    """Create the database if it doesn't exist"""
    try:
        temp_config = DB_CONFIG.copy()
        database_name = temp_config.pop('database')

        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.close()
        conn.close()
        print(f"✓ Database '{database_name}' created successfully")
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        raise

def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        init_connection_pool()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_slips (
                id INT AUTO_INCREMENT PRIMARY KEY,
                company_name TEXT,
                company_address TEXT,
                document_type VARCHAR(255) DEFAULT 'Purchase Slip',
                vehicle_no VARCHAR(255),
                date VARCHAR(50) NOT NULL,
                bill_no INT NOT NULL,
                party_name TEXT,
                material_name TEXT,
                ticket_no VARCHAR(255),
                broker VARCHAR(255),
                terms_of_delivery TEXT,
                sup_inv_no VARCHAR(255),
                gst_no VARCHAR(255),
                bags DOUBLE DEFAULT 0,
                avg_bag_weight DOUBLE DEFAULT 0,
                net_weight DOUBLE DEFAULT 0,
                rate DOUBLE DEFAULT 0,
                amount DOUBLE DEFAULT 0,
                bank_commission DOUBLE DEFAULT 0,
                batav_percent DOUBLE DEFAULT 1,
                batav DOUBLE DEFAULT 0,
                shortage_percent DOUBLE DEFAULT 1,
                shortage DOUBLE DEFAULT 0,
                dalali_rate DOUBLE DEFAULT 10,
                dalali DOUBLE DEFAULT 0,
                hammali_rate DOUBLE DEFAULT 10,
                hammali DOUBLE DEFAULT 0,
                freight DOUBLE DEFAULT 0,
                rate_diff DOUBLE DEFAULT 0,
                quality_diff DOUBLE DEFAULT 0,
                moisture_ded DOUBLE DEFAULT 0,
                tds DOUBLE DEFAULT 0,
                total_deduction DOUBLE DEFAULT 0,
                payable_amount DOUBLE DEFAULT 0,
                payment_method VARCHAR(255),
                payment_date VARCHAR(50),
                payment_amount DOUBLE DEFAULT 0,
                prepared_by VARCHAR(255),
                authorised_sign VARCHAR(255),
                paddy_unloading_godown TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("✓ Database tables initialized successfully")

    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
        raise

def get_db_connection():
    """Get a database connection from the pool"""
    global connection_pool
    if connection_pool is None:
        init_connection_pool()
    return connection_pool.get_connection()

def get_next_bill_no():
    """Get the next bill number"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT MAX(bill_no) as max_bill FROM purchase_slips')
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result['max_bill'] is None:
        return 1
    return result['max_bill'] + 1
