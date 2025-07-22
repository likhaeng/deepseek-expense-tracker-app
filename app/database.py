import os
# import psycopg2
import pyodbc
import pandas as pd
from dotenv import load_dotenv

import re
from typing import Dict, List

# Load environment variables from .env
load_dotenv()

# Database credentials from .env
# DB_HOST = os.getenv("POSTGRES_HOST")
# DB_PORT = os.getenv("POSTGRES_PORT")
# DB_USER = os.getenv("POSTGRES_USER")
# DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
# DB_NAME = os.getenv("POSTGRES_DB")
# DB_HOST = creds.POSTGRES_HOST
# DB_PORT = creds.POSTGRES_PORT
# DB_USER = creds.POSTGRES_USER
# DB_PASSWORD = creds.POSTGRES_PASSWORD
# DB_NAME = creds.POSTGRES_DB

# Establish database connection
# def get_db_connection():
#     return psycopg2.connect(
#         host=DB_HOST,
#         port=DB_PORT,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         dbname=DB_NAME
#     )

def get_sql_connection(server, database, username=None, password=None):
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection error: {e}")
        return None

# Create transactions table if it doesn't exist
def create_table():
    query = """
    CREATE TABLE IF NOT EXISTS bank_transactions (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        date DATE NOT NULL,
        posting_date DATE NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('Income', 'Expense')),
        description TEXT NOT NULL,
        month_year VARCHAR(7) NOT NULL
    );
    """
    conn = get_sql_connection(
        server="DESKTOP-934DC6L\SQLEXPRESS",
        database="AED_DIGITAL",
        username="sa",
        password="@BoitAdmin"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

# NOTE: Temporary not applicable as too many not null fields to be integrated from AutoCount database PO table
# Insert transactions into the database (avoid duplicates)
def insert_transactions(df):
    conn = get_sql_connection(
        server="DESKTOP-934DC6L\SQLEXPRESS",
        database="AED_DIGITAL",
        username="sa",
        password="@BoitAdmin"
    )
    cursor = conn.cursor()

    # print(DB_NAME)

    # SQL Query for inserting data (ignores duplicates)
    insert_query = """
    INSERT INTO PO (DocNo, DocDate, CreditorName, Phone1, Attention, Total) VALUES (?, ?, ?, ?, ?, ?, ?);
    """

    # Convert DataFrame to a list of tuples
    records = df[['DocNo', 'DocDate', 'CreditorName', 'Phone1', 'Attention', 'Total']].values.tolist()

    # Execute batch insert
    cursor.executemany(insert_query, records)
    conn.commit()

    cursor.close()
    conn.close()

# Fetch transactions for a specific user
def get_transactions(name):
    conn = get_sql_connection(
        server="DESKTOP-934DC6L\SQLEXPRESS",
        database="AED_DIGITAL",
        username="sa",
        password="@BoitAdmin"
    )
    cursor = conn.cursor()

    query = "SELECT * FROM bank_transactions WHERE name = %s ORDER BY date DESC"
    cursor.execute(query, (name,))
    records = cursor.fetchall()

    # Convert results to DataFrame
    columns = [ 'name', 'date', 'posting_date', 'amount', 'transaction_type', 'description', 'month_year']
    df = pd.DataFrame(records, columns=columns)

    cursor.close()
    conn.close()
    
    return df


def format_schema_with_metadata(schema: Dict) -> str:
    """Generate detailed schema prompt with types and descriptions"""
    prompt = "# Database Schema Documentation (MUST USE THESE STRUCTURES)\n\n"
    
    for table_name, table_info in schema["tables"].items():
        # Table header
        prompt += f"## Table: {table_name}\n"
        if table_info.get("description"):
            prompt += f"*Description*: {table_info['description']}\n\n"
        
        # Columns section
        prompt += "### Columns\n"
        for col in table_info["columns"]:
            # Handle both string and dict column definitions
            if isinstance(col, str):
                col_name = col
                col_type = "unknown"
                col_desc = ""
            else:  # Assume dict format
                col_name = col["name"]
                col_type = col.get("type", "unknown")
                col_desc = col.get("description", "")
            
            # Format column line
            prompt += f"- `{col_name}`"
            prompt += f" ({col_type})" if col_type != "unknown" else ""
            prompt += f": {col_desc}" if col_desc else ""
            
            # Add key indicators
            if "primary_key" in table_info and col_name == table_info["primary_key"]:
                prompt += " 🔑"
            if "foreign_keys" in table_info and col_name in table_info["foreign_keys"]:
                prompt += f" → {table_info['foreign_keys'][col_name]}"
            prompt += "\n"
        
        # Add table relationships
        if "foreign_keys" in table_info:
            prompt += "\n### Relationships\n"
            for fk_col, ref_table in table_info["foreign_keys"].items():
                prompt += f"- Joins to `{ref_table}` via `{fk_col}`\n"
        
        prompt += "\n" + "-"*50 + "\n\n"  # Visual separator
    print(prompt)
    return prompt

# if __name__ == "__main__":
#     format_schema_with_metadata(DATABASE_SCHEMA)