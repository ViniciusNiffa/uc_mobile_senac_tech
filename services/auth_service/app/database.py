import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    try:
        host=os.getenv("DB_HOST")
        user=os.getenv("DB_USER")
        password=os.getenv("DB_PASS")
        database=os.getenv("DB_NAME")

        if not all([host,user,database]):
            raise Exception("Variaveis de ambiente não configuradas")
        
        conn= mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            autocommit=True
        )
        return conn
    except Error as e:
        print(f"[ERROR DB] {e}")
        return None