import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig, AutoModel
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import torch.nn.functional as F

def define_fields(text):
    MODEL_PATH = "D:/kit/saiga_yandexgpt_8b"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=False
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    generation_config = GenerationConfig.from_pretrained(MODEL_PATH)

    query = f"""
    Ты - секретарь государственной организации. Проанализируй текст обращения гражданина и извлеки ключевые поля в строгом формате.

    ТРЕБОВАНИЯ К ПОЛЯМ:
    - номер_обращения (если указан)
    - имя (если указано)
    - фамилия (если указана)
    - email (если указан)
    - район_проживания (если указан)
    - адресат (ФИО или организация, кому направлено)
    - текст_обращения (основная суть проблемы, 20-35 слов, одна строка, официальный стиль)

    ВАЖНЫЕ ПРАВИЛА:
    1. Формат вывода: название_поля: значение.
    2. Необходимо вывести ВСЕ поля. Если подходящее значение отсутствует - выводить значение: "-".
    3. Без пояснений, комментариев или лишних символов.
    
    ВАЖНЫЕ ПРАВИЛА ДЛЯ ПОЛЯ текст_обращения:
    1. Фокус на ОСНОВНОЙ ПРОБЛЕМЕ, а не на контексте
    2. Выделить КОНКРЕТНЫЙ ОБЪЕКТ проблемы (туалет, дорога, отопление и т.д.)
    3. Указать СУТЬ проблемы (платность, неработает, грязно и т.д.)
    4. Указать СФЕРУ проблемы (бытовое обслуживание, ремонтные работы, управление учреждением и т.д.)
    5. Только факты и требования по существу

    ПОЛНОЕ ОБРАЩЕНИЕ:
    {text}

    ВЫВЕДИ ТОЛЬКО ЗАПРОШЕННЫЕ ПОЛЯ В ТРЕБУЕМОМ ФОРМАТЕ
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

    print(output)
    return output

def define_category(text):
    MODEL_PATH = "D:/kit/saiga_yandexgpt_8b"
    rosberta_path = "D:/ru-en-RoSBERTa"
    chroma_path = "D:/LLM-class/local_chroma"
    collection_name = "appeals_embeddings"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=False
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    generation_config = GenerationConfig.from_pretrained(MODEL_PATH)

    embeddings = HuggingFaceEmbeddings(
        model_name=rosberta_path,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )

    chroma_db = Chroma(
        persist_directory=chroma_path,
        collection_name=collection_name,
        embedding_function=embeddings
    )

    results = chroma_db.similarity_search(
        query=text,
        k=15
    )

    context = []

    for doc in results:
        text_only = doc.metadata['id'] + " " + doc.page_content
        context.append(text_only)

    query = f"""
    Ты — опытный секретарь государственной организации. Твоя задача — классифицировать обращение гражданина.

    КОНТЕКСТ:
    Доступные для выбора категории (КОД + НАЗВАНИЕ):
    {context}

    ИНСТРУКЦИЯ:
    1.  ВНИМАТЕЛЬНО сопоставь текст обращения с предоставленным списком категорий.
    2.  Выбери от 1 до 3 наиболее релевантных категорий.
    3.  ОТВЕТ ДОЛЖЕН БЫТЬ строго в следующем формате:
        Код_1 Полное_Название_1; Код_2 Полное_Название_2
        *   Коды и названия должны быть разделены ОДНИМ пробелом.
        *   Категории должны быть разделены точкой с запятой и пробелом ("; ").
    4.  Никаких дополнительных комментариев, пояснений, точек в конце или кавычек быть не должно. Только чистый список категорий в одну строку.

    ТЕКСТ ОБРАЩЕНИЯ ГРАЖДАНИНА:
    {text}

    ОТВЕТ:
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

def simple_similarity(text1, text2):
    rosberta_path = "D:/ru-en-RoSBERTa"

    tokenizer = AutoTokenizer.from_pretrained(rosberta_path)
    model = AutoModel.from_pretrained(rosberta_path)
    model.eval()

    def get_embedding(text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        return outputs.last_hidden_state[:, 0, :]

    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)

    return F.cosine_similarity(emb1, emb2).item()
