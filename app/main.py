import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import app.database as db
import app.processing as processing
import app.deepseek_ai as deepseek
import app.visualization as visualization
import app.csv_ai as csv_ai
import re

# Configure Streamlit page
st.set_page_config(page_title="AI Financial Budgeting", layout="wide")

# Title & Description
st.title("💰 Deepseek MoneyMind")
st.write("Upload your transaction CSV file OR ask AI financial questions based on past data.")

# Create Tabs for Two Separate Workflows
tab1, tab2 = st.tabs(["📂 Upload CSV", "🤖 Ask AI"])

# 📂 **Tab 1: Upload CSV**
with tab1:
    name = st.selectbox("Select Name", options=["Name 1", "Name 2"], index=0)

    uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

    if uploaded_file:
        # Read and clean CSV
        df = processing.clean_and_process_csv(uploaded_file)
        df["Name"] = name  

        # Section 1: Display Uploaded Transactions
        st.subheader("📊 Uploaded Transactions")
        st.dataframe(df)  
        
        # Display Spending Chart
        st.subheader("📊 Spending Overview")
        visualization.plot_spending_chart(df)  

        # Button to manually load data into PostgreSQL
        if st.button("📥 Load Data into Database"):
            db.insert_transactions(df)
            st.success("Data successfully loaded into the database.")

        # Button to trigger AI-based categorization & insights
        if st.button("🔍 Analyze with AI"):
            # 🔹 Show spinner while AI categorizes transactions
            with st.spinner("🔄 Categorizing transactions with AI..."):
                categorized_df = csv_ai.batch_categorize_transactions(df)  # Run AI-based categorization

            # Section 2: Display AI-Categorized Transactions
            st.subheader("📊 AI-Categorized Transactions")
            st.dataframe(categorized_df)  # Show transactions with AI-generated categories

            # 🔹 Show spinner while AI generates insights
            with st.spinner("💡 Generating insights with AI..."):
                insights = csv_ai.generate_insights(categorized_df)  # Run AI-based analysis

            # Section 3: Display AI Insights
            if insights:
                st.subheader("💡 AI-Generated Insights")
                st.markdown(insights)


with tab2:
    st.subheader("🤖 Deepseek Financial Chatbot")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "last_sql" not in st.session_state:
        st.session_state.last_sql = ""

    if "last_sql_result" not in st.session_state:
        st.session_state.last_sql_result = ""

    if "thinking" not in st.session_state:
        st.session_state.thinking = False

    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None  # Stores user query before rerun

    # Display chat messages in proper order (Oldest at the Top, Newest at the Bottom)
    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.chat_history:
            if role == "You":
                st.markdown(f"🧑‍💼 **You:** {message}")
            else:
                st.markdown(f"🤖 **AI:** {message}")

    # Display generated SQL query BELOW the chat
    if st.session_state.last_sql:
        with st.expander("🔍 See Generated SQL Query"):
            st.code(st.session_state.last_sql, language="sql")

    # Display AI's reasoning (thinking process) in Markdown
    if "last_think_text" in st.session_state and st.session_state.last_think_text:
        with st.expander("💭 AI's Thought Process"):
            if isinstance(st.session_state.last_think_text, list):  # Ensure it's a list
                for i, think_step in enumerate(st.session_state.last_think_text, start=1):
                    st.markdown(f"**Attempt {i}:**")
                    st.markdown(f" {think_step}\n")  # Display each attempt as a blockquote
            else:
                st.markdown(f"> {st.session_state.last_think_text}")  # Fallback for single string


    # Display raw SQL execution result BELOW the chat
    if st.session_state.last_sql_result:
        with st.expander("📊 See SQL Execution Result"):
            st.write(st.session_state.last_sql_result)

    # User input field at the bottom
    user_query = st.chat_input("Ask AI about your finances...")

    if user_query:
        # Store the user query before rerun
        st.session_state.pending_query = user_query
        st.session_state.thinking = True
        st.rerun()

    if st.session_state.thinking and st.session_state.pending_query:
        with st.spinner("🤖 Thinking... Generating response..."):
            user_query = st.session_state.pending_query  # Retrieve stored query
            # print(user_query)  # Debugging: Ensure query is retained

            sql_query, ai_response, sql_result, think_text = deepseek.ask_financial_question(user_query, return_sql=True, return_result=True)

            # Save chat history in proper order
            st.session_state.chat_history.append(("You", user_query))
            st.session_state.chat_history.append(("🤖 AI", ai_response))

            # Save last generated SQL and executed result
            st.session_state.last_sql = sql_query
            st.session_state.last_think_text = think_text 
            st.session_state.last_sql_result = sql_result

            # Clear stored query and reset thinking state
            st.session_state.pending_query = None
            st.session_state.thinking = False
            st.rerun()

