import requests
import os

url = "https://dicom.nema.org/medical/dicom/final"
response = requests.get(url)

with open("downloads/final.html", "wb") as f:
    f.write(response.content)

print(f"Downloaded HTML content from {url} to downloads/final.html")

