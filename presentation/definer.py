import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

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
    текст_обращения (нужно извлечь основную суть обращения гражданина. Итоговая выжимка может быть до 100 - 150 слов. Пиши ее в одну строку, без переноса).
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
        encode_kwargs={"normalize_embeddings": True},
    )

    chroma_db = Chroma(
        persist_directory=chroma_path,
        collection_name=collection_name,
        embedding_function=embeddings
    )

    results = chroma_db.similarity_search(
        query=text,
        k=10
    )

    context = []

    for doc in results:
        text_only = doc.page_content
        context.append(text_only)

    query = f"""
        Ты - секретарь государственной организации, которому поступило обращение гражданина. Твоя задача:
        Проанализируй предоставленный текст обращения гражданина и определи его категорию. Вот все возможные категории:
        {context}
        Текст может относиться только к одной категории или одновременно к двум или трем, но не более.
        Не обрамляй ответ кавычками. Сохраняй исходные формулировки категорий, даже если они состоят из двух предложений.
        Не вставляй никаких лишних символов, укажи только названия категорий через знак ";".
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
