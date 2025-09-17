#ЗДЕСЬ БУДЕТ ТЕСТ НАШЕЙ МОДЕЛИ
from presentation.definer import define_fields, define_category
from presentation.extractor import extract_fields
from presentation.pdf_extractor import extract_text_from_pdf

import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
import re
import json

penis  = "Городской, сельский и междугородний пассажирский транспорт; Транспортное обслуживание населения, пассажирские перевозки; Тарифы, сборы и льготы на транспортные услуги."

def split_categories(categories_str: str) -> list[str]:
    if not categories_str or not categories_str.strip():
        return []

    newstr = categories_str.replace(".", "")

    text = newstr.split('; ')

    return text

print(split_categories(penis))

def get_categories(text):

    fields = define_fields(text)

    extracted_fields = extract_fields(fields)

    return split_categories(define_category(extracted_fields["текст_обращения"]))

with open('../jsons_with_info/full_dataset.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

file = open('example.txt', 'w', encoding='utf-8')

counter = 0

i = 0

for appeals in data["documents"]:
    i += 1
    categories_from_LLM = get_categories(appeals["text"])
    categories_from_human = appeals["categories"]
    common_elements = set(categories_from_LLM) & set(categories_from_human)
    if common_elements != []:
        print(common_elements)
        file.write("Категории, которые выдала LLM: " + str(categories_from_LLM) + "\n")
        file.write("Категории, которые определил хьюман: " + str(categories_from_human) + "\n")
        counter += 1
    else:
        file.write('У LLMки проблемы с этим файлом: ' + appeals['id'] + '\n')

    if i > 1:
        break

file.write('ИТОГО: ' + str(counter) + ' БЫЛО ОПРЕДЕЛЕНО ПРАВИЛЬНО')

