# Python Library
import os
# Custom Library
from util_deepseek_rag import RAG
from util_doc_generator import DocumentGenerator
import config
# Streamlit Library
import streamlit as st  # pip install streamlit

# Title & Description
st.title("Medical AI")
st.write("Ask AI medical questions based on past research.")

# AI Model DropDown Menu
# modelSelected = st.selectbox(
#     'Choose your AI Model',
#     ('deepseek-r1:1.5b', 'deepseek-r1:7b'),
#     index=0 # default to first option
# )
modelSelected = st.selectbox(
    'Choose your AI Model',
    config.model_list,
    index=0 # default to first option
)

# AI Model DropDown Menu
# searchModeSelected = st.selectbox(
#     'Choose your Search Mode',
#     ('Past Research', 'PubMed', 'Past Research + PubMed', 'Nutrionist Plan'),
#     index=0 # default to first option
# )

searchModeSelected = st.selectbox(
    'Choose your Search Mode',
    config.search_mode_list,
    index=0 # default to first option
)

## Part 1: Chatbox component
# Chatbox init with placeholder
user_query = st.chat_input("Ask AI about your past researches...")
if user_query: # If user input and press Enter, the following code will be triggered
    # Display user's input
    st.markdown(f"🧑‍💼 **You:** {user_query}")
    # AI to think and process the question and generate response to be displayed
    with st.spinner("🤖 Thinking... Generating response..."):
        # Generation for 1. Response, 2. SQL Query, 3. Thinking Process, 4. SQL Result 
        # Init RAG & Doc Generator based on the AI model selected
        ragMode = RAG(model_name=modelSelected)
        # Get ChromaDB collection to be used
        collection_name = config.search_mode_and_collection_map[searchModeSelected]
        # Dynamic AI response generation based on selected search Mode
        if searchModeSelected == "Past Research":
            ai_response, think_text, isDocRequest, document_file_path  = ragMode.generate_ollama_response(user_query, isChroma=True, collection_name=collection_name)
        elif searchModeSelected == "PubMed":
            ai_response, think_text, isDocRequest, document_file_path = ragMode.generate_ollama_response(user_query, isWebScrape=True)
        elif searchModeSelected == "Past Research + PubMed":
            ai_response, think_text, isDocRequest, document_file_path = ragMode.generate_ollama_response(user_query, isWebScrape=True, isChroma=True, collection_name=collection_name)
        elif searchModeSelected == "Nutrionist Plan":
            ai_response, think_text, isDocRequest, document_file_path = ragMode.generate_ollama_response(user_query, isChroma=True, collection_name=collection_name)
        # Display Response
        st.markdown(ai_response)
        # Generate document if AI thinks that user is asking for template/document generation
        if isDocRequest:
            st.markdown("Download the file below:")
            filename_with_extension = os.path.basename(document_file_path)
            with open(document_file_path, "rb") as f:
                st.download_button('Download File', f, file_name=filename_with_extension)
        # Display Think Process
        with st.expander("💭 AI's Thought Process"):
            if isinstance(think_text, list):  # Ensure it's a list
                for i, think_step in enumerate(think_text, start=1):
                    st.markdown(f"**Attempt {i}:**")
                    st.markdown(f" {think_step}\n")  # Display each attempt as a blockquote
            else:
                st.markdown(f"> {think_text}")  # Fallback for single string