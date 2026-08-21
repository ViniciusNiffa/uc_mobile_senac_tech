from .validator import hash_password
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = sqlite3.connect(os.getenv("database"))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as error:
        print(f"[ERRO DB] {error}")
        return None

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS contas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    ativo INTEGER NOT NULL DEFAULT 1,
    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
     """)
    
    conn.commit()

    cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_id INTEGER NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expira_em TEXT NOT NULL,
    expirado_em TEXT,
                   
    FOREIGN KEY (conta_id)
        REFERENCES contas(id)
        ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conta_id INTEGER NOT NULL,
        codigo_hash TEXT NOT NULL,
        expira_em TEXT NOT NULL,
        usado INTEGER NOT NULL DEFAULT 0,
        tentativas INTEGER NOT NULL DEFAULT 0,
        criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (conta_id)
            REFERENCES contas(id)
            ON DELETE CASCADE
    )
""")

    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if admin_email and admin_password:
        cursor.execute("""
            SELECT id
            FROM contas
            WHERE email = ?
        """, (admin_email,))

        admin = cursor.fetchone()

        if admin is None:
            cursor.execute("""
                INSERT INTO contas (
                    email,
                    senha_hash,
                    is_admin,
                    ativo
                )
                VALUES (?, ?, 1, 1)
            """, (
                admin_email,
                hash_password(admin_password)
            ))
        else:
            cursor.execute("""
                UPDATE contas
                SET is_admin = 1,
                    ativo = 1
                WHERE email = ?
            """, (admin_email,))

    conn.commit()
    cursor.close()
    conn.close()
