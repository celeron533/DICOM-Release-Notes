import requests
import os
from lxml import etree
from lxml import html

url = "https://dicom.nema.org/medical/dicom/"
response = requests.get(url)

tree = html.fromstring(response.content)
folders = []
for link in tree.xpath("//a"):
    href = link.get("href")
    if href and href.endswith("/") and href != "../":
        folder_name = link.text_content()
        folders.append((folder_name, href))

print(folders)

# only keep folders that start with 4 digits
release_folders = [f for f in folders if f[0][:4].isdigit()]
print(release_folders)
# filter the folders that the year part is 2014 or older.
# the earlier versions are not well organized.
release_folders = [f for f in release_folders if int(f[0][:4]) >= 2014]
print(release_folders)

# download the release notes
# url looks like this:
# https://dicom.nema.org/medical/dicom/2024d/source/docbook/releasenotes/releasenotes_2024d.xml
for folder_name, href in release_folders:
    year = folder_name[:4]
    version = folder_name[4:]
    download_url = f"{url}{folder_name}/source/docbook/releasenotes/releasenotes_{folder_name}.xml"

    print(f"Downloading {download_url}...")
    #download the file to the downloads folder
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    # skip if the file already exists
    if os.path.exists(f"downloads/releasenotes_{folder_name}.xml"):
        print(f"File for {folder_name} already exists, skipping download.")
        continue
    response = requests.get(download_url)

    if response.status_code == 200:
        with open(f"downloads/releasenotes_{folder_name}.xml", "wb") as file:
            file.write(response.content)
        print(f"Downloaded {folder_name} release notes successfully.")
    else:
        print(f"Failed to download {folder_name} release notes. Status code: {response.status_code}")

# all downloaded.
# start processing the xml files.
for folder_name, href in release_folders:
    year = folder_name[:4]
    version = folder_name[4:]
    file_path = f"downloads/releasenotes_{folder_name}.xml"

    if os.path.exists(file_path):
        print(f"Processing {file_path}...")
        # use bs4, find a <section> who has a sub tag <title> with text "Changes to Parts"
        with open(file_path, "r", encoding="utf-8") as file:
            # Read the XML content by lxml
            xml_content = file.read()
            xml_tree = etree.fromstring(xml_content.encode('utf-8'))
            ns = {
                'db': 'http://docbook.org/ns/docbook',
                'xhtml': 'http://www.w3.org/1999/xhtml',
                'xl': 'http://www.w3.org/1999/xlink'
            }
            # find the section with child xml tag title "Changes to Parts"
            changes_section = xml_tree.xpath("//db:section[db:title[text()='Changes to Parts']]",namespaces=ns)
            print(changes_section)
    else:
        print(f"File {file_path} does not exist, skipping processing.")