# Python Library
from datetime import datetime
import logging
import multiprocessing
import os
import re
# Custom Library
import config
from util_web_scrap import PubMed
from util_chroma_db import ChromaDb
from util_doc_generator import DocumentGenerator
# LLM Library
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
# MSSQL Library
import pyodbc

class RAG:
    def __init__(self, model_name):
        # Ollama to trigger AI to response
        self.ollama_url = config.ollama_base_url
        self.ollama_model_name = model_name # "deepseek-r1:1.5b" TODO: Make sure model_name is selectable in the UI
        # Log to Database Connection
        self.mssql_server = config.mssql_server
        self.mssql_database = config.mssql_database
        self.mssql_username = config.mssql_username
        self.mssql_password = config.mssql_password
        # PubMed Web Screap
        self.pubMed = PubMed()
        # Chroma to get context
        self.chromaDb = ChromaDb()
        # Document Generator
        self.docGenerator = DocumentGenerator(model_name=model_name)


    def generate_ollama_response(self, query, isChroma=False, collection_name="", chromaContext="", isWebScrape=False):
        # Get context from Chroma based on selected collection
        if isChroma:
            chromaContext = self.chromaDb.get_context_from_collection(collection_name=collection_name, query=query)
        # Web Scrap Init
        webScrapArticle = ""
        # webScrapContext = ""
        webScrapReference = []
        if isWebScrape:
            webScrapArticle = self.pubMed.search_pubmed(query=query)
            for i, article in enumerate(webScrapArticle):
                # webScrapContext += f"Article {i+1}: {article['title']}\nAbstract: {article.get('abstract', 'N/A')}\n\n"
                webScrapReference.append(f"[{i+1}] {article['title']} - {article['url']}\n\n")
        # AI response generation start
        start_time = datetime.now()
        logging.warning("Generate AI Response (via RAG) Start Time")
        ollama_llm = OllamaLLM(base_url=self.ollama_url, model=self.ollama_model_name)
        # Dynamic prompt based on web scrap
        prompt = f"""
            You are a helpful scientific assistant. Use the provided articles & context below to answer:
            Article: {webScrapArticle}
            Context: {chromaContext}
            Question: {query}
            Answer:
            
            ## Rules:
            1. Cite references like [1], [2], etc.
        """
        # Generate with Ollama
        response = ollama_llm.invoke(prompt)
        # If doing web scrap, append AI response with references received
        if isWebScrape:
            response = f"{response}\n\nReferences:\n\n" + "\n".join(webScrapReference)
        end_time = datetime.now()
        logging.warning("Generate AI Response (via RAG) End")

        # Log to DB
        log_remarks = "Web, Remote Deepseek, ChromaDB and Web Scrapping Integration"
        time_spent_second = (end_time-start_time).total_seconds()
        sourceFileName = os.path.basename(__file__)
        ai_response, ai_think = self.log_to_db(
            user_query=query, 
            ai_think="", 
            ai_response=response, 
            ai_prompt=prompt, 
            remarks=log_remarks, 
            ai_model=self.ollama_model_name, 
            tag=sourceFileName,
            process_time_second=time_spent_second
        )

        # Generate document if AI thinks that user is asking for template/document generation
        document_file_path = ""
        isDocRequest = self.docGenerator.queryIntepreterDocGeneration(user_query=query)
        if isDocRequest:
            document_file_path = self.docGenerator.txtToDoc(ai_response=ai_response)
        return ai_response, ai_think, isDocRequest, document_file_path
    
    def get_sql_connection(self, server, database, username=None, password=None):
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
        try:
            return pyodbc.connect(conn_str)
        except Exception as e:
            logging.error(f"Connection error: {e}")
            return None

    def log_to_db(self, user_query="", ai_think="", ai_response="", ai_prompt="", remarks="", ai_model="", tag="", process_time_second=0):
        conn = self.get_sql_connection(
            server=self.mssql_server,
            database=self.mssql_database,
            username=self.mssql_username,
            password=self.mssql_password
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
        # Execute batch insert
        cursor.executemany(insert_query, [data_list])
        conn.commit()
        # Close connection after data insertion
        cursor.close()
        conn.close()
        return ai_response, ai_think

if __name__ == "__main__":
    # Frontend need to provide ALL the hardcoded values below
    model_name = "deepseek-r1:1.5b"
    rag = RAG(model_name=model_name)
    # Scenario 1: Diabetes (Chroma only)
    query = "What is the potential activity that cause diabetes?"
    ai_response, ai_think, isDocRequest, document_file_path = rag.generate_ollama_response(query, isChroma=True, collection_name="medicalAI_diabetes")
    print("AI Response: " + ai_response)
    print("AI Think: " + ai_think)
    # Scenario 2: Diabetes (Web Scrap only)
    query = "What is the potential activity that cause diabetes?"
    ai_response, ai_think, isDocRequest, document_file_path = rag.generate_ollama_response(query, isWebScrape=True)
    print("AI Response: " + ai_response)
    print("AI Think: " + ai_think)
    # Scenario 3: Diabetes (Chroma and Web Scrap)
    query = "What is the potential activity that cause diabetes?"
    ai_response, ai_think, isDocRequest, document_file_path = rag.generate_ollama_response(query, isWebScrape=True, isChroma=True, collection_name="medicalAI_diabetes")
    print("AI Response: " + ai_response)
    print("AI Think: " + ai_think)
    # Scenario 4: Programmming (Chroma only)
    query = "What is the best programming language to learn AI?"
    ai_response, ai_think, isDocRequest, document_file_path = rag.generate_ollama_response(query, isChroma=True, collection_name="medicalAI_programmingLanguage")
    print("AI Response: " + ai_response)
    print("AI Think: " + ai_think)