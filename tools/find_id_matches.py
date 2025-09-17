import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
import json
import re

def extract_data_from_xml(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    tree = ET.parse(file_path)
    root = tree.getroot()
    pattern = r'\b\d{4}(?:\.\d{4})+\b'

    contract_ref = None
    for contract in root.findall('.//Contract'):
        contract_ref = contract.get('ContractRef')
        if contract_ref:
            break

    name_value = None
    for items_row in root.findall('.//ItemsRow'):
        name_value = items_row.get('Name')
        if name_value and re.match(pattern, name_value):
            break

    return str(contract_ref), name_value

ids = set([])

with open('../jsons_with_info/appeals_texts.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

for docs in data["documents"]:
    ids.add(docs["id"])

id_to_category = {}

for root, dirs, files in os.walk(r'D:\Обращения\Обращения январь 2025\Questions'):
    for name in files:
        ref, category = extract_data_from_xml(root + "\\" + name)
        ref = ref.lower()
        if (ref in ids):
            if ref not in id_to_category:
                id_to_category[ref] = []
            id_to_category[ref].append(category)

for document in data.get('documents'):
    document_id = document.get('id')
    if document_id in id_to_category:
        document['categories'] = id_to_category[document_id]

with open('../jsons_with_info/full_dataset.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
