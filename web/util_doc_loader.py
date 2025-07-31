# Python Library
import os
# LLM Library
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocProcessor:
    def __init__(self, folder_path):
        self.pdf_storage_path = folder_path

    def load_and_split_doc(self, doc_name):
        # Load & Split Documents
        doc_file_path = os.path.join(self.pdf_storage_path, doc_name)
        loader = PyPDFLoader(doc_file_path)
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