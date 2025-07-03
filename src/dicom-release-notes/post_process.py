import os
import pandas as pd
# python 3.9+ supports list[str] as well, but we use List for compatibility with earlier versions.
from typing import List
import json


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
        grouped.groupby('version')
        .apply(lambda df: [
            {'id': row['id'], 'parts': row['part']}
            for _, row in df.iterrows()
        ])
        .reset_index(name='ids')
    )

    result.to_json('grouped_changes_of_parts.json', orient='records', force_ascii=False, indent=2)

    return result

def process():
    supplements_incorporated_df = pd.read_json(supplements_incorporated_json_file)
    correction_items_incorporated_df = pd.read_json(correction_items_incorporated_json_file)
    grouped_changes_of_parts_df = grouped_changes_of_parts(pd.read_json(change_of_parts_json_file))

    # join the dataframes and write to a combined json file
    id_details_combined_df = pd.concat([supplements_incorporated_df, correction_items_incorporated_df], ignore_index=True)

    # Create mappings from id to description and name for quick lookup
    id_to_description = dict(zip(id_details_combined_df['id'], id_details_combined_df['description']))
    id_to_name = dict(zip(id_details_combined_df['id'], id_details_combined_df['name']))

    # # Iterate each item (row) in grouped_changes_of_parts_df
    # for idx, version_entry in grouped_changes_of_parts_df.iterrows():
    #     print(f"Version: {version_entry['version']}")
    #     for id_obj in version_entry['ids']:
    #         print(f"  ID: {id_obj['id']}, Parts: {id_obj['parts']}")

    # Add description and name to each id object in grouped_changes
    for idx, version_entry in grouped_changes_of_parts_df.iterrows():
        for id_obj in version_entry['ids']:
            id_val = id_obj['id']
            id_obj['description'] = id_to_description.get(id_val, None)
            id_obj['name'] = id_to_name.get(id_val, None)

    # Convert back to DataFrame for further processing or saving
    all_in_one_df = pd.DataFrame(grouped_changes_of_parts_df)
   
    all_in_one_json_file = f"data/all_in_one.json"

    all_in_one_df.to_json(all_in_one_json_file, orient='records', force_ascii=False, indent=2)

if __name__ == "__main__":
    process()
    print("Post processing completed.")