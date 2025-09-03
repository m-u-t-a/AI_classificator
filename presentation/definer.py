import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig

def define_fields(text):
    MODEL_PATH = "D:/kit/saiga_yandexgpt_8b"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=False
    )
    # model = AutoModelForCausalLM.from_pretrained(
    #     MODEL_PATH,
    #     device_map="auto",
    #     torch_dtype=torch.float32
    # )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    generation_config = GenerationConfig.from_pretrained(MODEL_PATH)

    query = f"""
    Ты - секретарь государственной организации, которому поступило обращение гражданина. Твоя задача:
    Проанализируй предоставленный текст обращения гражданина и извлеки ключевые поля в структурированном формате.
    Ответ представь в формате текста со следующими полями:
    номер_обращения,
    дата_обращения (в формате "DD.MM.YYYY"),
    автор (ФИО гражданина),
    email (если указан),
    телефон (если указан),
    населенный_пункт (если указан. название поля "населенный_пункт" пиши именно так и никак иначе),
    адрес (если указан),
    социальное_положение (если указано),
    адресат (кому направлено обращение. указать ФИО или организацию),
    текст_обращения (нужно извлечь основную суть обращения гражданина. итоговая выжимка может быть от 300 до 500 слов).
    Если какое-то поле отсутствует в тексте, укажи для него значение "не указано".
    Не пиши кроме названия поля и его значения никаких пояснений, ничего не придумывай сверх поставленной задачи.
    Формат вывода:
    название поля: значение поля
    Не вставляй никаких лишних символов, сохраняй такой формат вывода.
    Предоставленный текст:
    {text}
    """

    prompt = tokenizer.apply_chat_template([{
        "role": "user",
        "content": query
    }], tokenize=False, add_generation_prompt=True)

    data = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    data = {k: v.to(model.device) for k, v in data.items()}
    data.pop("token_type_ids", None)

    output_ids = model.generate(**data, generation_config=generation_config)[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    return output

def define_category(text):
    MODEL_PATH = "D:/kit/saiga_yandexgpt_8b"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,  # Используем float16 вместо bfloat16
        device_map="auto",
        load_in_8bit=False    # Отключаем 8-битное квантование
    )
    # model = AutoModelForCausalLM.from_pretrained(
    #     MODEL_PATH,
    #     device_map="auto",
    #     torch_dtype=torch.float32
    # )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    generation_config = GenerationConfig.from_pretrained(MODEL_PATH)

    query =  f"""
        "Ты - секретарь государственной организации, которому поступило обращение гражданина. Твоя задача:
        Проанализируй предоставленный текст обращения гражданина и определи его категорию. Вот какие могут быть категории:
        'Благоустройство городов и поселков. Обустройство придомовых территорий',
        'Выделение земельных участков для строительства, фермерства, садоводства и огородничества',
        'Газификация поселений',
        'Дорожное хозяйство',
        'Лечение и оказание медицинской помощи',
        'Оплата жилищно-коммунальных услуг (ЖКХ)',
        'Переработка вторичного сырья и бытовых отходов. Полигоны бытовых отходов',
        'Переселение из подвалов, бараков, коммуналок, общежитий, аварийных домов, ветхого жилья, санитарно-защитной зоны',
        'Получение места в детских дошкольных воспитательных учреждениях',
        'Социальное обеспечение, материальная помощь многодетным, пенсионерам и малообеспеченным слоям населения'
        Текст может относиться только к одной категории или одновременно к двум, но не более.
        Формат вывода:
        название категории
        Больше ничего не пиши в ответе! Если вдруг текст относится сразу к двум категориям, дописывай вторую через знак ";", чтобы получилось вот так:
        название первой категории; название второй категории.

        Предоставленный текст:
        {text}
        """


    prompt = tokenizer.apply_chat_template([{
        "role": "user",
        "content": query
    }], tokenize=False, add_generation_prompt=True)

    data = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    data = {k: v.to(model.device) for k, v in data.items()}
    data.pop("token_type_ids", None)

    output_ids = model.generate(**data, generation_config=generation_config)[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

    return output
