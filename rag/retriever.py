from rag.embedder import embed_chunks, embed_query
from rag.vector_store import get_or_create_collection, add_chunks, search

def get_relevant_chunks(transcript_metadata: dict, all_chunks: list[dict], query: str):
    collection, is_new = get_or_create_collection(transcript_metadata)

    if is_new:
        embeddings = embed_chunks(all_chunks)
        add_chunks(collection, all_chunks, embeddings)

    query_embedding = embed_query(query)
    documents, metadatas = search(collection, query_embedding)

    return documents, metadatas