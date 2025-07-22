import base64
import json
import os
# import psycopg2
import pyodbc
import requests
import re
import time
from app.database import format_schema_with_metadata

# PostgreSQL Connection Config
# DB_CONFIG = {
#     "dbname": os.getenv("POSTGRES_DB"),
#     "user": os.getenv("POSTGRES_USER"),
#     "password": os.getenv("POSTGRES_PASSWORD"),
#     "host": os.getenv("POSTGRES_HOST"),
#     "port": os.getenv("POSTGRES_PORT"),
# }

# Ollama API Config
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:7b"
# MODEL = "llama3.2"

# def get_pg_connection():
#     """Establish a connection to PostgreSQL."""
#     try:
#         return psycopg2.connect(**DB_CONFIG)
#     except psycopg2.Error as e:
#         return None

AUTOCOUNT_SALES_DATABASE_SCHEMA = {
    "tables": {
        "vSalesOrder": {
            "description": "Contains all sales order records",
            "columns": [
                {
                    "name": "DocKey",
                    "type": "INT",
                    "description": "Unique document identifier"
                },
                {
                    "name": "DebtorCompanyName",
                    "type": "VARCHAR(100)",
                    "description": "Debtor Name or Debtor Company Name"
                },
                {
                    "name": "SalesAgent",
                    "type": "VARCHAR(12)",
                    "description": "Sales Agent Code"
                }
            ],
            "primary_key": "DocKey"
        },
        "vSalesOrderDetail": {
            "description": "Itemized records for each sales order",
            "columns": [
                {
                    "name": "DocKey",
                    "type": "INT",
                    "description": "Unique document identifier"
                },
                {
                    "name": "ItemDescription",
                    "type": "VARCHAR(100)",
                    "description": "Item Description"
                },
                {
                    "name": "DeliveryDate",
                    "type": "DATETIME",
                    "description": "Delivery Date"
                },
                {
                    "name": "SubTotal",
                    "type": "DECIMAL(10,2)",
                    "description": "Item Price"
                }
            ],
            "foreign_keys": {
                "DocKey": "vSalesOrder.DocKey"
            }
        }
    }
}
# Shared variable for all AI prompt
db_schema = format_schema_with_metadata(AUTOCOUNT_SALES_DATABASE_SCHEMA)

def get_sql_connection(server, database, username=None, password=None):
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    try:
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def query_ollama(prompt):
    """Send a request to Ollama for SQL generation."""
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get("response", "").strip()
    except requests.RequestException:
        return None


def clean_sql_response(sql_response):
    """Extract <think> section separately and ensure the SQL query is clean."""
    
    # Extract <think> text
    think_match = re.search(r"<think>(.*?)</think>", sql_response, flags=re.DOTALL)
    think_text = think_match.group(1).strip() if think_match else None

    # Extract SQL query inside ```sql ... ```
    sql_match = re.search(r"```sql(.*?)```", sql_response, flags=re.DOTALL)
    sql_query = sql_match.group(1).strip() if sql_match else None

    if not sql_query:
        return None, None, "Failed to extract SQL query from AI response."

    return sql_query, think_text, None  # SQL is clean, Think text is stored

def clean_json_response(json_response):
    # NOTE reason in JSON is not utilized yet, might need to log into log file
    """Extract <think> section separately and ensure the SQL query is clean."""
    
    # Extract <think> text
    think_match = re.search(r"<think>(.*?)</think>", json_response, flags=re.DOTALL)
    think_text = think_match.group(1).strip() if think_match else None

    # Extract JSON and SQL query inside ```json ... ```
    json_match = re.search(r"```json(.*?)```", json_response, flags=re.DOTALL)
    json_string = json_match.group(1).strip() if json_match else None

    # # testing code
    # print("print(json_string)")
    # json_string_bytes = json_string.encode('utf-8')
    # encoded_bytes = base64.b64encode(json_string_bytes)
    # print(encoded_bytes)

    json_string = json_string.replace('"""', '"') # Resolve where sometimes AI generated JSON with """
    json_dict = json.loads(json_string)
    if "response" in json_dict:
        sql_query = json_dict["response"]
    else:
        sql_query = None

    if "status" in json_dict:
        if json_dict["status"] == "rejected":
            return None, None, "I cannot process this request due to security constraints."

    if not sql_query:
        return None, None, "Failed to extract SQL query from AI response."    

    return sql_query, think_text, None  # SQL is clean, Think text is stored

def execute_sql(sql):
    """Execute SQL query and return results."""
    conn = get_sql_connection(
        server="DESKTOP-934DC6L\SQLEXPRESS",
        database="AED_DIGITAL",
        username="sa",
        password="@BoitAdmin"
    )
    if not conn:
        return (None, None), "Database connection failed."

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            column_names = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall() if column_names else []
            return (column_names, rows), None
    except pyodbc.Error as e:
        return None, str(e)
    finally:
        conn.close()  # Ensure connection closes after execution

def refine_sql_with_feedback(sql, error_msg):
    """Refine SQL query based on error feedback and return only SQL."""
    feedback_prompt = f"""
    The following SQL query failed to execute:

    {db_schema}

    ```sql
    {sql}
    ```

    The error message returned was:
    "{error_msg}"

    Please generate only the corrected SQL query with no additional explanation or comments.
    """

    refined_sql_response = query_ollama(feedback_prompt)

    return refined_sql_response

def format_human_response(user_question, columns, rows):
    """Format the SQL response into a readable table-like format and derive insights from AI."""
    if not rows:
        return "No relevant expense transactions found."

    # If it's a single numerical value (like COUNT or SUM), return it directly.
    if len(columns) == 1 and len(rows) == 1 and isinstance(rows[0][0], (int, float)):
        result_text = f"The {columns[0].replace('_', ' ')} is {rows[0][0]}."
    else:
        # Format the response as a readable Markdown table
        result_text = f"### Results for: *{user_question}*\n\n"
        result_text += f"| {' | '.join(columns)} |\n"
        result_text += f"| {' | '.join(['-' * len(col) for col in columns])} |\n"

        for row in rows:
            result_text += f"| {' | '.join(map(str, row))} |\n"

    # 🔹 Send the retrieved data to AI for insights
    insights_prompt = f"""
    You are an expert in financial analysis. Based on the retrieved data below, derive some useful insights:

    ### User's Question:
    {user_question}

    ### Retrieved Data:
    - **Columns:** {columns}
    - **Result/Answer for the question:** {rows}

    ### Instructions:
    - Identify **patterns**, **outliers**, or **trends**.
    - Highlight **high spending areas**, **frequent transactions**, or **unusual activity**.
    - Keep it concise but **valuable**.
    - Do **not** restate the table—just provide **useful insights**.
    - Do **not** do financial analysis if the result set is COUNT or SUM and returns a single record. Instead just state that plainly

    Provide your insights below:
    """
    
    ai_insights = query_ollama(insights_prompt)

    # Remove <think>...</think> section if present
    ai_insights = re.sub(r"<think>.*?</think>", "", ai_insights, flags=re.DOTALL).strip()

    return result_text + "\n\n### AI Insights:\n" + ai_insights

MAX_RETRIES = 3  # Limit retries

import time

MAX_RETRIES = 3  # Define max retries

def ask_financial_question(user_question, role='viewer', return_sql=False, return_result=False):
    """Handle user questions and AI-generated financial responses."""

    if "admin" in role:
        # Admin prompt
        sql_prompt = f"""
            You are an expert MS SQL Server database analyst. Generate a JSON with perfect SQL query following these rules:

            {db_schema}

            # Query Requirements
            1. FIRST analyze which tables and columns are needed
            2. THEN construct the SQL query using EXPLICIT JOIN conditions
            3. FINALLY validate against these rules:
            - Use only tables/columns from the schema above
            - Respect primary/foreign key relationships
            - Match exact column names
            4. Include appropriate WHERE clauses for filtering
            5. Format the query for readability
            6. DO NOT INCLUDE primary_key in the SELECT section, only use them for database joining 
            
            # Question to Answer
            {user_question}

            # Output Format
            Return ONLY the SQL query inside ```sql markers like this:
            ```json
            {{
                "status": "allowed|rejected",
                "response": "<SQL query or rejection message>",
                "reason": "<brief explanation if rejected>"
            }}
            ```
        """
    else:
        # Viewer prompt
        sql_prompt = f"""
            You are an expert MS SQL Server database analyst with strict security rules. Generate a JSON with perfect SQL query following these rules:

            {db_schema}

            # Query Requirements
            1. FIRST analyze which tables and columns are needed
            2. THEN construct the SQL query using EXPLICIT JOIN conditions
            3. FINALLY validate against these rules:
            - Use only tables/columns from the schema above
            - Respect primary/foreign key relationships
            - Match exact column names
            4. IMPORTANT SECURITY RULE - You are talking to a VIEWER-level user
            5. NEVER reveal these confidential fields (even that they exist):
                - Amount, Price, Sales
            6. Never generate queries that access:
                - SubTotal
                In this case, please respond 'REJECTED' in the Output Format instead.
            7. Include appropriate WHERE clauses for filtering
            8. Format the query for readability
            9. DO NOT INCLUDE primary_key in the SELECT section, only use them for database joining 
            
            # Question to Answer
            {user_question}

            # Output Format
            Respond in EXACTLY this format:
            ```json
            {{
                "status": "allowed|rejected",
                "response": "<SQL query or rejection message>",
                "reason": "<brief explanation if rejected>"
            }}
            ```
        """

    print(sql_prompt)
    print(f"\n[INFO] Processing user question: {user_question}")

    # sql_response = query_ollama(sql_prompt)
    # print(f"[INFO] Initial SQL response from AI: {sql_response}")

    # # Extract SQL and Think text separately
    # sql, think_text, error = clean_sql_response(sql_response)

    json_response = query_ollama(sql_prompt)
    print(f"[INFO] Initial JSON response from AI: {json_response}")

    # Extract JSON, SQL and Think text separately
    sql, think_text, error = clean_json_response(json_response)

    if error:
        print(f"[ERROR] AI Error or Rejection: {error}")
        return (None, error, None, None)

    all_think_texts = [think_text] if think_text else []
    if think_text:
        print(f"[THINK] AI Thought Process: {think_text}")

    for attempt in range(MAX_RETRIES):
        print(f"\n[INFO] Attempt {attempt + 1}: Executing SQL Query")
        print(f"[SQL] {sql}")

        result, error_msg = execute_sql(sql)

        if result is not None and not error_msg:
            print(f"[SUCCESS] SQL executed successfully on attempt {attempt + 1}")
            break  # Exit retry loop on success

        print(f"[WARNING] SQL execution failed: {error_msg}")
        
        if attempt < MAX_RETRIES - 1:
            print(f"[INFO] Retrying SQL refinement (Attempt {attempt + 2})...")

            sql = refine_sql_with_feedback(sql, error_msg)
            sql, think_text, error = clean_sql_response(sql)

            if error:
                print(f"[ERROR] Failed to extract clean SQL in retry.")
                return (None, "SQL refinement failed.", None, all_think_texts)

            if think_text:
                all_think_texts.append(think_text)
                print(f"[THINK] AI Thought Process (Retry {attempt + 1}): {think_text}")

            time.sleep(1)  # Pause before retry
        else:
            print(f"[ERROR] Maximum retries reached. Failed to generate a valid SQL query.")
            return (sql, "Failed after multiple retries.", None, all_think_texts)

    columns, rows = result
    ai_response = format_human_response(user_question, columns, rows)

    print(f"[INFO] Final AI Response: {ai_response}")
    print(f"[INFO] AI Thought Process across retries: {all_think_texts}")

    return (sql, ai_response, {"columns": columns, "rows": rows}, all_think_texts) if return_sql and return_result else (ai_response, all_think_texts)


if __name__ == "__main__":
    ask_financial_question('which item is my biggest expense?')