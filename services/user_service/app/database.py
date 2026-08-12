import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_connection_user():
    try:
        return sqlite3.connect(
            os.getenv("database")
        )
    except sqlite3.Error as e:
        print(f"[ERRO DB] {e}")
        return None

def init_db():
    conn = get_connection_user()
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    sobrenome TEXT NOT NULL,
    telefone TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    data_nasc NOT NULL DATE,
    cpf TEXT NOT NULL UNIQUE,
    is_admin INTEGER NOT NULL DEFAULT 0,
    resete_code TEXT,
    reset_code_expira TEXT,
    endereco_id FOREIGN KEY
    )
     """)
    
    conn.commit()

    conn = get_connection_user()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS endereco (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    estado TEXT NOT NULL,
    cidade TEXT NOT NULL,
    bairro TEXT NOT NULL,
    rua TEXT NOT NULL,
    numero TEXT NOT NULL,
    complemento TEXT    
    )
    """)

    conn.commit()
    cursor.close()