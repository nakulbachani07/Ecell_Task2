import json
import chromadb
from sentence_transformers import SentenceTransformer # used to load embedding model

CHUNKS_FILE = "data/processed/chunks.json"
VECTOR_DB_FOLDER = "data/vector_store"
COLLECTION_NAME = "nit_trichy_docs"

def load_chunks():
    with open(CHUNKS_FILE,"r",encoding="utf-8") as file:
        chunks = json.load(file) # reads json file and convert into python list

    return chunks

def create_vector_store():
    print("Loading chunks...")
    chunks = load_chunks()

    print("Total chunks loaded:" , len(chunks))

    print("Loading embedding model..")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to ChromaDB..")
    client = chromadb.PersistentClient(path=VECTOR_DB_FOLDER) #PersistentClient means the database will be saved permanently, So even after closing terminal, the vector store remains saved.
    # client means your connection to ChromaDB.
    # client = connection to ChromaDB database
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    # collection is like a table/folder inside ChromaDB where your chunks are stored

    documents = []
    metadatas = []
    ids = []

    for chunk in chunks:
        documents.append(chunk["text"])

        metadatas.append({
            "source_file": chunk.get("source_file", chunk.get("file_name", "unknown")),
            "page_number": chunk["page_number"],
            "length": chunk["length"]
        })

        ids.append(str(chunk["chunk_id"]))

    print("Creating embeddings...")
    embeddings = model.encode(documents).tolist() # documents is a list of chunk texts

    print("Adding chunks to ChromaDB")

    collection.add(
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=ids
    )

    print("Vector store created ")
    print("Saved inside:" , VECTOR_DB_FOLDER)


if __name__ == "__main__":
    create_vector_store()

