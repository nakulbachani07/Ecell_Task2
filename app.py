import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel

# allow app.py to import files from src folder
sys.path.append("src")

from train import search_document, generate_answer, calculate_confidence

# FastAPI app
app = FastAPI(
    title="NIT Trichy Policy RAG API",
    description="A document-based question answering API using ChromaDB and Gemini.",
    version="1.0"
)

#input format
class QueryRequest(BaseModel):
    query: str

#home route
@app.get("/")
def home():
    return {
        "message": "NIT Trichy Policy RAG API is running",
        "endpoint": "/query",
        "docs": "/docs"
    }

#Query route
@app.post("/query")
def query_documents( request: QueryRequest):
    user_query = request.query

    search_results = search_document(user_query, top_k=5)
    answer = generate_answer(user_query, search_results)
    confidence = calculate_confidence(search_results)

    sources = []
    used_sources = set()


    for result in search_results:
        source_file = result.get("source_file", "unknown")
        page_number = result.get("page_number", "unknown")

        source_key = (source_file, page_number)

        if source_key not in used_sources:
            sources.append({
                "source_file": source_file,
                "page_number": page_number
            })
            used_sources.add(source_key)

    return {
        "query": user_query,
        "answer": answer,
        "confidence": confidence,
        "sources": sources
    }

