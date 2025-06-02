import os

import google.generativeai as genai

genai.configure(api_key=os.environ['GENAI_API_KEY'])

embedding_model = genai.embed_content

def embed_text(text: str, task_type='semantic_similarity') -> list[float] | None:
    try:
        result = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type=task_type
        )
        return result['embedding']
    except Exception as e:
        print("Embedding error:", e)
        return None
