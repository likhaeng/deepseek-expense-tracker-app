# Python Library
from pathlib import Path
from yaml.loader import SafeLoader
import os
import sys
import yaml
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Streamlit Library
import streamlit as st  # pip install streamlit
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

def my_logout_callback():
    # Reset UI
    # pages = []
    # pg = st.navigation(pages)
    # pg.run()
    pass


config_file_path = Path(__file__).parent / "config.yaml"
with open(config_file_path) as file:
    authConfig = yaml.load(file, Loader=SafeLoader)

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Dashboard", page_icon=":bar_chart:", layout="wide")

pages =  [
    st.Page("page_chatbot.py", title="Medical AI"),
    st.Page("page_reporting.py", title="Reporting"),
]

# --- USER AUTHENTICATION ---
authenticator = stauth.Authenticate(
    authConfig['credentials'],
    authConfig['cookie']['name'],
    authConfig['cookie']['key'],
    authConfig['cookie']['expiry_days']
)
authenticator.login()

if st.session_state.get('authentication_status') is False:
    st.error("Username/password is incorrect")

if st.session_state.get('authentication_status') is None:
    st.warning("Please enter your username and password")

if st.session_state.get('authentication_status'):
    # ---- SIDEBAR ----
    authenticator.logout("Logout", "sidebar", callback=my_logout_callback())
    if st.session_state.get('roles'):
        user_role = ','.join(st.session_state.get('roles'))
    else:
        user_role = None
    st.sidebar.title(f'Welcome *{st.session_state.get("name")}* ({user_role})')

    # Configure Streamlit page
    st.set_page_config(page_title="iAction AI Medical", layout="wide")

    # Pagination
    pg = st.navigation(pages)
    pg.run()

    # # Title & Description
    # st.title("Medical AI")
    # st.write("Ask AI medical questions based on past research.")

    # # AI Model DropDown Menu
    # modelSelected = st.selectbox(
    #     'Choose your AI Model',
    #     ('deepseek-r1:1.5b', 'deepseek-r1:7b'),
    #     index=0
    # )

    # ## Part 1: Chatbox component
    # # Chatbox init with placeholder
    # user_query = st.chat_input("Ask AI about your finances...")
    # if user_query: # If user input and press Enter, the following code will be triggered
    #     # Display user's input
    #     st.markdown(f"🧑‍💼 **You:** {user_query}")
    #     # AI to think and process the question and generate response to be displayed
    #     with st.spinner("🤖 Thinking... Generating response..."):
    #         # Generation for 1. Response, 2. SQL Query, 3. Thinking Process, 4. SQL Result 
    #         ai_response, think_text = ['', '']
    #         # Display Response
    #         st.markdown(ai_response)
    #         # Display Think Process
    #         with st.expander("💭 AI's Thought Process"):
    #             if isinstance(think_text, list):  # Ensure it's a list
    #                 for i, think_step in enumerate(think_text, start=1):
    #                     st.markdown(f"**Attempt {i}:**")
    #                     st.markdown(f" {think_step}\n")  # Display each attempt as a blockquote
    #             else:
    #                 st.markdown(f"> {think_text}")  # Fallback for single string

