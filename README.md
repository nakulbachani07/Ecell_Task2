# NIT Trichy Institutional Policy RAG System

## Project Overview

This project is a document-based Question Answering system built using a Retrieval-Augmented Generation pipeline. The system allows users to ask natural language questions based on institutional policy documents of NIT Trichy and returns grounded answers with source references.

The system processes multiple PDF documents, extracts and cleans text, splits the text into chunks, generates embeddings, stores them in a local vector database, retrieves relevant chunks for a user query, and uses Gemini to generate the final answer.

The main goal of this project is to create a reliable knowledge management system for institutional rules, academic regulations, hostel rules, student conduct policies, and frequently asked questions.

---

## Problem Statement

Large institutional documents such as academic regulations, hostel rules, and disciplinary policies are often difficult for students to search manually. Students may need quick answers to questions like attendance requirements, fee reimbursement, hostel rules, or disciplinary guidelines.

This project solves that problem by building a semantic retrieval system where users can ask questions in normal language and receive answers based only on the uploaded documents.

---

## Documents Used

The knowledge base contains the following NIT Trichy documents:

* `FREQUENTLY_ASKED_QUESTIONS.pdf`
* `Regulations_B.Tech._2024.pdf`
* `Regulations_PG_2024.pdf`
* `Regulations_B.Arch._2025.pdf`
* `RULES_REGULATIONS_HOSTEL_RESIDENTS_2025_v2.pdf`
* `Students Conduct and Disciplinary Code.pdf`

These documents cover:

* Attendance requirements
* Academic regulations
* Course structure
* Programme electives
* Hostel rules
* Student conduct rules
* Disciplinary policies
* Scholarship and fee reimbursement
* Supplementary exams
* Revaluation process

---

## Folder Structure

```text
Ecell_Task_2/
├── app.py
├── README.md
├── requirements.txt
├── evaluation_results.json
├── .gitignore
├── models/
│   └── model_config.json
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── chunks.json
│   └── vector_store/
└── src/
    ├── preprocess.py
    ├── features.py
    ├── train.py
    ├── evaluate.py
    └── utils.py
```

---

## System Architecture

The system follows a Retrieval-Augmented Generation workflow:

```text
PDF Documents
↓
Text Extraction
↓
Text Cleaning
↓
Chunk Creation
↓
Embedding Generation
↓
ChromaDB Vector Store
↓
User Query
↓
Semantic Retrieval
↓
Context Creation
↓
Gemini Answer Generation
↓
Answer + Confidence + Sources
```

---

## Pipeline Explanation

### 1. Document Preprocessing

File used:

```text
src/preprocess.py
```

This stage reads all PDF files from the `data/raw/` folder using PyMuPDF. The extracted text is cleaned by removing unwanted spaces, page number noise, and unnecessary formatting.

The cleaned text is then divided into overlapping chunks. Each chunk contains:

* Chunk ID
* Source file name
* Page number
* Text
* Length of the chunk

Output file:

```text
data/processed/chunks.json
```

---

### 2. Embedding Generation and Vector Store Creation

File used:

```text
src/features.py
```

This stage loads the processed chunks and converts each chunk into an embedding using the SentenceTransformer model:

```text
all-MiniLM-L6-v2
```

The embeddings, original chunk text, metadata, and IDs are stored in a local ChromaDB vector database.

Output folder:

```text
data/vector_store/
```

---

### 3. Retrieval and Answer Generation

File used:

```text
src/train.py
```

When a user enters a query, the query is converted into an embedding using the same SentenceTransformer model. ChromaDB compares the query embedding with stored document embeddings and returns the top matching chunks.

The retrieved chunks are converted into a readable context and passed to Gemini along with the user query. The prompt instructs Gemini to answer only using the given context and avoid outside knowledge.

If the answer is not present in the retrieved context, the system responds:

```text
I could not find enough information in the provided documents.
```

---

### 4. Confidence Score

The system calculates a simple confidence score using the retrieval distance of the best matching chunk.

The logic used is:

```text
No results             → 0.20
Distance < 0.35        → 0.90
Distance < 0.60        → 0.75
Distance < 0.85        → 0.55
Distance >= 0.85       → 0.30
```

Lower distance means the retrieved document chunk is more semantically similar to the query.

---

### 5. FastAPI Backend

File used:

```text
app.py
```

The project includes a FastAPI backend to expose the RAG system through an API.

The main endpoint is:

```text
POST /query
```

Input format:

```json
{
    "query": "What is the attendance requirement in NIT Trichy?"
}
```

Output format:

```json
{
    "query": "What is the attendance requirement in NIT Trichy?",
    "answer": "The minimum attendance requirement is 75% in every subject.",
    "confidence": 0.55,
    "sources": [
        {
            "source_file": "FREQUENTLY_ASKED_QUESTIONS.pdf",
            "page_number": 1
        }
    ]
}
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## Evaluation

File used:

```text
src/evaluate.py
```

The system was evaluated using 7 test queries across different documents.

The evaluation tracks:

* Generated answer
* Confidence score
* Latency in seconds
* Sources retrieved
* Handling of unsupported queries

Output file:

```text
evaluation_results.json
```

### Evaluation Queries

```text
What is the attendance requirement in NIT Trichy?
```

```text
What are Programme Electives in B.Tech?
```

```text
What is the admission rule for foreign students in PG programmes?
```

```text
What are microcredit courses in B.Arch?
```

```text
Is NIT Trichy a smoking free and alcohol free campus?
```

```text
What is the procedure for scholarship and fee reimbursement?
```

```text
What is the mess menu for Monday?
```

The last query was intentionally used as a negative test because the mess menu is not present in the uploaded documents.

---

## Evaluation Summary

| Metric                | Result                        |
| --------------------- | ----------------------------- |
| Total Queries Tested  | 7                             |
| Answerable Queries    | 6                             |
| Unsupported Queries   | 1                             |
| Query Resolution Rate | 7/7 for the selected test set |
| Average Latency       | Around 18.66 seconds/query    |
| Confidence Range      | 0.30 to 0.75                  |

The system correctly refused to answer the unsupported query:

```text
What is the mess menu for Monday?
```

Response:

```text
I could not find enough information in the provided documents.
```

This shows that the system is able to avoid hallucinating when the answer is not present in the provided documents.

---

## Sample API Response

Example query:

```json
{
    "query": "What are Programme Electives in B.Tech?"
}
```

Example response:

```json
{
    "query": "What are Programme Electives in B.Tech?",
    "answer": "Programme Electives are specialized, choice-based courses offered by a student's own programme or branch. They provide flexibility and academic customization, allowing students to deepen their knowledge within their discipline and tailor their learning pathway according to professional goals.",
    "confidence": 0.75,
    "sources": [
        {
            "source_file": "Regulations_B.Tech._2024.pdf",
            "page_number": 6
        },
        {
            "source_file": "Regulations_B.Tech._2024.pdf",
            "page_number": 5
        }
    ]
}
```

---

## How to Run the Project

### Step 1: Clone the Repository

```bash
git clone <your-repository-link>
cd Ecell_Task_2
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Add Gemini API Key

Create a `.env` file in the project root.

Inside `.env`, add:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not upload the `.env` file to GitHub.

---

### Step 5: Add PDFs

Place all PDF documents inside:

```text
data/raw/
```

---

### Step 6: Run Preprocessing

```bash
python src/preprocess.py
```

This creates:

```text
data/processed/chunks.json
```

---

### Step 7: Create Vector Store

```bash
python src/features.py
```

This creates the local ChromaDB vector store inside:

```text
data/vector_store/
```

---

### Step 8: Run Terminal-Based Query System

```bash
python src/train.py
```

Then enter a query when prompted.

---

### Step 9: Run FastAPI Server

```bash
uvicorn app:app --reload
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Use the `POST /query` endpoint to test the system.

---

### Step 10: Run Evaluation

```bash
python src/evaluate.py
```

This creates:

```text
evaluation_results.json
```

---

## Technologies Used

* Python
* PyMuPDF
* SentenceTransformers
* ChromaDB
* Gemini API
* FastAPI
* Uvicorn
* Python-dotenv
* JSON

---

## Model and Configuration

The project uses the following main components:

| Component       | Value            |
| --------------- | ---------------- |
| Embedding Model | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB         |
| LLM             | Gemini           |
| Chunk Size      | 900 characters   |
| Chunk Overlap   | 150 characters   |
| Retrieval Count | Top 5 chunks     |

The configuration is stored in:

```text
models/model_config.json
```

---

## Limitations

* The system retrieves the top 5 chunks for every query, so some extra related sources may appear.
* The confidence score is a simple heuristic based on retrieval distance.
* Latency is relatively high because the embedding model is loaded during query execution and Gemini API is called externally.
* The system depends on the quality of text extraction from PDFs.
* It does not currently use reranking.
* It does not currently have a frontend interface.

---

## Future Improvements

* Load the embedding model once during application startup to reduce latency.
* Add reranking to improve source relevance.
* Add a relevance threshold to remove weak sources.
* Improve confidence calculation using multiple retrieved chunks.
* Add a frontend interface for users.
* Deploy the FastAPI backend online.
* Add support for more institutional documents.
* Add OCR support for scanned PDFs if needed.

---

## Conclusion

This project successfully demonstrates an end-to-end RAG-based knowledge management system for institutional policy documents. It can retrieve relevant information from multiple PDFs, generate grounded answers using Gemini, return confidence scores, and provide source references through a FastAPI backend.

The system is useful for answering student-related queries about academic regulations, hostel rules, disciplinary policies, attendance, scholarships, and programme requirements.
