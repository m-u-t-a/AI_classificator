from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from tools.categoryExtractor import category_extractor

rosberta_path = "D:/ru-en-RoSBERTa"

chroma_path = "D:/LLM-class/local_chroma"
collection_name = "appeals_embeddings"

model = SentenceTransformer(rosberta_path, device='cuda', local_files_only = True)

data = category_extractor("D:/categories.pdf")

data_for_db = []

for key in data:
    one_piece = {}
    one_piece["text"] = data[key]
    metadata_dictionary = {}
    metadata_dictionary["id"] = key
    one_piece["metadata"] = metadata_dictionary
    data_for_db.append(one_piece)

def generate_chroma_db():
    embeddings = HuggingFaceEmbeddings(
        model_name = rosberta_path,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True}
    )

    chroma_db = Chroma.from_texts(
        texts=[item["text"] for item in data_for_db],
        embedding=embeddings,
        ids=[str(item["metadata"]["id"]) for item in data_for_db],
        metadatas=[item["metadata"] for item in data_for_db],
        persist_directory=chroma_path,
        collection_name=collection_name
    )

    return chroma_db

generate_chroma_db()


