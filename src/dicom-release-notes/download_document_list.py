import requests
from settings import DICOM_FINAL_URL, DOWNLOADED_DIR, FINAL_HTML_FILE, REQUEST_TIMEOUT

def download_document_list():
    import os
    os.makedirs(DOWNLOADED_DIR, exist_ok=True)
    
    try:
        response = requests.get(DICOM_FINAL_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        with open(FINAL_HTML_FILE, "wb") as f:
            f.write(response.content)
        
        print(f"Downloaded HTML content from {DICOM_FINAL_URL} to {FINAL_HTML_FILE}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download document list: {e}")
        raise

if __name__ == "__main__":
    download_document_list()
    print("Document list download completed.")