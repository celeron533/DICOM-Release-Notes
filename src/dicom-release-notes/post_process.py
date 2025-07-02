import os
import pandas as pd
# python 3.9+ supports list[str] as well, but we use List for compatibility with earlier versions.
from typing import List
import json


change_of_parts_json_file = f"data/extracted/change_of_parts.json"
supplements_incorporated_json_file = f"data/extracted/supplements_incorporated.json"
correction_items_incorporated_json_file = f"data/extracted/correction_items_incorporated.json"

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

def process():
    supplements_incorporated_dataframe = pd.read_json(supplements_incorporated_json_file)
    correction_items_incorporated_dataframe = pd.read_json(correction_items_incorporated_json_file)
    changes_of_parts_dataframe = pd.read_json(change_of_parts_json_file)

    # join the dataframes and write to a combined json file
    id_details_combined_dataframe = pd.concat([supplements_incorporated_dataframe, correction_items_incorporated_dataframe], ignore_index=True)
    all_in_one_dataframe = pd.merge(
        changes_of_parts_dataframe[['version', 'part', 'id']],
        id_details_combined_dataframe[['id', 'name', 'filename_pdf', 'description']],
        how='left',
        on='id',
        )
    # Remove rows where 'name' is NaN or empty string
    all_in_one_dataframe = all_in_one_dataframe[all_in_one_dataframe['name'].notna() & (all_in_one_dataframe['name'] != '')]
    # Replace NaN with None to ensure valid JSON output
    all_in_one_dataframe = all_in_one_dataframe.where(pd.notnull(all_in_one_dataframe), None)
   
    all_in_one_json_file = f"data/all_in_one.json"

    append_to_json(all_in_one_dataframe, all_in_one_json_file)

if __name__ == "__main__":
    process()
    print("Post processing completed.")