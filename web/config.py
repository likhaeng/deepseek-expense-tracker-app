from configparser import ConfigParser, NoSectionError
from datetime import datetime
import logging
import json
import os
from dotenv import load_dotenv

# Base Directory and Source System
BASE_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

# Init config from config.ini
config_file_name = 'config.ini'
config_file_path = os.path.join(BASE_DIR, 'web', config_file_name)
config = ConfigParser()
config.read(config_file_path) # NOTE: Following can be updated based on user local environment

# init config from config.json
with open(os.path.join(BASE_DIR, 'web', 'config.json'), 'r') as f:
    config_json = json.load(f)

# Init config from .env
load_dotenv()

# Logging Config
now         = datetime.now()               
tmp_str     = str(now.strftime('%Y%m%d%H%M%S')) # To be used on log file naming
log_path    = os.path.join(BASE_DIR, "log", 'prg_' + tmp_str + '.log')
log_level   = logging.WARNING # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Sharepoint Config (env)
sharepoint_domain_name              = os.getenv("SHAREPOINT_DOMAIN_NAME")
sharepoint_site_url                 = os.getenv("SHAREPOINT_SITE_URL")
sharepoint_client_id                = os.getenv("SHAREPOINT_CLIENT_ID")
sharepoint_thumbprint               = os.getenv("SHAREPOINT_THUMBPRINT")
sharepoint_cert_path                = os.getenv("SHAREPOINT_CERT_PATH")
# Sharepoint Config (ini)
sharepoint_processing_folder        = os.path.join(BASE_DIR, *config['SHAREPOINT']['processing_folder'].split("|"))
sharepoint_archived_folder          = os.path.join(BASE_DIR, *config['SHAREPOINT']['archived_folder'].split("|"))
# Sharepoint Config (json)
sharepoint_download_folder          = config_json.get('SHAREPOINT_DOWNLOAD_FOLDER')

# Persist Variable Config
sharepoint_last_process_datetime    = datetime.strptime(config['PERSIST_VARIABLE']['sharepoint_last_process_datetime'], "%Y%m%d%H%M%S")

# Chroma Config (ini)
chroma_collection_host                  = config['CHROMA']['collection_host']
chroma_collection_port                  = int(config['CHROMA']['collection_port'])
chroma_collection_embedding_model_url   = config['CHROMA']['collection_embedding_model_url']
chroma_collection_embedding_model_name  = config['CHROMA']['collection_embedding_model_name']
chroma_collection_max_batch_size        = int(config['CHROMA']['collection_max_batch_size'])
# Chroma Config (json)
chroma_collection_hnsw_config           = config_json.get('CHROMA_COLLECTION_HNSW_CONFIG')

# Pubmed Config (ini)
pubmed_base_url     = config['PUBMED']['base_url']
pubmed_tool_name    = config['PUBMED']['tool_name']
pubmed_email        = config['PUBMED']['email']

# Spacy Config (ini)
spacy_language_model = config['SPACY']['language_model']

# MSSQL Config (env)
mssql_server    = os.getenv("MSSQL_SERVER")
mssql_database  = os.getenv("MSSQL_DATABASE")
mssql_username  = os.getenv("MSSQL_USERNAME")
mssql_password  = os.getenv("MSSQL_PASSWORD")

# OLLAMA Config (ini)
ollama_base_url = config['OLLAMA']['base_url']

# Frontend Config (json)
model_list                      = config_json.get('SUPPORTED_AI_MODEL')
search_mode_and_collection_map  = config_json.get('SEARCH_MODE_AND_COLLECTION_MAP')
search_mode_list                = config_json.get('SEARCH_MODE_AND_COLLECTION_MAP').keys()

# config.ini Update Function
def update_config(section, key, value):
    config = ConfigParser()
    # Preserve case sensitivity (Python 3.8+)
    config.optionxform = lambda option: option
    # Read existing config or create new if doesn't exist
    config.read(config_file_path)
    try:
        # Update or add the key-value pair
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, key, value)
        # Write the updated config back to file
        with open(config_file_path, 'w') as configfile:
            config.write(configfile)
        return True
    except (NoSectionError, TypeError, ValueError) as e:
        print(f"Error updating config: {e}")
        return False

if __name__ == "__main__": 
    # Example usage
    update_config('PERSIST_VARIABLE', 'sharepoint_last_process_datetime', '20200101231259')