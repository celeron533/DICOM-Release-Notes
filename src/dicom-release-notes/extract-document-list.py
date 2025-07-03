import os
from lxml import html
import pandas as pd

file_path = "downloads/final.html"
with open(file_path, "rb") as f:
    content = f.read()

tree = html.fromstring(content)
docs = []
for link in tree.xpath("/html/body/pre/a"):
    href = link.get("href")
    if href and href != "../":
        text = link.text_content()
        if "To Parent Directory" in text:
            continue
        docs.append((text, href))

#convert the list of tuples to pandas DataFrame
folders_df = pd.DataFrame(docs, columns=["name", "link"])
#remove the rows that name not start with 'cp' or 'sup'
folders_df = folders_df[folders_df['name'].str.startswith(('cp', 'sup'))]
# extract doc_id as "cp_012" or "sup_123" from the filename
folders_df['doc_id'] = folders_df['name'].str.extract(
    r'^(cp|sup)[-_]?(\d+)', expand=True
    ).agg('_'.join, axis=1)
# group by the doc_id and the files are the names and corresponding links
folders_df = folders_df.groupby('doc_id').apply(
    lambda x: x[['name', 'link']].to_dict(orient='records'),
    include_groups=False
).reset_index(name='files')

#print(f">> Links found: \n{folders_df}")

# Save the DataFrame to a json file
output_file = "data/extracted/document_list.json"
if not os.path.exists("data/extracted"):
    os.makedirs("data/extracted")
folders_df.to_json(output_file, orient='records', force_ascii=False, indent=2)
print(f"Document list saved to {output_file}")