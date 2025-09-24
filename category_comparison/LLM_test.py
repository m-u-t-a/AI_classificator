from presentation.definer import define_fields, define_category
from presentation.extractor import extract_fields
from presentation.pdf_extractor import extract_text_from_pdf

import json

penis  = "0003.0009.0104.0000 Городской, сельский и междугородний пассажирский транспорт. Тралала тралала.; 0003.0009.0104.0012 Транспортное обслуживание населения, пассажирские перевозки.; 0002.0009.0104.0000 Тарифы, сборы и льготы на транспортные услуги."
test_text = "Автовокзал Синегорье вызывает недовольство среди уезжающих и гостей Челябинска из-за платного туалета. Человек в тяжёлом состоянии после лечения в онкоцентре не смог воспользоваться туалетом бесплатно, несмотря на предъявление билета, так как доступ предоставляется только за час до отправления. Многие другие также сталкиваются с этой проблемой. Прошу обратить внимание на ситуацию и рассмотреть возможность её решения."
def split_categories(categories_str: str) -> list[str]:
    if not categories_str or not categories_str.strip():
        return []

    print(categories_str)

    text = categories_str.split("; ")

    text = [cat[:-1] if cat and cat.endswith(".") else cat for cat in text]

    return text

def get_categories(appeal_text):

    return split_categories(define_category(appeal_text))

def get_fields(text):

    fields = define_fields(text)

    return extract_fields(fields)

with open("../jsons_with_info/full_dataset.json", "r", encoding="utf-8") as file:
    data = json.load(file)

file = open("testing2.txt", "w", encoding="utf-8")

counter_cat1 = 0
counter_cat2 = 0
counter_cat3 = 0
counter_email = 0
counter_name = 0
counter_sur = 0
full_matches = 0

i = 0

def category_compare(cat1: list[str], cat2: list[str]):
    codes1 = [item.split()[0] for item in cat1]
    codes2 = [item.split()[0] for item in cat2]
    common_elements = (set(codes1) & set(codes2))
    if common_elements != set():
        return 3

    for code1 in codes1:
        for code2 in codes2:
            if abs(int(code1[-4]) - int(code2[-4])) < 6:
                return 2

    for code1 in codes1:
        for code2 in codes2:
            s1 = code1.split(".")[2]
            s2 = code2.split(".")[2]
            if s1 == s2:
                return 1

    return 0


for appeals in data["documents"]:
    i += 1
    full_match = 0
    appeal_fields = get_fields(appeals["text"])
    text_from_LLM = appeal_fields["текст_обращения"]

    categories_from_LLM = get_categories(text_from_LLM)
    categories_from_human = appeals["categories"]

    file.write("-----------------------------------------------------------------------------\n")
    file.write("Обрабатываемый файл - (id = " + str(appeals["id"]) + "\n")
    if appeal_fields["email"] == appeals["email"]:
        counter_email += 1
        full_match += 1
        file.write("Email, определенный LLM: " + str(appeal_fields["email"]) + "\n")
        file.write("Email, определенный хьюманом: " + str(appeals["email"]) + "\n")
        file.write("✓ УСПЕШНО!\n")
    else:
        file.write("Email, определенный LLM: " + str(appeal_fields["email"]) + "\n")
        file.write("Email, определенный хьюманом: " + str(appeals["email"]) + "\n")
        file.write("✗ НЕУСПЕШНО!\n")

    if appeal_fields["имя"] == appeals["name"]:
        counter_name += 1
        full_match += 1
        file.write("Имя, определенное LLM: " + str(appeal_fields["имя"]) + "\n")
        file.write("Имя, определенное хьюманом: " + str(appeals["name"]) + "\n")
        file.write("✓ УСПЕШНО!\n")
    else:
        file.write("Имя, определенное LLM: " + str(appeal_fields["имя"]) + "\n")
        file.write("Имя, определенное хьюманом: " + str(appeals["name"]) + "\n")
        file.write("✗ НЕУСПЕШНО!\n")

    if appeal_fields["фамилия"] == appeals["surname"]:
        counter_sur += 1
        full_match += 1
        file.write("Фамилия, определенная LLM: " + str(appeal_fields["фамилия"]) + "\n")
        file.write("Фамилия, определенная хьюманом: " + str(appeals["surname"]) + "\n")
        file.write("✓ УСПЕШНО!\n")
    else:
        file.write("Фамилия, определенная LLM: " + str(appeal_fields["фамилия"]) + "\n")
        file.write("Фамилия, определенная хьюманом: " + str(appeals["surname"]) + "\n")
        file.write("✗ НЕУСПЕШНО!\n")

    flag = category_compare(categories_from_LLM, categories_from_human)

    file.write("Категории, которые выдала LLM: " + str(categories_from_LLM) + "\n")
    file.write("Категории, которые определил хьюман: " + str(categories_from_human) + "\n")
    file.write("Выжимка LLM: " + str(text_from_LLM) + "\n")

    if flag == 3:
        file.write("✓ УСПЕШНО МАКСИМАЛЬНО!\n")
        counter_cat1 += 1
        full_match += 1
    elif flag == 2:
        file.write("✓ НЕУСПЕШНО, НО ОЧЕНЬ РЯДОМ!\n")
        counter_cat2 += 1
    elif flag == 1:
        file.write("✓ НЕУСПЕШНО, НО ОДНА ПОДКАТЕГОРИЯ!\n")
        counter_cat3 += 1
    else:
        file.write("✗ НЕУСПЕШНО!\n")
    file.write("-----------------------------------------------------------------------------\n\n")

    if full_match == 4:
        full_matches += 1

file.write("ИТОГО: " + str(counter_cat1) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО ПОЛНОСТЬЮ ПРАВИЛЬНО")
file.write("ИТОГО: " + str(counter_cat2) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО РЯДОМ ПРАВИЛЬНО")
file.write("ИТОГО: " + str(counter_cat3) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО В ОДНОй ПОДКАТЕГОРИИ ПРАВИЛЬНО")
file.write("ИТОГО: " + str(counter_email) + " ЕМЕЙЛОВ БЫЛО ОПРЕДЕЛЕНО ПРАВИЛЬНО")
file.write("ИТОГО: " + str(counter_name) + " ИМЕН БЫЛО ОПРЕДЕЛЕНО ПРАВИЛЬНО")
file.write("ИТОГО: " + str(counter_sur) + " ФАМИЛИЙ БЫЛО ОПРЕДЕЛЕНО ПРАВИЛЬНО")
file.write("ИТОГО: " + str(full_matches) + " АБСОЛЮТНЫХ СОВПАДЕНИЙ")
