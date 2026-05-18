import os
import requests

BASE_URL = "https://dicom.nema.org/medical/dicom/final"
DOWNLOADED_DIR = "downloaded"
FILENAME = os.path.join(DOWNLOADED_DIR, "final.html")
TIMEOUT = 30

def download_document_list():
    os.makedirs(DOWNLOADED_DIR, exist_ok=True)
    
    try:
        response = requests.get(BASE_URL, timeout=TIMEOUT)
        response.raise_for_status()
        
        with open(FILENAME, "wb") as f:
            f.write(response.content)
        
        print(f"Downloaded HTML content from {BASE_URL} to {FILENAME}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download document list: {e}")
        raise

if __name__ == "__main__":
    download_document_list()
    print("Document list download completed.")