import os
import requests
from lxml import html
from settings import DICOM_BASE_URL, DOWNLOADED_DIR, REQUEST_TIMEOUT

def download_file(download_url, folder_name):
    print(f"Downloading {download_url}...")
    file_path = os.path.join(DOWNLOADED_DIR, f"releasenotes_{folder_name}.xml")
    
    if os.path.exists(file_path):
        print(f"File for {folder_name} already exists, skipping download.")
        return
    
    try:
        response = requests.get(download_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        with open(file_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {folder_name} release notes successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {folder_name} release notes: {e}")
        raise

def download_release_notes():
    os.makedirs(DOWNLOADED_DIR, exist_ok=True)
    
    try:
        response = requests.get(DICOM_BASE_URL, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        folders = []
        for link in tree.xpath("//a"):
            href = link.get("href")
            if href and href.endswith("/") and href != "../":
                folder_name = link.text_content()
                folders.append((folder_name, href))
        
        print(f">> Links found: {folders}")
        
        release_folders = [f for f in folders if f[0][:4].isdigit()]
        release_folders = [f for f in release_folders if int(f[0][:4]) >= 2014]
        print(f">> Links to be downloaded: {release_folders}")
        
        for folder_name, href in release_folders:
            download_url = f"{DICOM_BASE_URL}{folder_name}/source/docbook/releasenotes/releasenotes_{folder_name}.xml"
            download_file(download_url, folder_name)
        
        folder = f"{DICOM_BASE_URL}current/source/docbook/releasenotes"
        response = requests.get(folder, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        latest_version_link = tree.xpath("//a[contains(@href, 'releasenotes_')]/@href")
        
        if latest_version_link:
            download_url = latest_version_link[0]
            version = download_url.split('_')[-1].split('.')[0]
            print(f"Latest version found: {version}")
            download_file(f"https://dicom.nema.org/{download_url}", version)
        else:
            print("No current release notes found.")
        
        print("All release notes downloaded.")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download release notes: {e}")
        raise

if __name__ == "__main__":
    download_release_notes()
    print("Release notes download completed.")