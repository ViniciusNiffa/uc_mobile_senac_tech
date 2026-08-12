import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_connection_catalog():
    try:
        return sqlite3.connect(
            os.getenv("database")
        )
    except sqlite3.Error as e:
        print(f"[ERRO DB] {e}")
        return None

def init_db():
    conn = get_connection_catalog()
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT
    nome TEXT NOT NULL,
    )

     """)