import requests
import os

filename = "downloaded/final.html"

def download_document_list():
    """
    Downloads the HTML content from the DICOM NEMA final document list page.
    """

    if not os.path.exists("downloaded"):
        os.makedirs("downloaded")

    url = "https://dicom.nema.org/medical/dicom/final"
    response = requests.get(url)

    with open(filename, "wb") as f:
        f.write(response.content)

    print(f"Downloaded HTML content from {url} to {filename}")

if __name__ == "__main__":
    download_document_list()
    print("Document list download completed.")