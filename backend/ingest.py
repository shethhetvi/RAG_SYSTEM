import os
import json
import numpy as np
import faiss
from datasets import load_dataset
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
DATASET_NAME = "ai4bharat/MSMARCO-XI"
# Use english subset for now if available, or just take first N rows
NUM_SAMPLES = 500
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_STORE_PATH = "vector_store"
METADATA_PATH = "vector_store/metadata.json"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def ingest_data():
    print(f"Loading {NUM_SAMPLES} samples from {DATASET_NAME}...")
    # Load dataset - MSMARCO usually has a 'train' or 'validation' split.
    # The 'ai4bharat/MSMARCO-XI' dataset has an 'en' config for english.
    try:
        dataset = load_dataset(DATASET_NAME, "en", split=f"train[:{NUM_SAMPLES}]")
    except Exception as e:
        print(f"Error loading 'en' config, falling back to default: {e}")
        try:
            # Fallback if config is different
            dataset = load_dataset(DATASET_NAME, split=f"train[:{NUM_SAMPLES}]")
        except Exception as e2:
            print(f"Could not load dataset. Make sure you have HuggingFace access or internet connection. {e2}")
            return

    print("Dataset loaded successfully.")

    # Initialize text splitter for vast chunking (semantic + overlap)
    # We use recursive character splitting to keep paragraphs/sentences intact as much as possible
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = []
    metadata = []

    print("Chunking documents...")
    # MSMARCO usually has 'query', 'passages' or 'text' columns. We need to inspect the schema.
    # Typically, passages are what we want to index.
    
    # Assuming standard text column for now. If it's a QA dataset, we might index answers/passages.
    for i, row in enumerate(dataset):
        # We need to find the text content. It might be 'text', 'passage', 'content'
        text_content = row.get("text", "") or row.get("passage", "") or row.get("content", "")
        if not text_content:
            # Try to get string representation of values if specific keys aren't found
            texts = [str(v) for k, v in row.items() if isinstance(v, str) and len(v) > 20]
            text_content = " ".join(texts)

        if not text_content:
            continue

        doc_id = row.get("id", str(i))
        
        # Split text into chunks
        doc_chunks = text_splitter.split_text(text_content)
        
        for chunk_idx, chunk_text in enumerate(doc_chunks):
            chunks.append(chunk_text)
            metadata.append({
                "doc_id": doc_id,
                "chunk_index": chunk_idx,
                "source": "MSMARCO-XI",
                "text": chunk_text
            })

    print(f"Generated {len(chunks)} chunks.")

    # Load embedding model
    print(f"Loading embedding model {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print("Embedding chunks...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # Create FAISS index
    print("Creating FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save to disk
    print(f"Saving vector store to {VECTOR_STORE_PATH}...")
    ensure_dir(VECTOR_STORE_PATH)
    faiss.write_index(index, os.path.join(VECTOR_STORE_PATH, "index.faiss"))
    
    with open(METADATA_PATH, 'w') as f:
        json.dump(metadata, f)

    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
