# Python Library
from datetime import datetime, timedelta
import logging
import os
# Custom Library
import config
from config import update_config
# Sharepoint Library
from office365.sharepoint.client_context import ClientContext

logging.basicConfig(format='%(asctime)s %(message)s', filename=config.log_path, level = config.log_level)

class SharePointUtil():
    def __init__(self):
        self.site_domain_name   = config.sharepoint_domain_name
        self.site_url           = config.sharepoint_site_url
        self.client_id          = config.sharepoint_client_id
        self.thumbprint         = config.sharepoint_thumbprint
        self.cert_path          = config.sharepoint_cert_path
        self.ctx                = self.authClientContext()

    def authClientContext(self):
        ## Authenticate with ClientContext
        cert_settings = {
            'client_id': self.client_id,
            'thumbprint': self.thumbprint, # Please refer to your own selfsigncert.crt to get this value
            'cert_path': self.cert_path,
        }
        ctx = ClientContext(self.site_url).with_client_certificate(self.site_domain_name, **cert_settings)
        # Simple verification
        web = ctx.web.get().execute_query()
        logging.warning("Connected to SharePoint Site: " + str(web.properties["Title"]))
        return ctx
    
    def list_files_recursively(self, folder_url, file_list, file_type=['.pdf'], timezone_diff=8):
        """
        Recursively lists files and folders within a given SharePoint folder.
        """
        # Get the folder object
        root_folder = self.ctx.web.get_folder_by_server_relative_path(folder_url)
        self.ctx.load(root_folder).execute_query()

        # Get files within the current folder
        files = root_folder.files
        self.ctx.load(files).execute_query()
        for file in files:
            logging.warning(f"File: {file.serverRelativeUrl}")
            file_created_datetime = file.time_created + timedelta(hours=timezone_diff)
            file_extension = os.path.splitext(file.name)[1]
            if file_created_datetime > config.sharepoint_last_process_datetime and file_extension.lower() in file_type:
                file_list.append(file)

        # Get subfolders and recurse
        folders = root_folder.folders
        self.ctx.load(folders).execute_query()
        for subfolder in folders:
            # Skip system folders like "Forms"
            if not subfolder.name.startswith("_"):
                self.list_files_recursively(subfolder.serverRelativeUrl, file_list)
        return file_list
    
    # NOTE: Since this function only download file recursively into a single folder, 
    # it is possible that there are duplicated filename from source sharepoint folder, which can be a challenge
    def downloadFileByFolder(self):
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        logging.warning("Current value of sharepoint_last_process_datetime: " + str(config.sharepoint_last_process_datetime))
        isError = False
        for folderObj in config.sharepoint_download_folder:
            try:
                # Get value from config
                folder_url = folderObj["remote_folder"]
                local_folder_name = folderObj["local_folder"]
                logging.warning("Accessing sharepoint folder via: " + folder_url)
                # Get remote files path from sharepoint folder
                file_list = []
                file_list = self.list_files_recursively(folder_url, file_list)
                # Folder Preparation to store file locally
                local_folder_path = os.path.join(config.sharepoint_processing_folder, local_folder_name)
                os.makedirs(local_folder_path, exist_ok=True)
                # Download files
                for file in file_list:
                    file_name = file.name
                    file_url = file.serverRelativeUrl
                    local_path = os.path.join(local_folder_path, file_name)
                    with open(local_path, "wb") as local_file:
                        file = self.ctx.web.get_file_by_server_relative_url(file_url).download(local_file).execute_query()
                    logging.warning(f"File downloaded successfully to: {local_path}")
            except Exception as ex:
                logging.error("Could not retrieve files from folder '%s/%s', Error: %s", folder_url, local_folder_name, str(ex))
                isError=True
        # If no error
        if not isError:
            update_config('PERSIST_VARIABLE', 'sharepoint_last_process_datetime', now)

        # pass
        # ## Downloading files
        # file_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest/Document.docx" # Replace with the actual path to your file
        # local_path = "Document.docx" # Replace with the desired local filename
        # try:
        #     with open(local_path, "wb") as local_file:
        #         file = self.ctx.web.get_file_by_server_relative_url(file_path).download(local_file).execute_query()
        #     print(f"File downloaded successfully to: {local_path}")
        # except Exception as e:
        #     print(f"Error downloading file: {e}")

if __name__ == "__main__":
    sharepointObj = SharePointUtil()
    sharepointObj.downloadFileByFolder()

# ## Uploading files
# import os
# sharepoint_folder_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest"
# local_file_path = "sample.csv"
# file_name = os.path.basename(local_file_path)
# try:
#     target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_path)
#     with open(local_file_path, "rb") as f:
#         uploaded_file = target_folder.files.upload(f, file_name).execute_query()
#     print(f"File '{file_name}' uploaded successfully to: {uploaded_file.properties}")
# except Exception as e:
#     print(f"Error uploading file: {e}")



# ## Reading files into memory (for ETL)
# import pandas as pd
# import io
# from office365.sharepoint.files.file import File
# # Specify the file path on SharePoint (server-relative)
# remote_csv_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest/sample.csv"
# response = File.open_binary(ctx, remote_csv_path)
# file_content = response.content  # bytes of the file
# # Load into pandas DataFrame directly from bytes (assuming CSV format)
# df = pd.read_csv(io.BytesIO(file_content))
# # Optional: handle case where file might not exist or be empty
# if df.shape[0] == 0:
#     raise FileNotFoundError(f"No data found. The file might be empty or path is incorrect: {remote_csv_path}")
# else:
#     print("DataFrame loaded. Shape:", df.shape)
#     print(df.head())



# ## Writing data directly to SharePoint (from pandas DataFrame)
# import pandas as pd
# from io import BytesIO
# sharepoint_folder_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest"  # Replace with the desired SharePoint folder path
# file_name = "sample.csv"
# df = pd.DataFrame({'Sales': [100, 200, 300], 'Region': ['East', 'West', 'South']})
# buffer = BytesIO()
# df.to_csv(buffer, index=False)
# buffer.seek(0)  # Reset the buffer's position to the start
# try:
#     target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_path)
#     uploaded_file = target_folder.files.upload(buffer, file_name).execute_query()
#     print(f"Data written to '{uploaded_file.properties}' successfully.")
# except Exception as e:
#     print(f"Error writing data to SharePoint: {e}")