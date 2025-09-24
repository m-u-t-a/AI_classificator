import re

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
    content = file.read()

all_data = extract_all_data(content)

# print(f"Найдено пар: {len(category_pairs)}")
# for i, pair in enumerate(category_pairs):
#     print(f"Пара {i + 1}:")
#     print(f"LLM: {pair[0]}")
#     print(f"Human: {pair[1]}")
#     print("-" * 50)

statistics = open("testing2.txt", "w", encoding="utf-8")

counter_cat1 = 0
counter_cat2 = 0
counter_cat3 = 0
counter_email = 0
counter_name = 0
counter_sur = 0
full_matches = 0

i = 0

penis = ['0003.0009.0099.0733 Транспортное обслуживание населения, пассажирские перевозки', '0002.0014.0143.0391 Помещение в больницы и специализированные лечебные учреждения. Оплата за лечение, пребывание в лечебных учреждениях']
vagin = ['0003.0009.0104.0000 Бытовое обслуживание населения']

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

for appeal in all_data:
    i += 1
    full_match = 0

    categories_from_LLM = appeal["categories_llm"]
    categories_from_human = appeal["categories_human"]

    if appeal["email_llm"] == appeal["email_human"]:
        counter_email += 1
        full_match += 1

    if appeal["name_llm"] == appeal["name_human"]:
        counter_name += 1
        full_match += 1

    if appeal["surname_llm"] == appeal["surname_human"]:
        counter_sur += 1
        full_match += 1

    flag = category_compare(categories_from_LLM, categories_from_human)

    if flag == 3:
        full_match += 1
        counter_cat1 += 1
    elif flag == 2:
        counter_cat2 += 1
    elif flag == 1:
        counter_cat3 += 1

    if full_match == 4:
        full_matches += 1

statistics.write("ИТОГО: " + str(counter_cat1) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО ПОЛНОСТЬЮ ПРАВИЛЬНО")
statistics.write("ИТОГО: " + str(counter_cat2) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО РЯДОМ ПРАВИЛЬНО")
statistics.write("ИТОГО: " + str(counter_cat3) + " КАТЕГОРИЙ БЫЛО ОПРЕДЕЛЕНО В ОДНОй ПОДКАТЕГОРИИ ПРАВИЛЬНО")
statistics.write("ИТОГО: " + str(full_matches) + " АБСОЛЮТНЫХ СОВПАДЕНИЙ!!!")
