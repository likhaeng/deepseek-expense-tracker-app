# Python Library
from datetime import datetime
import logging
import os
import shutil
# Custom Library
from util_doc_loader import DocProcessor
import config
# Chroma Library
import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
# LLM Library
from langchain_chroma import Chroma

logging.basicConfig(format='%(asctime)s %(message)s', filename=config.log_path, level = config.log_level)

class ChromaDb:
    def __init__(self):
        # ChromeDB Connection
        # self.collection_url = ""
        self.collection_host = config.chroma_collection_host
        self.collection_port = config.chroma_collection_port
        self.chroma_client = chromadb.HttpClient(host=self.collection_host, port=self.collection_port)
        # Collection/Database configuration
        # self.collection_name = "ResearchDoc"
        # NOTE Modifiable (using .modify) config to fine tune based on our own use case
        # Default config as per documented: https://docs.trychroma.com/docs/collections/configure
        self.collection_config = config.chroma_collection_hnsw_config
        # Define custom embedding_model to be used. 
        # NOTE: Leave it empty to use default embedding model SentenceTransformers https://docs.trychroma.com/docs/collections/manage-collections
        self.custom_embedding_model = {
            "url": config.chroma_collection_embedding_model_url,
            "model_name": config.chroma_collection_embedding_model_name
        }
        # Define maximum how many splitted list of data that can be uploaded in a single batch
        # e.g. if max_batch_size = 250, and document splitted into 207, then it will generate only 1 batch to process
        # e.g. if max_batch_size = 250, and document splitted into 300, then it will be separated into 2 batches to process
        self.max_batch_size = config.chroma_collection_max_batch_size

    # If error is received during debug, then connection fails
    def verify_connection(self):
        self.chroma_client.heartbeat() # Verify connection.

    # NOTE: Similar in SQL to creating new database
    def init_collection(self, collection_name):
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
            name=collection_name,
            embedding_function=ollama_ef,
            metadata={
                "description": "MedicalAI ResearchDoc Collection", # TODO Change to dynamic based on folder name
                "created": str(datetime.now())
            },
            configuration=self.collection_config
        )

    def delete_collection(self, collection_name):
        self.chroma_client.delete_collection(name=collection_name)

    def review_collections(self):
        collections = self.chroma_client.list_collections()
        logging.warning(collections)

    def review_specific_collection(self, collection_name):
        collection = self.chroma_client.get_collection(name=collection_name)
        logging.warning("Number of records in the collection: " + str(collection.count()))
        # logging.warning("First 10 records in the collection " + str(collection.peek()))

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
    
    def processFileToChroma(self):
        for folderObj in config.sharepoint_download_folder:
            # Setup collection name and folder path via config from json and ini
            chroma_collection_name = folderObj["chroma_collection_name"]
            chroma_local_folder = folderObj["local_folder"]
            local_folder_path = os.path.join(config.sharepoint_processing_folder, chroma_local_folder)
            # Create Chroma DB Collection
            self.init_collection(chroma_collection_name)
            self.review_specific_collection(collection_name=chroma_collection_name) # TODO Can be commented in future to optimize
            # Load and process document
            docLoader = DocProcessor(local_folder_path)
            processing_file_list = docLoader.get_file_list()
            for processing_file in processing_file_list:
                logging.warning("Load and review doc: " + processing_file)
                docData = docLoader.load_and_split_doc(doc_name=processing_file)
                self.add_doc_to_collection(collection_name=chroma_collection_name, docData=docData)
                self.review_specific_collection(collection_name=chroma_collection_name) # TODO Can be commented in future to optimize

    def archiveFile(self):
        for folderObj in config.sharepoint_download_folder:
            # Setup collection name and folder path via config from json and ini
            chroma_local_folder = folderObj["local_folder"]
            local_folder_path = os.path.join(config.sharepoint_processing_folder, chroma_local_folder)
            archive_folder_path = os.path.join(config.sharepoint_archived_folder, chroma_local_folder)
            os.makedirs(archive_folder_path, exist_ok=True)
            # Load and process document
            docLoader = DocProcessor(local_folder_path)
            processing_file_list = docLoader.get_file_list()
            # Archiving file to archived folder
            for file_name in processing_file_list:
                srcFilePath = os.path.join(local_folder_path, file_name)
                dstFilePath = os.path.join(archive_folder_path, file_name)
                logging.warning("Archiving file from " + srcFilePath + " To " + dstFilePath)
                shutil.move(srcFilePath, dstFilePath)

