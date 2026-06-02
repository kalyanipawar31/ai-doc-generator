
import sqlite3

def create_connection():
    conn = sqlite3.connect("metadata.db")
    return conn


def create_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_count INTEGER,
            functions TEXT
        )
    """)

    conn.commit()
    conn.close()
