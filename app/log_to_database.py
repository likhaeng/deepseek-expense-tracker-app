import pyodbc
import re

def get_sql_connection(server, database, username=None, password=None):
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection error: {e}")
        return None
    
# def log_to_db(data_list):
def log_to_db(user_query="", ai_think="", ai_response="", ai_prompt="", remarks="", ai_model="", tag="", process_time_second=0):
    conn = get_sql_connection(
        server="DESKTOP-3T1535M",
        database="MedicalAI",
        username="sa",
        password="@BoitAdmin2502"
    )
    cursor = conn.cursor()

    # construct data list
    if "deepseek" in ai_model: # Only applicable to deepseek model, where think string will be extracted, and response will exclude think string
        # Get AI think text
        think_match = re.search(r"<think>(.*?)</think>", ai_response, flags=re.DOTALL)
        ai_think = think_match.group(1).strip() if think_match else None
        # Get AI response text
        ai_response = re.sub(r"<think>.*?</think>", "", ai_response, flags=re.DOTALL).strip()
    data_list = [user_query, ai_think, ai_response, ai_prompt, remarks, ai_model, tag, process_time_second]

    # SQL Query for inserting data (ignores duplicates)
    insert_query = """
    INSERT INTO LOGGING (USER_QUERY, AI_THINK, AI_RESPONSE, AI_PROMPT, REMARKS, AI_MODEL, TAG, PROCESS_TIME_SECOND) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    # Convert DataFrame to a list of tuples
    # records = df[['USER_QUERY', 'AI_THINK', 'AI_RESPONSE', 'AI_PROMPT', 'REMARKS', 'AI_MODEL', 'TAG']].values.tolist()

    # Execute batch insert
    cursor.executemany(insert_query, [data_list])
    conn.commit()

    cursor.close()
    conn.close()