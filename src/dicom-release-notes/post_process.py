import os
import pandas as pd
# python 3.9+ supports list[str] as well, but we use List for compatibility with earlier versions.
from typing import List


change_of_parts_json_file = f"data/extracted/change_of_parts.json"
supplements_incorporated_json_file = f"data/extracted/supplements_incorporated.json"
correction_items_incorporated_json_file = f"data/extracted/correction_items_incorporated.json"
document_list_json_file = f"data/extracted/document_list.json"


def grouped_changes_of_parts(changes_of_parts_df: pd.DataFrame) -> pd.DataFrame:
    # Exclude rows where 'id' is blank string or null
    filtered_df = changes_of_parts_df[changes_of_parts_df['id'].notna() & (changes_of_parts_df['id'] != '')]

    # Group by 'version' and 'id', aggregate 'part' into lists
    grouped = filtered_df.groupby(['version', 'id'])['part'].apply(list).reset_index()

    # Now group by 'version', aggregate 'id' and 'part' into desired structure
    result = (
        grouped.groupby('version')[['id','part']]
        .apply(
            lambda df: [
                {'id': row['id'], 'parts': row['part']}
                for _, row in df.iterrows()
            ])
        .reset_index(name='ids')
    )

    # result.to_json('grouped_changes_of_parts.json', orient='records', force_ascii=False, indent=2)

    return result

def process():
    supplements_incorporated_df = pd.read_json(supplements_incorporated_json_file)
    correction_items_incorporated_df = pd.read_json(correction_items_incorporated_json_file)
    grouped_changes_of_parts_df = grouped_changes_of_parts(pd.read_json(change_of_parts_json_file))
    document_list_df = pd.read_json(document_list_json_file)

    id_details_combined_df = pd.concat([supplements_incorporated_df, correction_items_incorporated_df], ignore_index=True)

    # Create mappings from id to (name, description),(files) for quick lookup
    id_to_name_description = {row['id']: (row['name'], row['description']) for _, row in id_details_combined_df.iterrows()}
    id_to_document_list = {row['doc_id']: [file['name'] for file in row['files']] for _, row in document_list_df.iterrows()}

    # Add description and name to each id object in grouped_changes
    for idx, version_entry in grouped_changes_of_parts_df.iterrows():
        for id_obj in version_entry['ids']:
            id_val = id_obj['id']
            # Add name and description from mapping, or defaults if not found
            id_obj['name'], id_obj['description'] = id_to_name_description.get(id_val, ('Unknown', 'No description available'))
            # Add document list from mapping, or empty list if not found
            id_obj['files'] = id_to_document_list.get(id_val, [])

    # Convert back to DataFrame for further processing or saving
    consolidated_df = pd.DataFrame(grouped_changes_of_parts_df)
   
    consolidated_json_file = f"data/consolidated.json"

    consolidated_df.to_json(consolidated_json_file, orient='records', force_ascii=False, indent=2)

    print(f"Consolidated data saved to {consolidated_json_file}")

    # create a new json file, contains the consolidated data generated time
    consolidated_info = {
        "generated_at": pd.Timestamp.now().isoformat(),
    }
    # save the consolidated info to a new json file
    consolidated_info_file = f"data/consolidated_info.json"
    with open(consolidated_info_file, 'w', encoding='utf-8') as f:
        pd.Series(consolidated_info).to_json(f, force_ascii=False, indent=2)

if __name__ == "__main__":
    process()
    print("Post processing completed.")