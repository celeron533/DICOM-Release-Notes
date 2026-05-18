import os
import json
from dataclasses import dataclass
from typing import List
from lxml import etree
import pandas as pd
from settings import NAMESPACES, DOWNLOADED_DIR, EXTRACTED_DIR

@dataclass
class IDsInParts:
    version: str
    part: str
    id: str
    name: str
    alt: str = ""

    def to_dict(self):
        return {
            'version': self.version,
            'part': self.part,
            'id': self.id,
            'name': self.name,
            'alt': self.alt
        }

@dataclass
class IDDetails:
    id: str
    name: str
    link: str
    description: str
    filename_pdf: str = ""

    def __post_init__(self):
        if self.link:
            self.filename_pdf = self.link.rsplit('/', 1)[-1]
            if not self.filename_pdf.lower().endswith('.pdf'):
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
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    if isinstance(data, pd.DataFrame):
        new_data = data.to_dict(orient='records')
    else:
        new_data = data

    existing_data.extend(new_data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {filename}")

def extract_changes_of_parts(version_str: str, section_change_of_parts) -> List[IDsInParts]:
    ids_in_parts: List[IDsInParts] = []
    if not section_change_of_parts:
        return ids_in_parts
    
    parts = section_change_of_parts[0].xpath('./db:section', namespaces=NAMESPACES)
    for part in parts:
        part_title = part.xpath('./db:title/text()', namespaces=NAMESPACES)
        if not part_title or not part_title[0]:
            print("Part title not found.")
            continue
        
        paras = part.xpath('./db:itemizedlist/db:listitem/db:para', namespaces=NAMESPACES)
        for para in paras:
            text = para.text.strip() if para.text else ""

            link = para.xpath('./db:link', namespaces=NAMESPACES)
            link_text = link[0].text.strip() if link and link[0].text else ""

            linkend = para.xpath('./db:link/@linkend', namespaces=NAMESPACES)
            linkend_val = linkend[0].strip() if linkend else ""

            if (link_text and linkend_val) or text:
                data = IDsInParts(version_str, part_title[0], linkend_val, link_text, text)
                ids_in_parts.append(data)
    return ids_in_parts

def extract_varlistentry(section_cp_or_supp) -> List[IDDetails]:
    id_details: List[IDDetails] = []
    if not section_cp_or_supp:
        print("No 'Supplements Incorporated' or 'Correction Items Incorporated' section found.")
        return id_details
    
    section = section_cp_or_supp[0]
    entries = section.xpath('./db:variablelist/db:varlistentry', namespaces=NAMESPACES)
    
    for entry in entries:
        xml_id = entry.xpath('./@xml:id', namespaces=NAMESPACES)
        xml_id_val = xml_id[0].strip() if xml_id else ""

        link = entry.xpath('./db:term/db:link[1]', namespaces=NAMESPACES)
        link_text = ""
        link_href = ""
        if link:
            link_text = link[0].text.strip() if link[0].text else ""
            link_href_list = link[0].xpath('./@xl:href', namespaces=NAMESPACES)
            link_href = link_href_list[0].strip() if link_href_list else ""

        paras = entry.xpath('.//db:para', namespaces=NAMESPACES)
        text = ""
        for para in paras:
            text += para.text.strip().replace('\r', ' ').replace('\n', ' ') if para.text else ""

        if xml_id_val and link_text and text:
            data = IDDetails(xml_id_val, link_text, link_href, text)
            id_details.append(data)
    return id_details

def extract_release_info(file_path: str):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
        
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()
 
    version = ""
    title_elements = root.xpath('/db:book/db:title[1]', namespaces=NAMESPACES)
    if title_elements and title_elements[0].text:
        title = title_elements[0].text.strip()
        version = title.split()[-1] if len(title.split()) > 1 else ""
        print(f"Extracted version: {version} from title: {title}")

    changes = root.xpath('/db:book/db:chapter/db:section[db:title="Changes to Parts"]', namespaces=NAMESPACES)
    changes_of_parts_result = extract_changes_of_parts(version, changes)
    changes_of_parts_df = pd.DataFrame([entry.to_dict() for entry in changes_of_parts_result])
    
    sups = root.xpath('/db:book/db:chapter/db:section[db:title="Supplements Incorporated"]', namespaces=NAMESPACES)
    supplements_incorporated_result = extract_varlistentry(sups)
    supplements_incorporated_df = pd.DataFrame([entry.to_dict() for entry in supplements_incorporated_result])
    
    cps = root.xpath('/db:book/db:chapter/db:section[db:title="Correction Items Incorporated"]', namespaces=NAMESPACES)
    correction_items_incorporated_result = extract_varlistentry(cps)
    correction_items_incorporated_df = pd.DataFrame([entry.to_dict() for entry in correction_items_incorporated_result])

    os.makedirs(EXTRACTED_DIR, exist_ok=True)
        
    if not changes_of_parts_df.empty:
        change_of_parts_json_file = os.path.join(EXTRACTED_DIR, "change_of_parts.json")
        append_to_json(changes_of_parts_df, change_of_parts_json_file)

    if not supplements_incorporated_df.empty:
        supplements_incorporated_json_file = os.path.join(EXTRACTED_DIR, "supplements_incorporated.json")
        append_to_json(supplements_incorporated_df, supplements_incorporated_json_file)

    if not correction_items_incorporated_df.empty:
        correction_items_incorporated_json_file = os.path.join(EXTRACTED_DIR, "correction_items_incorporated.json")
        append_to_json(correction_items_incorporated_df, correction_items_incorporated_json_file)

def walk_directory(directory: str):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml') and file.startswith('releasenotes_'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")
                extract_release_info(file_path)

def extract_release_notes():
    walk_directory(DOWNLOADED_DIR)

if __name__ == "__main__":
    extract_release_notes()
    print("Release notes extraction completed.")