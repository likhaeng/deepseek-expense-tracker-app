import pyodbc

def get_sql_connection(server, database, username=None, password=None):
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
def log_to_db(data_list):
    conn = get_sql_connection(
        server="DESKTOP-934DC6L\SQLEXPRESS",
        database="MedicalAI",
        username="sa",
        password="@BoitAdmin"
    )
    cursor = conn.cursor()

    # SQL Query for inserting data (ignores duplicates)
    insert_query = """
    INSERT INTO LOGGING (USER_QUERY, AI_THINK, AI_RESPONSE, AI_PROMPT, REMARKS, AI_MODEL, TAG) VALUES (?, ?, ?, ?, ?, ?, ?);
    """

    # Convert DataFrame to a list of tuples
    # records = df[['USER_QUERY', 'AI_THINK', 'AI_RESPONSE', 'AI_PROMPT', 'REMARKS', 'AI_MODEL', 'TAG']].values.tolist()

    # Execute batch insert
    cursor.executemany(insert_query, [data_list])
    conn.commit()

    cursor.close()
    conn.close()