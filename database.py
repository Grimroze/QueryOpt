"""
Database integration module.
Handles connections to PostgreSQL, schema extraction, and EXPLAIN query execution.
"""

import os
import re
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Establishes a connection to the PostgreSQL database using the DATABASE_URL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is missing in .env file.")
    return psycopg2.connect(database_url)

def extract_table_names(query: str) -> list:
    """Extracts table names from a SQL query using regex."""
    from_tables = re.findall(r'\bFROM\s+(\w+)', query, re.IGNORECASE)
    join_tables = re.findall(r'\bJOIN\s+(\w+)', query, re.IGNORECASE)
    return list(set(from_tables + join_tables))

def fetch_table_schema(table_name: str) -> str:
    """Fetches the schema definition for a given table from the database."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        columns = cursor.fetchall()
        
        if not columns:
            return f"Schema for table '{table_name}' not found."
        
        schema_text = f"Table: {table_name}\n"
        for col_name, data_type, nullable in columns:
            null_info = "NULL" if nullable == "YES" else "NOT NULL"
            schema_text += f"  {col_name}: {data_type} ({null_info})\n"
        return schema_text
    finally:
        cursor.close()
        connection.close()

def run_explain_analyze(query: str) -> str:
    """Runs EXPLAIN on the given query to retrieve the execution plan."""
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(f"EXPLAIN {query}")
        plan_rows = cursor.fetchall()
        return "\n".join([row[0] for row in plan_rows])
    except Exception as e:
        return f"Failed to retrieve execution plan: {str(e)}"
    finally:
        cursor.close()
        connection.close()
