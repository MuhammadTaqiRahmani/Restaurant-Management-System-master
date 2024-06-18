import os
from dotenv import load_dotenv
import pyodbc
load_dotenv()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
driver = 'ODBC Driver 17 for SQL Server'
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)
cnxn = pyodbc.connect(conn_str)
print("Connected successfully")