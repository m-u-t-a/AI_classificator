from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import re

rosberta_path = "D:/ru-en-RoSBERTa"

chroma_path = "D:/LLM-class/local_chroma"
collection_name = "appeals_embeddings"

embeddings = HuggingFaceEmbeddings(
        model_name = rosberta_path,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
)

chroma_db = Chroma(
    persist_directory=chroma_path,
    collection_name=collection_name,
    embedding_function=embeddings
)

results = chroma_db.similarity_search(
            query = "проведите газ пожалуйста в поселок Мымры",
            k = 10
        )

context = []

for doc in results:
    text_only = doc.page_content
    context.append(text_only)

print(context)