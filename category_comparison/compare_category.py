from presentation.definer import define_fields, define_category
from presentation.extractor import extract_fields
from presentation.pdf_extractor import extract_text_from_pdf

import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
import json

def split_categories(categories_str: str) -> list[str]:
    if not categories_str or not categories_str.strip():
        return []

    categories = [cat.strip() for cat in categories_str.split(';')]

    categories = [cat[:-1] if cat and cat.endswith('.') else cat for cat in categories]

    return [cat for cat in categories if cat]

def get_categories(text):

    # text = extract_text_from_pdf(appeal_path)

    fields = define_fields(text)
    # print(fields)

    extracted_fields = extract_fields(fields)
    # print(extracted_fields["текст_обращения"])

    return split_categories(define_category(extracted_fields["текст_обращения"]))
    # print(categories)

def extract_xml_data_from_folder(folder_path: str, max_files: int = None) -> List[Tuple[Optional[str], Optional[str]]]:

    results = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Папка {folder_path} не существует")

    xml_files = [f for f in os.listdir(folder_path) if f.endswith('.xml')]

    if max_files is not None:
        xml_files = xml_files[:max_files]

    for i, filename in enumerate(xml_files, 1):
        file_path = os.path.join(folder_path, filename)

        try:
            contract_ref, name_value = extract_data_from_xml(file_path)
            results.append((contract_ref.lower(), name_value.split(' ', 1)[1]))

        except Exception as e:
            print(f"  ✗ Ошибка при обработке {filename}: {e}")
            # results.append((None, None))

    return results

def extract_data_from_xml(file_path: str) -> Tuple[Optional[str], Optional[str]]:
    # Парсим XML файл
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Ищем ContractRef в теге Contract
    contract_ref = None
    for contract in root.findall('.//Contract'):
        contract_ref = contract.get('ContractRef')
        if contract_ref:
            break

    # Ищем Name в теге ItemsRow
    name_value = None
    for items_row in root.findall('.//ItemsRow'):
        name_value = items_row.get('Name')
        if name_value and name_value.startswith('0003.'):
            break

    return contract_ref, name_value

def load_appeals_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def count_matching_categories(extracted_pairs, appeals_json_path, output_file = "comparison_res.txt"):
    # Загружаем все обращения из JSON
    appeals_data = load_appeals_data(appeals_json_path)

    # Создаем словарь для быстрого поиска обращения по id
    # Ключ: id документа, Значение: текст документа
    appeals_dict = {}
    for doc in appeals_data.get('documents', []):
        appeals_dict[doc['id']] = doc['text']

    appeals_counter = 0
    match_count = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        for contract_ref, true_category in extracted_pairs:

            # Ищем обращение по contract_ref (который является id в JSON)
            appeal_text = appeals_dict.get(contract_ref)

            if appeal_text is not None:
                appeals_counter += 1

                predicted_categories = get_categories(appeal_text)

                if true_category in predicted_categories:
                    match_count += 1
                    f.write(f"Совпадение для ID {contract_ref}: '{true_category}' НАЙДЕНА в {predicted_categories}\n")
                else:
                    f.write(f"Совпадение для ID {contract_ref}: '{true_category}' НЕ НАЙДЕНА в {predicted_categories}\n")
            else:
                f.write(f"Обращение с ID {contract_ref} не найдено в JSON файле.\n")

        f.write(f"\n=== ИТОГИ ===\n")
        f.write(f"Всего обработано пар: {len(extracted_pairs)}\n")
        f.write(f"Найдено обращений: {appeals_counter}\n")
        f.write(f"Совпадений категорий: {match_count}\n")
        f.write(f"Точность: {match_count/appeals_counter*100:.2f}%\n")
    # return match_count

folder_path = "D:/Обращения/Обращения январь 2025/Questions"
json_file_path = "/jsons_with_info/appeals_texts.json"

extracted_cats = extract_xml_data_from_folder(folder_path, max_files=12)
count_matching_categories(extracted_cats, json_file_path)

