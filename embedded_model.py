import os
import json
from uuid import uuid4

import requests
import numpy as np

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")
API_KEY = os.getenv("API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = 'https://openrouter.ai/api/v1'
MODEL = 'mistralai/mistral-small-3.1-24b-instruct'

embedding_model = SentenceTransformer("ai-forever/ru-en-RoSBERTa")


def simple_ask():
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    user_prompt = "Кто сейчас президент США?"
    # user_prompt = "Расскажи график работы OOO Ромашка в городе Киров"

    messages = [{"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=8096,
        temperature=0.1
    )

    print(response.choices[0].message.content)


def context_ask():
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    user_prompt = "Расскажи график работы OOO Ромашка в городе Киров"

    context = """
Режим работы с 8 до 20, шоурум на ул.Ленина 25, пункт выдачи ул.Пушкина 17.
"""
    system_prompt = f"""
Ты профессиональный продавец-консультант компании. Отвечай ТОЛЬКО на основе предоставленного контекста. 
Если информации недостаточно – вежливо откажись отвечать. Сохраняй дружелюбный и уверенный тон.

**Роль:**
- Эксперт по продуктам/услугам компании
- Мастер вежливого общения
- Специалист по решению проблем клиентов

**Инструкции:**
1. Анализируй контекст из базы знаний: <CONTEXT_START>{context}<CONTEXT_END>
2. Отвечай максимально конкретно на вопрос: {user_prompt}
3. Если в контексте нет ответа: "Извините, эта информация временно недоступна. Уточните детали у менеджера"
4. Для сложных вопросов разбивай ответ на пункты
5. Избегай технического жаргона

**Стиль ответа:**
- Используй эмоджи для эмоциональной окраски (1-2 в сообщении)
- Подчеркивай выгоды клиента
- Предлагай дополнительные варианты: "Возможно вас также заинтересует..."
- Завершай вопросом: "Хотите уточнить какие-то детали?"

**Пример ответа:**
"Добрый день! <основной ответ из контекста>. 
Нужны дополнительные подробности? 😊"

**Технические примечания:**
- Контекст обрезан до 512 токенов
- Избегай markdown-разметки
- Ответ держи в пределах 3 предложений
"""

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=8096,
        temperature=0.1
    )

    print(response.choices[0].message.content)


####################### work_with_embeddings ##############################

def get_embeddings_local(text, task="search_document"):
    prefixed_text = f"{task}: {text}"
    # prefixed_text = text

    embedding = embedding_model.encode(
        prefixed_text,
        normalize_embeddings=True,
        convert_to_numpy=False,
        show_progress_bar=False
    ).tolist()
    return embedding


def get_embeddings_api(text, task="search_query"):
    API_URL = "https://router.huggingface.co/hf-inference/models/ai-forever/ru-en-RoSBERTa/pipeline/feature-extraction"
    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
    }
    prefixed_text = f"{task}: {text}"
    # prefixed_text = text
    payload = {
        "inputs": prefixed_text,
        "parameters": {
            "pooling_method": "cls",  # Явное указание пулинга
            "normalize_embeddings": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def embedd_example(text):
    print(get_embeddings_api(text))


def create_collection(client, collection_name, size):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE)
    )


def add_point(client, collection_name, text, payload):
    client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=str(uuid4().hex),
                vector=get_embeddings_local(text),
                payload=payload
            )
        ])


def make_chanks(long_text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", "! ", "? ", ]
    )
    chunks = splitter.split_text(long_text)
    return chunks


def clear_text_to_embedding(text):
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    system_prompt = f"""
Ты эксперт по подготовке текстовых данных для создания векторных представлений. 
Проведи семантическую оптимизацию текста по следующим правилам:

1. **Нормализация структуры**:
- Удали HTML/CSS/JS код, спецсимволы (кроме !?.,), лишние пробелы
- Замени кавычки на стандартные "
- Приведи сокращения к полной форме: "н-р" → "например"

2. **Семантическое уплотнение**:
- Сохрани термины, цифры, имена собственные
- Удали стоп-слова ("очень", "просто") и водные фразы 
- Объедини предложения с одинаковой темой
- Выдели ключевые сущности через двоеточие: "Python: язык программирования"

3. **Контекстуализация**:
- Добавь явные связи: вместо "работает быстро" → "скорость обработки: 500 запросов/сек"
- Замени местоимения на конкретные объекты: "он" → "алгоритм"
- Эксплицируй имплицитную информацию в [квадратных скобках]

4. **Чанкование** (для длинных текстов):
- Разбей на логические блоки по 1-3 предложения
- Добавь цепные маркеры: "#1", "#2"
- Сохрани тематическую целостность внутри чанка

**Пример преобразования:**

Исходный текст:
"Наш сервис, кстати, очень быстрый - обрабатывает до 500 запросов в секунду! Попробуйте прямо сейчас."

Обработанный:
"Скорость обработки: 500 запросов/сек. [показатель производительности сервиса] #1"

**Формат вывода:**
- Только очищенный текст без комментариев
- Максимальная информативная плотность
- Сохранение ключевых смысловых связей
- Чанки разделены пустой строкой

Обработай следующий текст:
"""

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": text}]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=8096,
        temperature=0.1
    )
    result = response.choices[0].message.content
    print("-----clear_text_to_embedding-----")
    print('original text', text)
    print('---------------------------------')
    print('clear text', result)
    return result


############################ read_json ###############################

def read_json_and_add_point(client, collection_name):
    with open('./result.json', 'r') as file:
        data = json.loads(file.read())
        print('всего сообщений:', len(data.get('messages')))
        count = len(data.get('messages'))
        for mess in data.get('messages')[:10]:
            print('id messages:', mess.get('id'))
            count -= 1
            print('Осталось:', count)
            if mess.get('text_entities'):
                full_text = []
                for tex_en in mess.get('text_entities'):
                    if tex_en.get('type') == 'plain':
                        full_text.append(tex_en.get('text'))
                text_to_embedd = ' '.join(full_text)

                payload = {
                    "content": text_to_embedd,
                    "metadata": {
                        "message_id": mess.get('id')
                    }}
                add_point(client, collection_name, text_to_embedd, payload)


def read_json_clear_and_add_point_v1(client, collection_name):
    with open('./result.json', 'r') as file:
        data = json.loads(file.read())
        print('всего сообщений:', len(data.get('messages')))
        count = len(data.get('messages'))
        for mess in data.get('messages'):
            print('id messages:', mess.get('id'))
            count -= 1
            print('Осталось:', count)
            if mess.get('text_entities'):
                full_text = []
                for tex_en in mess.get('text_entities'):
                    if tex_en.get('type') == 'plain':
                        # 1 way
                        clear_text = tex_en.get('text').replace('\n', ' ').strip().lower()
                        full_text.append(clear_text)

                text_to_embedd = ' '.join(full_text)

                # 2 way
                text_to_embedd = clear_text_to_embedding(text_to_embedd)

                payload = {
                    "content": text_to_embedd,
                    "metadata": {
                        "message_id": mess.get('id')
                    }}
                add_point(client, collection_name, text_to_embedd, payload)


def read_json_clear_and_add_point_v2(client, collection_name):
    with open('./result.json', 'r') as file:
        data = json.loads(file.read())
        print('всего сообщений:', len(data.get('messages')))
        count = len(data.get('messages'))
        for mess in data.get('messages'):
            print('id messages:', mess.get('id'))
            count -= 1
            print('Осталось:', count)
            if mess.get('text_entities'):
                full_text = []
                for tex_en in mess.get('text_entities'):
                    if tex_en.get('type') == 'plain':
                        clear_text = tex_en.get('text').replace('\n', ' ').strip().lower()
                        full_text.append(clear_text)

                text_to_embedd = ' '.join(full_text)

                # 2 way
                text_to_embedd = clear_text_to_embedding(text_to_embedd)

                text_chanks = make_chanks(text_to_embedd)

                for chank in text_chanks:
                    payload = {
                        "content": text_to_embedd,
                        "metadata": {
                            "message_id": mess.get('id')
                        }}
                    add_point(client, collection_name, chank, payload)


def find_text(client, collection_name, text):
    results = client.query_points(
        collection_name=collection_name,
        query=get_embeddings_api(text.lower()),
        limit=5,  # Количество ближайших результатов
        with_payload=True  # Включить payload в результаты
    )
    for _, scope in results:
        for point in scope:
            print(f"score: {point.score}")
            print(f"text: {point.payload.get('text')}")
            print("-----------")


if __name__ == "__main__":
    # simple_ask()
    # context_ask()
    # embedd_example('Привет ')

    client = QdrantClient(host="localhost", port=6333)
    collection_name = "rag_embeddings_with_prefix_clear_chanks_300_50"
    # text = 'маркетинговая стратегия магазина максимум результата быстро'

    # text = 'точки роста бизнеса'
    # text = 'Развитие личного бренда'
    text = 'Заработать миллион'
    # collection_name = 'no_clear_embeddings'
    find_text(client, collection_name, text)

    client.close()