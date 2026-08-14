from pathlib import Path
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("USER_DB_PATH", str(BASE_DIR / "data" / "users.db"))


def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:        
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS perfis (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL,
        sobrenome TEXT NOT NULL,
        telefone TEXT NOT NULL UNIQUE,
        data_nasc TEXT NOT NULL,
        foto_perfil TEXT,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()

        
        cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS enderecos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        perfil_id INTEGER NOT NULL,
        cep TEXT NOT NULL,
        estado TEXT NOT NULL,
        cidade TEXT NOT NULL,
        bairro TEXT NOT NULL,
        rua TEXT NOT NULL,
        numero TEXT NOT NULL,
        complemento TEXT,

        FOREIGN KEY (perfil_id)
            REFERENCES perfis(id)
            ON DELETE CASCADE
        )
        """)

        conn.commit()
    finally:
        cursor.close()
        conn.close()