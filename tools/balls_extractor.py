import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
import json
import re

def extract_data_from_xml(file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    tree = ET.parse(file_path)
    root = tree.getroot()

    email = None
    for contract in root.findall('.//PetitionerInfo'):
        email = contract.get('PetitionerEmail')
        if email:
            break

    name = None
    for items_row in root.findall('.//PetitionerInfo'):
        name = items_row.get('PetitionerName')
        if name:
            break

    surname = None
    for items_row in root.findall('.//PetitionerInfo'):
        surname = items_row.get('PetitionerSurname')
        if surname:
            break

    return email, name, surname

with open('../jsons_with_info/full_dataset.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

pattern = r'\{([^}]*)\}'

for root, dirs, files in os.walk(r'D:\Обращения\balls'):
    for file in files:
        email, name, surname = extract_data_from_xml(root + "\\" + file)
        id = re.findall(pattern, file)[0]
        for doc in data["documents"]:
            if doc["id"] == id:
                doc["email"] = email
                doc["name"] = name
                doc["surname"] = surname

with open('../jsons_with_info/full_dataset.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

