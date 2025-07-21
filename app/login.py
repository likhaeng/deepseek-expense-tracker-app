

import os
import pickle
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import app.csv_ai as csv_ai
# import app.database as db
import app.deepseek_ai as deepseek
import app.processing as processing
import app.visualization as visualization
# import pandas as pd  # pip install pandas openpyxl
# import plotly.express as px  # pip install plotly-express
# import re
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml

from pathlib import Path
from yaml.loader import SafeLoader

config_file_path = Path(__file__).parent / "config.yaml"
# print(config_file_path)
with open(config_file_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")


# --- USER AUTHENTICATION ---
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]

# load hashed passwords
# file_path = Path(__file__).parent / "hashed_pw.pkl"
# with file_path.open("rb") as file:
#     hashed_passwords = pickle.load(file)

# authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "sales_dashboard", "abcdef", cookie_expiry_days=30)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# name, authentication_status, username = authenticator.login("Login", "main")
authenticator.login()

if st.session_state.get('authentication_status') is False:
    st.error("Username/password is incorrect")

if st.session_state.get('authentication_status') is None:
    st.warning("Please enter your username and password")

if st.session_state.get('authentication_status'):
    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar")
    # authenticator.logout("Logout", "sidebar", callback=resetParam())
    if st.session_state.get('roles'):
        user_role = ','.join(st.session_state.get('roles'))
    else:
        user_role = None
    st.sidebar.title(f'Welcome *{st.session_state.get("name")}* ({user_role})')

    # Configure Streamlit page
    st.set_page_config(page_title="iAction AI Financial", layout="wide")

    # Title & Description
    # st.title("💰 Deepseek AutoCount")
    st.title("Deepseek AutoCount")
    st.write("Upload your transaction CSV file OR ask AI financial questions based on past data.")
  
    ## Part 1: File Upload, Graph Generation, Load Data to Table, Generate AI Analysis component
    uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

    if uploaded_file:
        # Read and clean CSV
        df = processing.clean_and_process_csv(uploaded_file) 

        # Section 1: Display Uploaded Transactions
        st.subheader("📊 Uploaded Transactions")
        st.dataframe(df.style.format({"Total": "{:.2f}"})) # Make sure Total column have 2 decimal places
        
        # Display Spending Chart
        st.subheader("📊 Spending Overview")
        visualization.plot_spending_chart(df)

        # Button to trigger AI-based categorization & insights
        if st.button("🔍 Analyze with AI"):
            # NOTE: Temporary disabled as this categorization is not applicable to PO
            # 🔹 Show spinner while AI categorizes transactions
            # with st.spinner("🔄 Categorizing transactions with AI..."):
            #     categorized_df = csv_ai.batch_categorize_transactions(df)  # Run AI-based categorization

            # # Section 2: Display AI-Categorized Transactions
            # st.subheader("📊 AI-Categorized Transactions")
            # st.dataframe(categorized_df)  # Show transactions with AI-generated categories

            # 🔹 Show spinner while AI generates insights
            with st.spinner("💡 Generating insights with AI..."):
                insights = csv_ai.generate_insights(df)  # Run AI-based analysis

            # Section 3: Display AI Insights
            if insights:
                st.subheader("💡 AI-Generated Insights")
                st.markdown(insights)

        # Button to manually load data into PostgreSQL
        if st.button("📥 Load Data into Database"):
            # NOTE: Temporary not applicable as too many not null fields to be integrated from AutoCount database PO table
            # db.insert_transactions(df)
            # st.success("Data successfully loaded into the database.")
            st.warning("Function Work In Progress.")

    ## Part 2: Chatbox component
    # Chatbox init with placeholder
    user_query = st.chat_input("Ask AI about your finances...")
    if user_query: # If user input and press Enter, the following code will be triggered
        # Display user's input
        st.markdown(f"🧑‍💼 **You:** {user_query}")
        # AI to think and process the question and generate response to be displayed
        with st.spinner("🤖 Thinking... Generating response..."):
            # Generation for 1. Response, 2. SQL Query, 3. Thinking Process, 4. SQL Result 
            sql_query, ai_response, sql_result, think_text = deepseek.ask_financial_question(user_query, role=user_role, return_sql=True, return_result=True)
            # Display Response
            st.markdown(ai_response)
            # Display SQL Query
            with st.expander("🔍 See Generated SQL Query"):
                st.code(sql_query, language="sql")
            # Display Think Process
            with st.expander("💭 AI's Thought Process"):
                if isinstance(think_text, list):  # Ensure it's a list
                    for i, think_step in enumerate(think_text, start=1):
                        st.markdown(f"**Attempt {i}:**")
                        st.markdown(f" {think_step}\n")  # Display each attempt as a blockquote
                else:
                    st.markdown(f"> {think_text}")  # Fallback for single string
            # Display SQL Result
            with st.expander("📊 See SQL Execution Result"):
                st.write(sql_result)

