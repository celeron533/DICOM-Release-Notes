import os
import json
import pandas as pd
from settings import (
    CHANGE_OF_PARTS_FILE,
    SUPPLEMENTS_INCORPORATED_FILE,
    CORRECTION_ITEMS_INCORPORATED_FILE,
    DOCUMENT_LIST_FILE,
    CONSOLIDATED_FILE,
    CONSOLIDATED_INFO_FILE
)

def grouped_changes_of_parts(changes_of_parts_df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = changes_of_parts_df[
        changes_of_parts_df['id'].notna() & (changes_of_parts_df['id'] != '')
    ]
    
    grouped = filtered_df.groupby(['version', 'id'])['part'].agg(list).reset_index()
    
    result = grouped.groupby('version').apply(
        lambda x: x[['id', 'part']].rename(columns={'part': 'parts'}).to_dict('records')
    ).reset_index(name='ids')
    
    return result

def process():
    json_files = {
        'changes': CHANGE_OF_PARTS_FILE,
        'supplements': SUPPLEMENTS_INCORPORATED_FILE,
        'corrections': CORRECTION_ITEMS_INCORPORATED_FILE,
        'documents': DOCUMENT_LIST_FILE
    }
    
    for name, path in json_files.items():
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing required file: {path}")
    
    supplements_incorporated_df = pd.read_json(SUPPLEMENTS_INCORPORATED_FILE)
    correction_items_incorporated_df = pd.read_json(CORRECTION_ITEMS_INCORPORATED_FILE)
    changes_of_parts_df = pd.read_json(CHANGE_OF_PARTS_FILE)
    document_list_df = pd.read_json(DOCUMENT_LIST_FILE)
    
    grouped_changes_of_parts_df = grouped_changes_of_parts(changes_of_parts_df)
    id_details_combined_df = pd.concat([supplements_incorporated_df, correction_items_incorporated_df], ignore_index=True)

    id_to_name_description = {row['id']: (row['name'], row['description']) 
                           for _, row in id_details_combined_df[['id', 'name', 'description']].iterrows()}
    id_to_document_list = {row['doc_id']: [file['name'] for file in row['files']] 
                           for _, row in document_list_df.iterrows()}

    def enrich_ids(ids_list):
        for id_obj in ids_list:
            id_val = id_obj['id']
            details = id_to_name_description.get(id_val)
            if details:
                id_obj['name'], id_obj['description'] = details
            else:
                id_obj['name'], id_obj['description'] = 'Unknown', 'No description available'
            id_obj['files'] = id_to_document_list.get(id_val, [])
        return ids_list

    grouped_changes_of_parts_df['ids'] = grouped_changes_of_parts_df['ids'].apply(enrich_ids)
    consolidated_df = grouped_changes_of_parts_df

    os.makedirs(os.path.dirname(CONSOLIDATED_FILE), exist_ok=True)
    consolidated_df.to_json(CONSOLIDATED_FILE, orient='records', force_ascii=False, indent=2)
    print(f"Consolidated data saved to {CONSOLIDATED_FILE}")

    consolidated_info = {
        "generated_at": pd.Timestamp.utcnow().isoformat(),
        "versions": consolidated_df['version'].tolist()
    }
    
    with open(CONSOLIDATED_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(consolidated_info, f, ensure_ascii=False, indent=2)
    print(f"Consolidated info saved to {CONSOLIDATED_INFO_FILE}")

if __name__ == "__main__":
    process()
    print("Post processing completed.")