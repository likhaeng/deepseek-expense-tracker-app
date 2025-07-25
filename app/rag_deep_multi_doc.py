import os
import streamlit as st
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

PROMPT_TEMPLATE = """
You are an expert research assistant. Use the provided context to answer the query. 
If unsure, state that you don't know. Be concise and factual (max 3 sentences).

Query: {user_query} 
Context: {document_context} 
Answer:
"""

PDF_STORAGE_PATH = 'document_store/pdfs/'
# Define Ollama Model
# OLLAMA_MODEL = 'deepseek-r1:7b' # Use the correct model name in Ollama
OLLAMA_MODEL = 'deepseek-r1:7b' # Use the correct model name in Ollama
EMBEDDING_MODEL = OllamaEmbeddings(model=OLLAMA_MODEL)
DOCUMENT_VECTOR_DB = InMemoryVectorStore(EMBEDDING_MODEL)
LANGUAGE_MODEL = OllamaLLM(model=OLLAMA_MODEL)

def load_pdf_documents():
    folder_path = PDF_STORAGE_PATH
    docs = []
    for file in os.listdir(folder_path):
        full_file_path = os.path.join(folder_path, file)
        if os.path.isfile(full_file_path):
            document_loader = PDFPlumberLoader(full_file_path)
            raw_doc = document_loader.load()
            docs.append(raw_doc)
    return docs

def chunk_documents(raw_documents):
    doc_chunks = []
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    for doc in raw_documents:
        doc_chunk = text_processor.split_documents(doc)
        doc_chunks.append(doc_chunk)
    return doc_chunks

def index_documents(document_chunks):
    for doc_chunk in document_chunks:
        DOCUMENT_VECTOR_DB.add_documents(doc_chunk)

def find_related_documents(query):
    return DOCUMENT_VECTOR_DB.similarity_search(query)

def generate_answer(user_query, context_documents):
    context_text = "\n\n".join([doc.page_content for doc in context_documents])
    conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    response_chain = conversation_prompt | LANGUAGE_MODEL
    return response_chain.invoke({"user_query": user_query, "document_context": context_text})

raw_docs = load_pdf_documents()
processed_chunks = chunk_documents(raw_docs)
index_documents(processed_chunks)
user_query = 'Between Python and Java, which is the better programming language?'
relevant_docs = find_related_documents(user_query)
ai_response = generate_answer(user_query, relevant_docs)
print(ai_response)
print('Done')
