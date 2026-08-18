import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load models and data globally for fast access
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
VECTOR_STORE_PATH = "backend/vector_store"
METADATA_PATH = f"{VECTOR_STORE_PATH}/metadata.json"
INDEX_PATH = f"{VECTOR_STORE_PATH}/index.faiss"

# We initialize these lazily or at startup
model = None
index = None
metadata = []

def init_retrieval():
    global model, index, metadata
    print("Initializing retrieval service...")
    
    # Check if index exists
    if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
        print("Warning: Vector store not found. Please run ingest.py first.")
        return False
        
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        index = faiss.read_index(INDEX_PATH)
        with open(METADATA_PATH, 'r') as f:
            metadata = json.load(f)
        print("Retrieval service initialized.")
        return True
    except Exception as e:
        print(f"Failed to initialize retrieval service: {e}")
        return False

def retrieve_context(query: str, top_k: int = 3):
    global model, index, metadata
    
    if index is None or model is None:
        if not init_retrieval():
            return []
            
    # Embed query
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')
    
    # Search FAISS
    distances, indices = index.search(query_embedding, top_k)
    
    # Retrieve metadata for the matched chunks
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1 and idx < len(metadata):
            results.append({
                "text": metadata[idx]["text"],
                "score": float(distances[0][i]),
                "doc_id": metadata[idx]["doc_id"]
            })
            
    return results
