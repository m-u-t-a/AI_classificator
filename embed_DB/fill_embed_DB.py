from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from tools.categoryExtractor import category_extractor

rosberta_path = "D:/ru-en-RoSBERTa"

chroma_path = "D:/LLM-class/local_chroma"
collection_name = "appeals_embeddings"

model = SentenceTransformer(rosberta_path, device='cuda', local_files_only = True)

data = category_extractor("D:/categories.pdf")

res = list(map(data.get, data.keys()))

data_for_db = []

for i in range(len(res)):
    one_piece = {}
    one_piece["text"] = res[i]
    metadata_dictionary = {}
    metadata_dictionary["id"] = i + 1
    one_piece["metadata"] = metadata_dictionary
    data_for_db.append(one_piece)


def generate_chroma_db():
    embeddings = HuggingFaceEmbeddings(
        model_name = rosberta_path,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )

    chroma_db = Chroma.from_texts(
        texts=[item["text"] for item in data_for_db],
        embedding=embeddings,
        ids=[str(item["metadata"]["id"]) for item in data_for_db],
        metadatas=[item["metadata"] for item in data_for_db],
        persist_directory=chroma_path,
        collection_name=collection_name,
    )

    return chroma_db

db = generate_chroma_db()

results = db.similarity_search(
            query = "проведите газ пожалуйста в поселок Мымры",
            k = 5
        )

print(results)


