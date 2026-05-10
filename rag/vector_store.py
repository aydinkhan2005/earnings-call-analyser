import chromadb
from pathlib import Path

CHROMA_PATH = Path(__file__).resolve().parents[1] / "chroma_store"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

def get_or_create_collection(transcript_metadata: dict):
    company = transcript_metadata["Company"].replace(" ", "_")
    year = transcript_metadata["Year"]
    quarter = transcript_metadata["Quarter"]
    transcript_id = f"{company}_{year}_Q{quarter}"

    existing = [c.name for c in client.list_collections()]

    if transcript_id in existing:
        return client.get_collection(transcript_id), False
    else:
        return client.create_collection(transcript_id), True

def add_chunks(collection, chunks: list[dict], embeddings: list):
    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings,
        documents=[chunk["Speech"] for chunk in chunks],
        metadatas=[{
            "speaker": chunk["Speaker"],
            "role": chunk["Role"],
            "company": chunk["Company"]
        } for chunk in chunks]
    )

def search(collection, query_embedding: list, n_results: int = 4):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results["documents"][0], results["metadatas"][0]