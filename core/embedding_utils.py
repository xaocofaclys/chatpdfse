# core/embedding_utils.py

import os
import hashlib
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

TEMP_DIR = "tempfiles"

def hash_pdf(file):
    return hashlib.md5(file.getvalue()).hexdigest()

def process_pdfs(uploaded_files, embeddings):
    documents = []
    os.makedirs(TEMP_DIR, exist_ok=True)
    source_map = {}

    for file in uploaded_files:
        file_hash = hash_pdf(file)
        temp_path = os.path.join(TEMP_DIR, f"{file_hash}.pdf")
        with open(temp_path, "wb") as f:
            f.write(file.getvalue())

        loader = PyPDFLoader(temp_path)
        loaded = loader.load()
        documents.extend(loaded)
        source_map[file.name] = temp_path

    splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=200)
    splits = splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(splits, embedding=embeddings)

    return vectorstore.as_retriever(), source_map
