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

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha TEXT NOT NULL,
    data_nasc TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    is_admin INTEGER NOT NULL DEFAULT 0
    )
     """)
    
    conn.commit()

    conn = get_connection()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_id NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expira_em TEXT NOT NULL,
    expirado_em TEXT NOT NULL,
                   
    FOREIGN KEY (conta_id)
        REFERENCES contas(id)
        ON DELETE CASCADE
    )
    """)

    conn.commit()
    cursor.close()