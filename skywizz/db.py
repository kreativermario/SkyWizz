import sqlite3
import json
import os

def initialize_database(logger):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('skywizz.db')
        cursor = conn.cursor()

        # Get absolute path to the config directory
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config'))

        # Load data from JSON file
        with open(os.path.join(config_dir, 'db.json'), 'r') as file:
            data = json.load(file)

        # Create tables if they don't exist
        for table_name, schema in data['schemas'].items():
            columns = ', '.join([f'{name} {datatype}' for name, datatype in schema.items()])
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({columns})')

        # Insert banks into the banks table
        for bank in data['banks']:
            try:
                cursor.execute('INSERT INTO banks (name, description, account_type, monthly_account_cost, annual_account_cost, country, country_code) VALUES (?, ?, ?, ?, ?, ?, ?)',
                               (bank['name'], bank['description'], bank['account_type'], bank['monthly_account_cost'], bank['annual_account_cost'], bank['country'], bank['country_code']))
            except sqlite3.IntegrityError:
                logger.warning(f"Bank '{bank['name']}' already exists in the database. Skipping insertion.")

        # Commit changes
        conn.commit()
        logger.info("SQLite database initialized successfully")
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return None

def deposit(conn, user_id, bank_id, amount):
    cursor = conn.cursor()
    # Check if the user exists
    cursor.execute('SELECT * FROM bank_accounts WHERE user_id = ? AND bank_id = ?', (user_id, bank_id))
    bank_account = cursor.fetchone()
    if bank_account is None:
        # Error
        return False

    # Update cash balance
    cursor.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))

    # Update bank account balance
    cursor.execute('UPDATE bank_accounts SET balance = balance + ? WHERE user_id = ? AND bank_id = ?', (amount, user_id, bank_id))
  
    # Commit changes
    conn.commit()
    return True

def withdraw(conn, user_id, bank_id, amount):
    cursor = conn.cursor()
    # Check if bank account exists and user has enough balance
    cursor.execute('SELECT balance FROM bank_accounts WHERE user_id = ? AND bank_id = ?', (user_id, bank_id))
    result = cursor.fetchone()
    if result is None or result[0] < amount:
        raise ValueError("Not enough balance or bank account does not exist")

    # Update bank account balance
    cursor.execute('UPDATE bank_accounts SET balance = balance - ? WHERE user_id = ? AND bank_id = ?', (amount, user_id, bank_id))
    
    # Update cash balance
    cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
    
    # Commit changes
    conn.commit()
    return True

def get_banks(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, description, account_type, monthly_account_cost, annual_account_cost, country FROM banks')
    return cursor.fetchall()

def get_bank_id_by_name(conn, bank_name):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM banks WHERE name=?", (bank_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def bank_account_exists(conn, user_id, bank_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bank_accounts WHERE user_id=? AND bank_id=?", (user_id, bank_id))
    return cursor.fetchone() is not None

def get_bank_balance(conn, user_id, bank_id):
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM bank_accounts WHERE user_id=? AND bank_id=?", (user_id, bank_id))
    result = cursor.fetchone()
    return result[0] if result else None

def create_bank_account(conn, user_id, bank_id, account_type):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bank_accounts (user_id, bank_id, account_type) VALUES (?, ?, ?)", (user_id, bank_id, account_type))
    conn.commit()

def update_bank_balance(conn, user_id, bank_name, new_balance):
    cursor = conn.cursor()
    cursor.execute("UPDATE bank_accounts SET balance=? WHERE user_id=? AND bank_name=?", (new_balance, user_id, bank_name))
    conn.commit()
    
def get_cash_balance(conn, user_id):
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_bank_accounts(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.name as bank_name, ba.balance, ba.account_type
        FROM bank_accounts ba
        JOIN banks b ON ba.bank_id = b.id
        WHERE ba.user_id=?
    """, (user_id,))
    bank_accounts = {}
    for row in cursor.fetchall():
        bank_name, balance, account_type = row
        bank_accounts[bank_name] = {'balance': balance, 'account_type': account_type}
    return bank_accounts



