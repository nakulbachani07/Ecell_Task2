import os
import re
import json # for saving chunks in a diff file
from pathlib import Path
import fitz #pymupdf

PDFs = "data/pdfs"
Output_folder = "data/processed"
output_file = "data/processed/chunks.json"

def clean_text(text):
    text = re.sub(r"[ \t]+"," ",text) #remove extra spaces or tabs
    text = re.sub(r"\n\s*\n+", "\n\n",text) #remove extra lines , \n - new line , "\n\n - one para gap" , \s* - any no. of spaces/newlines/tabs
    text = re.sub(r"Page\s+\d+(\s+of\s+\d+)?", "" , text, flags=re.IGNORECASE) # remove page no. , \d+ - one or more digits
    text = re.sub(r"\ns*\d+\s*\n", "\n",text) #remove page no. in a line
    text = re.sub(r"[-_=]{3,}", " ", text) # remove long made of dash or equal signs

    text = text.strip() # remove unnecessary spaces from start and end

    return text

def read_pdf(pdf_path):
    pages_data = []
    file_name = os.path.basename(pdf_path) # only this file name, no loaction

    try:
        pdf = fitz.open(pdf_path)

        for page_no in range(len(pdf)):
            page = pdf[page_no]
            text = page.get_text()

            text = clean_text(text)

            if len(text) > 50: # saving pages with enough content..
                pages_data.append({
                    "file_name" : file_name,
                    "page_number": page_no +1,
                    "text" : text
                })

        pdf.close()

    except Exception as e:
        print("Error while reading:", file_name)
        print(e)

    return pages_data

def make_chunks(text, chunk_size=900,overlap=150):
    chunks = []
    
    step = chunk_size - overlap # every new chunk starts after 750 character , while 150 character are repeated from previous chunk

    for start in range(0, len(text) , step):
        end = start+ chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())

    return chunks

def process_documents():
    os.makedirs(Output_folder, exist_ok=True)

    all_chunks =  []
    chunk_id = 0

    pdf_files = []

    for file in os.listdir(PDFs):
        if file.endswith(".pdf"):
            pdf_files.append(file)

    if len(pdf_files) == 0:
        print("No PDF files found")
        return
    
    print("pdf files founnd:" , len(pdf_files))

    for file in pdf_files: # loop for each pdf one by one
        pdf_path = os.path.join(PDFs,file) # os.path.join() combine , PDFs and file , path

        print("Processing:" , file)

        pages = read_pdf(pdf_path)

        for page in pages: # go through every page.
            page_chunks = make_chunks(page["text"]) # text from that particular page dictionary

            for chunk in page_chunks: # go through eah chunk
                if len(chunk) < 100:
                    continue

                all_chunks.append({
                    "chunk_id": chunk_id,
                    "page_number":page["page_number"],
                    "text": chunk,
                    "length": len(chunk),
                    "source_file": page["file_name"]
                })

                chunk_id += 1

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks,f, indent=4,ensure_ascii=False) # indent = 4(makes file readable) , ensure_ascii - llows proper saving of normal characters instead of converting everything into weird escape codes

    print("Total chunks created:", len(all_chunks))
    print("chunks saved at:" , output_file)


if __name__ == "__main__": # run document only when this file is executed directly
    process_documents() # when you import functions from preprocess.py later, it will not automatically start preprocessing again.






