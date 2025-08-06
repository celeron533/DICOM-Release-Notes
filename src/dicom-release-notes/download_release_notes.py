import requests
import os
from lxml import etree
from lxml import html

url = "https://dicom.nema.org/medical/dicom/"

def _download_file(download_url, folder_name):
    print(f"Downloading {download_url}...")
    #download the file to the downloaded folder
    # skip if the file already exists
    if os.path.exists(f"downloaded/releasenotes_{folder_name}.xml"):
        print(f"File for {folder_name} already exists, skipping download.")
        return
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(f"downloaded/releasenotes_{folder_name}.xml", "wb") as file:
            file.write(response.content)
        print(f"Downloaded {folder_name} release notes successfully.")
    else:
        print(f"Failed to download {folder_name} release notes. Status code: {response.status_code}")


def download_release_notes():
    """
    Downloads the release notes from the DICOM NEMA website.
    """

    response = requests.get(url)

    tree = html.fromstring(response.content)
    folders = []
    for link in tree.xpath("//a"):
        href = link.get("href")
        if href and href.endswith("/") and href != "../":
            folder_name = link.text_content()
            folders.append((folder_name, href))

    print(f">> Links found: {folders}")

    # only keep folders that start with 4 digits
    release_folders = [f for f in folders if f[0][:4].isdigit()]
    # print(release_folders)
    # filter the folders that the year part is 2014 or older.
    # the earlier versions are not well organized.
    release_folders = [f for f in release_folders if int(f[0][:4]) >= 2014]
    print(f">> Links to be downloaded: {release_folders}")

    if not os.path.exists("downloaded"):
        os.makedirs("downloaded")

    # download the release notes
    # url looks like this:
    # https://dicom.nema.org/medical/dicom/2024d/source/docbook/releasenotes/releasenotes_2024d.xml
    for folder_name, href in release_folders:
        year = folder_name[:4]
        version = folder_name[4:]
        download_url = f"{url}{folder_name}/source/docbook/releasenotes/releasenotes_{folder_name}.xml"
        _download_file(download_url, folder_name)

    # special case for "current" release notes
    # https://dicom.nema.org/medical/dicom/current/source/docbook/releasenotes/releasenotes_2025c.xml
    folder = f"{url}current/source/docbook/releasenotes"
    # parse the HTML to get the latest version
    response = requests.get(folder)
    tree = html.fromstring(response.content)
    latest_version_link = tree.xpath("//a[contains(@href, 'releasenotes_')]/@href")

    if latest_version_link:
        download_url = latest_version_link[0]
        #parse the version from the link
        version = download_url.split('_')[-1].split('.')[0]
        print(f"Latest version found: {version}")
        # download the file
        _download_file(f"https://dicom.nema.org/{download_url}", version)
    else:
        print("No current release notes found.")

    # all downloaded.
    print("All release notes downloaded.")

if __name__ == "__main__":
    download_release_notes()
    print("Release notes download completed.")