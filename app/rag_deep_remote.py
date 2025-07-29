# LLM Library
# from langchain_community.vectorstores import Chroma # The class `Chroma` was deprecated in LangChain 0.2.9 and will be removed in 1.0. An updated version of the class exists in the :class:`~langchain-chroma package and should be used instead.
from langchain_chroma import Chroma
# from langchain_community.llms import Ollama # Deprecated, use OllamaLLM
from langchain_ollama import OllamaLLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Chroma Library
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
# Python Library
from datetime import datetime
import multiprocessing
import os
# Custom Library
from log_to_database import log_to_db

# # Set up remote Ollama
# ollama_llm = Ollama(base_url="http://172.20.1.48:11434", model="deepseek-r1:1.5b")
# embeddings = OllamaEmbeddings(base_url="http://172.20.1.48:11434", model="nomic-embed-text")

# # Load & split documents
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# docs = [...]  # Your documents here
# splits = text_splitter.split_documents(docs)

# # Store in ChromaDB
# vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# # RAG prompt
# query = "What is Retrieval-Augmented Generation?"
# retrieved_docs = vectorstore.similarity_search(query)
# context = "\n".join([doc.page_content for doc in retrieved_docs])

# prompt = f"""Answer the question based on the context below:
# Context: {context}
# Question: {query}
# Answer:"""

# # Generate with Ollama
# response = ollama_llm(prompt)
# print(response)

class ChromaDb:
    def __init__(self):
        # ChromeDB Connection
        self.collection_url = ""
        self.collection_host = "172.20.1.48"
        self.collection_port = 8000
        self.chroma_client = chromadb.HttpClient(host=self.collection_host, port=self.collection_port)
        # Collection/Database configuration
        self.collection_name = "ResearchDoc"
        # NOTE Modifiable (using .modify) config to fine tune based on our own use case
        # Default config as per documented: https://docs.trychroma.com/docs/collections/configure
        self.collection_config = {
            "hnsw": {
                "space": "l2",
                "ef_construction": 100,
                "ef_search": 100,
                "max_neighbors": 16,
                "num_threads": 16, # NOTE: Change according based on AI server spec. Check using lscpu at section CPU(s)
                "batch_size": 100,
                "sync_threshold": 1000,
                "resize_factor": 1.2
            }
        }
        # Define custom embedding_model to be used. 
        # NOTE: Leave it empty to use default embedding model SentenceTransformers https://docs.trychroma.com/docs/collections/manage-collections
        self.custom_embedding_model = {
            "url": "http://172.20.1.48:11434",
            "model_name": "nomic-embed-text:v1.5"
        }
        # Define maximum how many splitted list of data that can be uploaded in a single batch
        # e.g. if max_batch_size = 250, and document splitted into 207, then it will generate only 1 batch to process
        # e.g. if max_batch_size = 250, and document splitted into 300, then it will be separated into 2 batches to process
        self.max_batch_size = 250

    # If error is received during debug, then connection fails
    def verify_connection(self):
        self.chroma_client.heartbeat() # Verify connection.

    # NOTE: Similar in SQL to creating new database
    def init_collection(self):
        # NOTE: Only 1 specific embedding model is set for a single collection/database
        if self.custom_embedding_model:
            # Custom embedding model
            ollama_ef = OllamaEmbeddingFunction(
                url=self.custom_embedding_model["url"],  # Default Ollama server address
                model_name=self.custom_embedding_model["model_name"] # Or your specific embedding model like 'llama2', 'deepseek-r1' etc.
            )
        else:
            ollama_ef = DefaultEmbeddingFunction() # Default embedding model as SentenceTransformers https://docs.trychroma.com/docs/collections/manage-collections
        # Get or Create ChromaDB collection
        self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=ollama_ef,
            metadata={
                "description": "MedicalAI ResearchDoc Collection",
                "created": str(datetime.now())
            },
            configuration=self.collection_config
        )

    def delete_collection(self, collection_name):
        self.chroma_client.delete_collection(name=collection_name)

    def review_collections(self):
        collections = self.chroma_client.list_collections()
        print(collections)

    def review_specific_collection(self, collection_name):
        collection = self.chroma_client.get_collection(name=collection_name)
        print("Number of records in the collection: " + str(collection.count()))
        # print("First 10 records in the collection " + str(collection.peek()))

    def add_doc_to_collection(self, collection_name, docData):
        # Dynamic data chunking process based on max batch size defined
        docDataBatch = []
        docDataCount = len(docData)
        if docDataCount <= self.max_batch_size:
            docDataBatch.append(docData)
        else:
            docDataBatch = [docData[i:i + self.max_batch_size] for i in range(0, len(docData), self.max_batch_size)]
        # Connect to ChromaDB Server
        chroma_conn = Chroma(
            collection_name=collection_name,
            host=self.collection_host,
            port=self.collection_port
        )
        # Add documents to ChromaDB (uses HTTP calls)
        for docDataList in docDataBatch:
            chroma_conn.add_documents(docDataList)

    def get_context_from_collection(self, collection_name, query):
        # Connect to ChromaDB Server
        chroma_conn = Chroma(
            collection_name=collection_name,
            host=self.collection_host,
            port=self.collection_port
        )
        # Retrieve relevant context from ChromaDB's collection
        retrieved_docs = chroma_conn.similarity_search(query)
        context = "\n".join([doc.page_content for doc in retrieved_docs])
        return context

class DocProcessor:
    def __init__(self):
        self.pdf_storage_path = "document_store/pdfs/"

    def load_and_split_doc(self, doc_name):
        # Load & Split Documents
        loader = PyPDFLoader(self.pdf_storage_path + doc_name)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        return splits
    
    def get_file_list(self):
        file_list = []
        for file in os.listdir(self.pdf_storage_path):
            file_list.append(file)
        return file_list
    
    def int_to_ordinal(self, n):
        """
        Converts an integer to its English ordinal representation.
        e.g., 1 -> '1st', 2 -> '2nd', 3 -> '3rd', 4 -> '4th', 11 -> '11th'
        """
        if 10 <= n % 100 <= 20:  # Handles 11th, 12th, 13th
            suffix = 'th'
        else:
            last_digit = n % 10
            if last_digit == 1:
                suffix = 'st'
            elif last_digit == 2:
                suffix = 'nd'
            elif last_digit == 3:
                suffix = 'rd'
            else:
                suffix = 'th'
        return str(n) + suffix
class RAG:
    def __init__(self):
        self.ollama_url = "http://172.20.1.48:11434"
        self.ollama_model_name = "deepseek-r1:7b"

    def generate_ollama_response(self, context, query):
        start_time = datetime.now()
        print("Generate AI Response (via RAG) Start Time: " + str(start_time))
        ollama_llm = OllamaLLM(base_url=self.ollama_url, model=self.ollama_model_name)
        prompt = f"""Answer the question based on the context below:
            Context: {context}
            Question: {query}
            Answer:"""

        # Generate with Ollama
        response = ollama_llm(prompt)
        print(response)
        end_time = datetime.now()
        print("Generate AI Response (via RAG) End Time: " + str(end_time))

        # Log to DB
        log_remarks = "Remote Deepseek & ChromaDB Integration"
        time_spent_second = (end_time-start_time).total_seconds()
        sourceFileName = os.path.basename(__file__)
        log_to_db(
            user_query=query, 
            ai_think="", 
            ai_response=response, 
            ai_prompt=prompt, 
            remarks=log_remarks, 
            ai_model=self.ollama_model_name, 
            tag=sourceFileName,
            process_time_second=time_spent_second
        )

if __name__ == "__main__":
    print("Python Classes Init Start Time: " + str(datetime.now()))
    collection_name = "ResearchDoc"
    chromaMedical = ChromaDb()
    # chromaMedical.verify_connection()
    # chromaMedical.init_collection()
    # chromaMedical.review_collections()
    # chromaMedical.review_specific_collection(collection_name="ResearchDoc")
    docLoader = DocProcessor()
    ragProcess = RAG()
    print("Python Classes Init End Time: " + str(datetime.now()))

    # Routine 1: 
    # 1. Initialize collection/database
    # 2. Load document into data
    # 3. Add data into ChromaDB collection/database
    # 4. Review database count and record
    print("Collection Creation & Review Start Time: " + str(datetime.now()))
    chromaMedical.init_collection()
    chromaMedical.review_collections()
    chromaMedical.review_specific_collection(collection_name=collection_name)
    print("Collection Creation & Review End Time: " + str(datetime.now()))
    # Process documents in a list based on a single folder path
    docList = docLoader.get_file_list()
    for idx, doc_name in enumerate(docList):
        strOrdinal = docLoader.int_to_ordinal(idx + 1)
        print("Load and review " + strOrdinal + " doc Start Time: " + str(datetime.now()))
        docData = docLoader.load_and_split_doc(doc_name=doc_name)
        chromaMedical.add_doc_to_collection(collection_name=collection_name, docData=docData)
        chromaMedical.review_specific_collection(collection_name=collection_name)
        print("Load and review " + strOrdinal + " doc End Time: " + str(datetime.now()))

    # 1st Test Result Review:
    # 1. After 1st doc is loaded, then records grow from 0 -> 207 (python pdf have 140 pages)
    # 2. process of add_doc_to_collection func for 1st doc take more than 30 seconds
    # 3. load_and_split_doc func may take more than 30 seconds to run as well (happens to 2nd)
    # 4. process of add_doc_to_collection func for 2nd doc fails due to error **httpx.ReadTimeout: The read operation timed out** (java pdf have 699 pages)

    # 2nd Test Result Review:
    # 1. Note: change java pdf to html tutorial pdf
    # 2. After 1st doc is loaded, then records grow from 0 -> 207 (python pdf have 140 pages)
    # 3. After 2nd doc is loaded, then records grow from 207 -> 339 (html tutorial pdf have 56 pages)

    # 3rd Test Result Review:
    # 1. Note: Test with print/log enhancement to track time taken for each process
    # 2. After 1st doc is loaded, then records grow from 0 -> 207 (python pdf have 140 pages) (28 seconds)
    # 3. After 2nd doc is loaded, then records grow from 207 -> 339 (html tutorial pdf have 56 pages) (44 seconds)

    # TODO: Look more into the document loader to review the chunk data that has been splitted (e.g. total size, chunk count, chunk data)
    # TODO: Try to fine tune the document loader so that it may process document in bigger size (chunk_size, chunk_overlap)
    # TODO: Try to split document into multiple batch of chunk if certain condition has been exceed. This is to avoid the upload timeout error that is stated in 1st Test Result Review

    # Documents
    # 1. Python Programming.pdf - 140 pages, 207 chunks
    # 2. html_tutorial.pdf - 56 pages, 132 chunks
    # 3. javanotes5.pdf - 699 pages, 2637 chunks
    # 4. the-complete-reference-html-css-fifth-edition.pdf - 857 pages, 2305 chunks

    # Routine 2:
    # 1. Get collection/database
    # 2. Using available data, send user query/question to AI for response. RAG will be retrieved from the ChromaDB
    # 3. Log to database
    # RAG prompt
    # print("Get context from collection/database Start Time: " + str(datetime.now()))
    # # query = "Between Python and HTML, which is the better programming language?"
    # # query = "I am new to programming. Please suggest the best prgramming language to learn for as a beginner"
    # query = "What can you tell me more about Java programming?"
    # context = chromaMedical.get_context_from_collection(collection_name=collection_name, query=query)
    # print("Get context from collection/database End Time: " + str(datetime.now()))
    # # Generate AI response with RAG
    # ragProcess.generate_ollama_response(context=context, query=query)
    
    # 1st Test Result Review:

    # Routine 3:
    # 1. Delete collection
    # chromaMedical.delete_collection(collection_name="ResearchDoc")
    

        