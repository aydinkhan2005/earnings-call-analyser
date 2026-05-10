from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_chunks(chunks: list[dict]) -> list:
    texts = [
        f"{chunk['Role']} {chunk['Speaker']}: {chunk['Speech']}"
        for chunk in chunks
    ]
    return model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

def embed_query(query: str) -> list:
    return model.encode(query).tolist()