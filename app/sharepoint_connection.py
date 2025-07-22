## NOTE: Refer to https://www.merge.dev/blog/sharepoint-api-python on how to generate certificate and private keys
## Please remember to generate your own certificates, and register into the sharepoint admin app permission section

## NOTE This section is not used START
## App-based authentication
# from office365.sharepoint.client_context import ClientContext
# from office365.runtime.auth.client_credential import ClientCredential
# import os
# CLIENT_ID = ""
# CLIENT_SECRET = ""
# SITE_URL = "https://t0tkb.sharepoint.com/sites/ITHelpDesk2"
# credentials = ClientCredential(CLIENT_ID, CLIENT_SECRET)
# ctx = ClientContext(SITE_URL).with_credentials(credentials)
# # Simple verification
# web = ctx.web.get().execute_query()
# print("Connected to SharePoint Site:", web.properties["Title"])
## NOTE This section is not used END


## Authenticate with ClientContext
SITE_URL = "https://t0tkb.sharepoint.com/sites/ITHelpDesk2"
from office365.sharepoint.client_context import ClientContext
cert_settings = {
    'client_id': "47ea28fb-bbcb-4a01-84b4-a11af6d18663",
    'thumbprint': "", # Please refer to your own selfsigncert.crt to get this value
    'cert_path':    "selfsigncert.pem",
}
ctx = ClientContext(SITE_URL).with_client_certificate("t0tkb.onmicrosoft.com", **cert_settings)
# Simple verification
web = ctx.web.get().execute_query()
print("Connected to SharePoint Site:", web.properties["Title"])



## Downloading files
file_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest/Document.docx" # Replace with the actual path to your file
local_path = "Document.docx" # Replace with the desired local filename
try:
    with open(local_path, "wb") as local_file:
        file = ctx.web.get_file_by_server_relative_url(file_path).download(local_file).execute_query()
    print(f"File downloaded successfully to: {local_path}")
except Exception as e:
    print(f"Error downloading file: {e}")



## Uploading files
import os
sharepoint_folder_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest"
local_file_path = "sample.csv"
file_name = os.path.basename(local_file_path)
try:
    target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_path)
    with open(local_file_path, "rb") as f:
        uploaded_file = target_folder.files.upload(f, file_name).execute_query()
    print(f"File '{file_name}' uploaded successfully to: {uploaded_file.properties}")
except Exception as e:
    print(f"Error uploading file: {e}")



## Reading files into memory (for ETL)
import pandas as pd
import io
from office365.sharepoint.files.file import File
# Specify the file path on SharePoint (server-relative)
remote_csv_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest/sample.csv"
response = File.open_binary(ctx, remote_csv_path)
file_content = response.content  # bytes of the file
# Load into pandas DataFrame directly from bytes (assuming CSV format)
df = pd.read_csv(io.BytesIO(file_content))
# Optional: handle case where file might not exist or be empty
if df.shape[0] == 0:
    raise FileNotFoundError(f"No data found. The file might be empty or path is incorrect: {remote_csv_path}")
else:
    print("DataFrame loaded. Shape:", df.shape)
    print(df.head())



## Writing data directly to SharePoint (from pandas DataFrame)
import pandas as pd
from io import BytesIO
sharepoint_folder_path = "/sites/ITHelpDesk2/Shared Documents/PythonIntegrationTest"  # Replace with the desired SharePoint folder path
file_name = "sample.csv"
df = pd.DataFrame({'Sales': [100, 200, 300], 'Region': ['East', 'West', 'South']})
buffer = BytesIO()
df.to_csv(buffer, index=False)
buffer.seek(0)  # Reset the buffer's position to the start
try:
    target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_path)
    uploaded_file = target_folder.files.upload(buffer, file_name).execute_query()
    print(f"Data written to '{uploaded_file.properties}' successfully.")
except Exception as e:
    print(f"Error writing data to SharePoint: {e}")