import pandas as pd
import datetime

def clean_and_process_csv(file_path):
    
    # Load CSV, skipping the first row (metadata) but keeping actual headers
    df = pd.read_csv(file_path, skiprows=2)

    # Drop 'Item #' and 'Card #' columns explicitly
    df = df.iloc[:, 2:]  # Keep only the last four columns

    # Rename columns for clarity
    df.columns = ['date', 'posting_date', 'amount', 'description']

    # Convert date formats (YYYYMMDD → YYYY-MM-DD)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')
    df['posting_date'] = pd.to_datetime(df['posting_date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

    # Ensure amount is numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    # Add a 'transaction_type' column based on positive/negative amounts
    df['transaction_type'] = df['amount'].apply(lambda x: 'Income' if x < 0 else 'Expense')

    # Convert all amounts to positive values (since credits were negative)
    df['amount'] = df['amount'].abs()

    # **Exclude "PAYMENT RECEIVED - THANK YOU" from being considered as Income**
    df = df[~((df['description'].str.contains("PAYMENT RECEIVED - THANK YOU", case=False, na=False)) & (df['transaction_type'] == "Income"))]

    # Add a 'month_year' column for easier comparisons (e.g., "2024-10")
    df['month_year'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')

    return df
