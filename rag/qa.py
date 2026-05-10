import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

print("API KEY:", os.getenv("ANTHROPIC_API_KEY"))
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def build_context(documents: list[str], metadatas: list[dict]) -> str:
    context_blocks = []
    for doc, meta in zip(documents, metadatas):
        context_blocks.append(
            f"[{meta['role']} {meta['speaker']}]: {doc}"
        )
    return "\n\n".join(context_blocks)

def answer_question(query: str, documents: list[str], metadatas: list[dict]) -> str:
    context = build_context(documents, metadatas)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system="""You are an expert financial analyst assistant. 
        You will be given excerpts from an earnings call transcript and a question about it.
        Answer the question using only the information in the excerpts provided.
        If the answer cannot be found in the excerpts, say so clearly.
        Always cite which speaker you are drawing information from.""",
        messages=[{"role": "user", "content": f"""Transcript excerpts: {context} Question: {query}"""}])

    return response.content[0].text