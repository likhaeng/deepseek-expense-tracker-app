# Python Library
import logging
import os 
# Custom Library
from util_sharepoint import SharePointUtil
from util_chroma_db import ChromaDb
import config

logging.basicConfig(format='%(asctime)s %(message)s', filename=config.log_path, level = config.log_level)
class AutomationFileToChroma():
    def __init__(self):
        self.chromaUtil = ChromaDb()
        self.sharepointUtil = SharePointUtil()

    def main(self):
        logging.warning("Automation Step 1 Start: Download File From SharePoint")
        self.sharepointUtil.downloadFileByFolder()
        logging.warning("Automation Step 1 End: Download File From SharePoint")

        logging.warning("Automation Step 2 Start: Process File to Chroma")
        self.chromaUtil.processFileToChroma()
        logging.warning("Automation Step 2 End: Process File to Chroma")

        logging.warning("Automation Step 3 Start: Archive File to Archived Folder")
        self.chromaUtil.archiveFile()
        logging.warning("Automation Step 3 End: Archive File to Archived Folder")


if __name__ == "__main__":
    automation = AutomationFileToChroma()
    automation.main()