import sqlite3

def initialize_database(logger):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('skywizz.db')
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT,
                            discriminator TEXT
                        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS warnings (
                            id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            moderator_id INTEGER,
                            guild_id INTEGER,
                            reason TEXT,
                            timestamp TIMESTAMP
                        )''')

        # Commit changes
        conn.commit()
        logger.info("SQLite database initialized successfully")
        return conn
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        return None
