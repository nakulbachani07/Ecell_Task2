import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import os

from dotenv import load_dotenv

VECTOR_DB_FOLDER = "data/vector_store"
COLLECTION_NAME = "nit_trichy_docs"

def search_document(query, top_k=5):
    print("loading embedding model")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to vector store")
    client = chromadb.PersistentClient(path=VECTOR_DB_FOLDER)

    collection = client.get_or_create_collection(name=COLLECTION_NAME) # collection contains stored PDF chunks

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding], # because chromadb can search multiple queries at once, therefore we wrap iy inside a list
        n_results=top_k
    )

    final_results = []

    for i in range(len(results["documents"][0])): # [0] because chromadb result is nested , and since we searched only one query , we use [0].
        metadata = results["metadatas"][0][i]
        final_results.append({
            "text": results["documents"][0][i],
            "source_file": metadata.get("source_file", "unknown"),
            "page_number": results["metadatas"][0][i]["page_number"],
            "distance": results["distances"][0][i]
        })

    return final_results

def make_context(search_results): 
    context = ""

    for index, result in enumerate(search_results,start=1):
        context += f"\nSource {index}:\n "
        context += f"File: {result.get('source_file','unkonwn')}\n"
        context += f"Page: {result['page_number']}\n"
        context += f"Text: {result['text']}\n"

    return context

def calculate_confidence(search_results):
    if len(search_results) == 0:
        return 0.20
    
    best_distance = search_results[0]["distance"] # first retrieved chunk

    if best_distance < 0.35:
        return 0.90
    elif best_distance < 0.60:
        return 0.75
    elif best_distance < 0.85:
        return 0.55
    else:
        return 0.30
    
def generate_answer(query, search_results):
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "Gemini API key not found. Please add it in the .env file"
    
    genai.configure(api_key=api_key) # connect to gemini with my python code my API key.

    context = make_context(search_results)

    prompt = f"""
You are a document-based question answering assistant.

Answer the user's question using only the context given below.
Rules:
1. Do not use outside knowledge.
2. If the answer is not clearly present in the context, say:
"I could not find enough information in the provided documents"
3. Keep the answer simple and direct.
4. Mention source file and page number if useful.

Context:
{context}

User question:
{query}

Answer:
"""
    
    model = genai.GenerativeModel("gemini-3.5-flash")
    response = model.generate_content(prompt)

    return response.text

def print_sources(search_results):
    print("\nSources:")

    used_sources = set() # does not print duplicate sources

    for result in search_results:
        source = result.get("source_file", "unknown")
        page_number = result.get("page_number", "unknown")

        if source not in used_sources:
            print(f"- {result['source_file']}, Page {result['page_number']}")
            used_sources.add(source)

if __name__ == "__main__":
    query = input("Enter your query: ")

    search_results = search_document(query, top_k=5)

    print("\nGenerating answer...\n")

    answer = generate_answer(query, search_results)
    confidence = calculate_confidence(search_results)

    print("Answer:")
    print(answer)

    print("Confidence:" , confidence)

    print_sources(search_results)

     