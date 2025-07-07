import os
from lxml import etree
import pandas as pd
# python 3.9+ supports list[str] as well, but we use List for compatibility with earlier versions.
from typing import List
import json

ns = {
    'db': 'http://docbook.org/ns/docbook',
    'xhtml': 'http://www.w3.org/1999/xhtml',
    'xl': 'http://www.w3.org/1999/xlink'
}

class IDsInParts:
    version: str
    part: str
    id: str
    name: str
    alt: str
    def __init__ (self, version, part, id, name, alt):
        self.version = version
        self.part = part
        self.id = id
        self.name = name
        self.alt = alt # this is only available when there is no id nor no name. Not used in the current code.

    def to_dict(self):
        return {
            'version': self.version,
            'part': self.part,
            'id': self.id,
            'name': self.name,
            'alt': self.alt
        }

class IDDetails:
    id: str
    name: str
    link: str
    filename_pdf: str
    description: str
    def __init__(self, id, name, link, description):
        self.id = id
        self.name = name
        self.link = link
        self.description = description
        # only get the part after the last slash
        self.filename_pdf = link.rsplit('/', 1)[-1] if link else ""
        # check if the file name is end with .pdf, if not, add .pdf to the end of the link
        if self.filename_pdf and not self.filename_pdf.lower().endswith('.pdf'):
            self.filename_pdf += '.pdf'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'link': self.link,
            'filename_pdf': self.filename_pdf,
            'description': self.description
        }


def append_to_json(data, filename):
    # Load existing data if file exists
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Append new data
    if isinstance(data, pd.DataFrame):
        new_data = data.to_dict(orient='records')
    else:
        new_data = data

    existing_data.extend(new_data)

    # Write back to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {filename}")


def extract_changes_of_parts(version_str, section_change_of_parts) -> list[IDsInParts]:
    ids_in_parts: list[IDsInParts] = []
    parts = section_change_of_parts[0].xpath('./db:section', namespaces=ns)
    for part in parts:
        part_title = part.xpath('./db:title/text()', namespaces=ns)
        if part_title and part_title[0]:
            # print(f"Part: {part_title[0]}")
            pass
        else:
            print("Part title not found.")
            continue
        
        paras = part.xpath('./db:itemizedlist/db:listitem/db:para', namespaces=ns)
        for para in paras:
            text = para.text.strip() if para.text else ""

            link = para.xpath('./db:link', namespaces=ns)
            if link:
                link = link[0].text.strip() if link[0].text else ""
            else:
                link = ""

            linkend = para.xpath('./db:link/@linkend', namespaces=ns)
            if linkend:
                linkend = linkend[0].strip()
            else:
                linkend = ""

            if (link and linkend) or text:
            # if (link and linkend): # we don't need alt text for IDsInParts
                # create an IDsInParts object
                data = IDsInParts(version_str, part_title[0], linkend, link, text)
                # print(f"  IDs in parts: Version: {version_str}, Part: {data.part}, ID: {data.id}, Name: {data.name}, Alt: {data.alt}")
                ids_in_parts.append(data)
    return ids_in_parts



def extract_varlistentry(section_cp_or_supp) -> list[IDDetails]:
    id_details: list[IDDetails] = []
    section_cp_or_supp = section_cp_or_supp[0] if section_cp_or_supp else None
    if section_cp_or_supp is None:
        print("No 'Supplements Incorporated' or 'Correction Items Incorporated' section found.")
        return
    entries = section_cp_or_supp.xpath('./db:variablelist/db:varlistentry', namespaces=ns)
    for entry in entries:
        xml_id = entry.xpath('./@xml:id', namespaces=ns)
        if xml_id:
            xml_id = xml_id[0].strip()
            # print(f" XML ID: {xml_id}")
        else:
            xml_id = ""
            print("  XML ID not found.")

        #get link:
        link = entry.xpath('./db:term/db:link[1]', namespaces=ns)
        if link:
            link_text = link[0].text.strip() if link[0].text else ""
            # print(f"  Link: {link_text}")   #"CP 2326" or "SUP 2326"
            link_href = link[0].xpath('./@xl:href', namespaces=ns)
            if link_href:
                link_href = link_href[0].strip()
                # print(f"  Link HREF: {link_href}")
        
        paras = entry.xpath('.//db:para', namespaces=ns)
        text = ""
        for para in paras:
            text += para.text.strip().replace('\r', ' ').replace('\n', ' ') if para.text else ""
            # print(f"  Para: {text}")
        if xml_id and link_text and text:
            # create an IDDetails object
            data = IDDetails(xml_id, link_text, link_href, text)
            # print(f"  ID Details: ID: {data.id}, Name: {data.name}, Link: {data.link}, Description: {data.description}, filename_pdf: {data.filename_pdf}")
            id_details.append(data)
    return id_details
        

def extract_release_info(file_path):
    """
    Extracts release information from a DICOM release notes XML file.
    
    Args:
        file_path (str): Path to the XML file.
        
    Returns:
        TBD
    """
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
        
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()
 
    version = ""
    # 1. extract <book><title>DICOM PS3 2023d</title>...</book>
    title_elements = root.xpath('/db:book/db:title[1]', namespaces=ns)
    if not title_elements or title_elements[0].text is None:
        title = ""
    else:
        title = title_elements[0].text.strip()
        version = title.split()[-1] if len(title.split()) > 1 else ""
        print(f"Extracted version: {version} from title: {title}")

    # 2. extract <chapter><section><title>"Changes to Parts" elements
    changes = root.xpath('/db:book/db:chapter/db:section[db:title="Changes to Parts"]', namespaces=ns)
    changes_of_parts_result = extract_changes_of_parts(version, changes)
    changes_of_parts_df = pd.DataFrame([entry.to_dict() for entry in changes_of_parts_result])
    
    # 3. extract <chapter><section><title>"Supplements Incorporated" elements
    sups = root.xpath('/db:book/db:chapter/db:section[db:title="Supplements Incorporated"]', namespaces=ns)
    supplements_incorporated_result = extract_varlistentry(sups)
    supplements_incorporated_df = pd.DataFrame([entry.to_dict() for entry in supplements_incorporated_result])
    
    # 4. extract <chapter><section><title>"Correction Items Incorporated" elements
    cps = root.xpath('/db:book/db:chapter/db:section[db:title="Correction Items Incorporated"]', namespaces=ns)
    correction_items_incorporated_result = extract_varlistentry(cps)
    correction_items_incorporated_df = pd.DataFrame([entry.to_dict() for entry in correction_items_incorporated_result])

    # write the dataframes to json files
    if os.path.exists("data/extracted") is False:
        os.makedirs("data/extracted")
        
    if not changes_of_parts_df.empty:
        change_of_parts_json_file = f"data/extracted/change_of_parts.json"
        append_to_json(changes_of_parts_df, change_of_parts_json_file)

    if not supplements_incorporated_df.empty:
        supplements_incorporated_json_file = f"data/extracted/supplements_incorporated.json"
        append_to_json(supplements_incorporated_df, supplements_incorporated_json_file)

    if not correction_items_incorporated_df.empty:
        correction_items_incorporated_json_file = f"data/extracted/correction_items_incorporated.json"
        append_to_json(correction_items_incorporated_df, correction_items_incorporated_json_file)


def walk_directory(directory):
    """
    Walks through the directory and processes XML files.
    
    Args:
        directory (str): Path to the directory.
    """
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml') and file.startswith('releasenotes_'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                extract_release_info(file_path)

if __name__ == "__main__":
    walk_directory("downloaded")