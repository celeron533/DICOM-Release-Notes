import os

# Base directories
DOWNLOADED_DIR = "downloaded"
DATA_DIR = "data"
EXTRACTED_DIR = os.path.join(DATA_DIR, "extracted")

# URLs
DICOM_BASE_URL = "https://dicom.nema.org/medical/dicom/"
DICOM_FINAL_URL = "https://dicom.nema.org/medical/dicom/final"

# Timeout settings
REQUEST_TIMEOUT = 30

# Namespaces
NAMESPACES = {
    'db': 'http://docbook.org/ns/docbook',
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'xl': 'http://www.w3.org/1999/xlink'
}

# File paths
FINAL_HTML_FILE = os.path.join(DOWNLOADED_DIR, "final.html")
CHANGE_OF_PARTS_FILE = os.path.join(EXTRACTED_DIR, "change_of_parts.json")
SUPPLEMENTS_INCORPORATED_FILE = os.path.join(EXTRACTED_DIR, "supplements_incorporated.json")
CORRECTION_ITEMS_INCORPORATED_FILE = os.path.join(EXTRACTED_DIR, "correction_items_incorporated.json")
DOCUMENT_LIST_FILE = os.path.join(EXTRACTED_DIR, "document_list.json")
CONSOLIDATED_FILE = os.path.join(DATA_DIR, "consolidated.json")
CONSOLIDATED_INFO_FILE = os.path.join(DATA_DIR, "consolidated_info.json")