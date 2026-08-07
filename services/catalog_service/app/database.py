import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        return sqlite3.connect(
            os.getenv("database")
        )
    except sqlite3.Error as e:
        print(f"[ERRO DB] {e}")
        return None

""" def init_db(): """
