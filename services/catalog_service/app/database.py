import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            database=os.getenv("DB_NAME", "senac_tech_db"),
            charset='utf8mb4',
            use_unicode=True,
            autocommit=True
        )
        return conn
    except Error as e:
        print(f"[ERRO DB] {e}")
        return None