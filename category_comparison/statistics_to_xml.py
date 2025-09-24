import re
import csv
from presentation.definer import simple_similarity

def extract_all_data(content):
    data_entries = []

    pattern = r'Обрабатываемый файл - \(id = (.*?)\s*Email, определенный LLM:\s*(.*?)\s*Email, определенный хьюманом:\s*(.*?)\s*[✓✗].*?Имя, определенное LLM:\s*(.*?)\s*Имя, определенное хьюманом:\s*(.*?)\s*[✓✗].*?Фамилия, определенная LLM:\s*(.*?)\s*Фамилия, определенная хьюманом:\s*(.*?)\s*[✓✗].*?Категории, которые выдала LLM:\s*(.*?)\s*Категории, которые определил хьюман:\s*(.*?)\s*Выжимка LLM:\s*(.*?)\s*-----------------------------------------------------------------------------'

    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        file_id, email_llm, email_human, name_llm, name_human, surname_llm, surname_human, categories_llm_str, categories_human_str, summary = match

        llm_categories = parse_categories(categories_llm_str.strip())
        human_categories = parse_categories(categories_human_str.strip())

        file_id = file_id.strip()
        email_llm = email_llm.strip()
        email_human = email_human.strip()
        name_llm = name_llm.strip()
        name_human = name_human.strip()
        surname_llm = surname_llm.strip()
        surname_human = surname_human.strip()
        summary = summary.strip().strip('"')
        summary = summary.split('\n')[0].strip()

        entry = {
            'file_id': file_id,
            'email_llm': email_llm,
            'email_human': email_human,
            'name_llm': name_llm,
            'name_human': name_human,
            'surname_llm': surname_llm,
            'surname_human': surname_human,
            'categories_llm': llm_categories,
            'categories_human': human_categories,
            'summary': summary
        }

        data_entries.append(entry)

    return data_entries


def parse_categories(category_str):
    categories = []
    category_str = category_str.strip().replace('\n', ' ')

    if '[' in category_str and ']' in category_str:
        content = category_str[category_str.find('[') + 1:category_str.find(']')]

        for cat in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", content):
            cat = cat.strip().strip("'\"")
            if cat:
                categories.append(cat)
    else:
        if category_str:
            categories.append(category_str)

    return categories

with open('testing.txt', 'r', encoding='utf-8') as file:
    testing_text = file.read()

all_data = extract_all_data(testing_text)


def category_compare(cat1: list[str], cat2: list[str]):
    codes1 = [item.split()[0] for item in cat1]
    codes2 = [item.split()[0] for item in cat2]

    common_elements = (set(codes1) & set(codes2))
    if common_elements != set():
        return 3

    for code1 in codes1:
        for code2 in codes2:
            if abs(int(code1[-4:]) - int(code2[-4:])) < 6:
                return 2

    for code1 in codes1:
        for code2 in codes2:
            s1 = code1.split(".")[2]
            s2 = code2.split(".")[2]
            if s1 == s2:
                return 1

    return 0

counter_cat1 = 0
counter_cat2 = 0
counter_cat3 = 0
counter_email = 0
counter_name = 0
counter_sur = 0

statistics = open("stat.csv", "w", newline='', encoding="utf-8-sig")

fieldnames = [
    'file_id',
    'email_llm', 'email_human',
    'name_llm', 'name_human',
    'surname_llm', 'surname_human',
    'categories_llm', 'categories_human', 'match_mark',
    'summary'
]

writer = csv.DictWriter(statistics, fieldnames=fieldnames)
writer.writeheader()

for piece in all_data:

    categories_from_LLM = piece['categories_llm']
    categories_from_human = piece['categories_human']

    match_marks = []

    for cat1 in categories_from_LLM:
        for cat2 in categories_from_human:
            match_marks.append(simple_similarity(cat1, cat2))

    row_data = {
        'file_id': piece["file_id"],
        'email_llm': piece["email_llm"],
        'email_human': piece["email_human"],
        'name_llm': piece["name_llm"],
        'name_human': piece["name_human"],
        'surname_llm': piece["surname_llm"],
        'surname_human': piece["surname_human"],
        'categories_llm': ' | '.join(piece["categories_llm"]),
        'categories_human': ' | '.join(piece["categories_human"]),
        'match_mark': match_marks,
        'summary': piece["summary"]
    }

    writer.writerow(row_data)
