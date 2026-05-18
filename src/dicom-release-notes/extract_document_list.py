import os
from lxml import html
import pandas as pd
from settings import FINAL_HTML_FILE, DOCUMENT_LIST_FILE

def extract_document_list():
    if not os.path.exists(FINAL_HTML_FILE):
        raise FileNotFoundError(f"Input file not found: {FINAL_HTML_FILE}")
    
    with open(FINAL_HTML_FILE, "rb") as f:
        content = f.read()
    
    tree = html.fromstring(content)
    docs = []
    
    for link in tree.xpath("/html/body/pre/a"):
        href = link.get("href")
        if href and href != "../":
            text = link.text_content()
            if "To Parent Directory" in text:
                continue
            docs.append({"name": text, "link": href})
    
    if not docs:
        print("No documents found.")
        return
    
    folders_df = pd.DataFrame(docs)
    folders_df = folders_df[folders_df['name'].str.startswith(('cp', 'sup'))]
    
    folders_df['doc_id'] = folders_df['name'].str.extract(
        r'^(cp|sup)[-_]?(\d+)', expand=True
    ).agg('_'.join, axis=1)
    
    folders_df = folders_df.groupby('doc_id').apply(
        lambda x: x[['name', 'link']].to_dict(orient='records'),
        include_groups=False
    ).reset_index(name='files')
    
    os.makedirs(os.path.dirname(DOCUMENT_LIST_FILE), exist_ok=True)
    folders_df.to_json(DOCUMENT_LIST_FILE, orient='records', force_ascii=False, indent=2)
    print(f"Document list saved to {DOCUMENT_LIST_FILE}")

if __name__ == "__main__":
    extract_document_list()
    print("Document list extraction completed.")