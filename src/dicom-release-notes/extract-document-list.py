
import os
from lxml import etree
from lxml import html
import requests

file_path = "downloads/final.html"
with open(file_path, "rb") as f:
    content = f.read()

tree = html.fromstring(content)
folders = []
for link in tree.xpath("/html/body/pre/a"):
    href = link.get("href")
    if href and href != "../":
        folder_name = link.text_content()
        if "To Parent Directory" in folder_name:
            continue
        folders.append((folder_name, href))

print(f">> Links found: {folders}")