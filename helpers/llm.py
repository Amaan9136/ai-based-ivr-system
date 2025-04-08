import re
import json
import ollama
import numpy as np
from typing import List, Dict
import chromadb


# ---------- LLM: Generate and sanitize response ----------

def generate_response(prompt: str, model: str = "llama3.2") -> str:
    response = ollama.generate(
        model=model,
        prompt=prompt,
        stream=False
    )

    raw_response = response.get("response", "").strip()
    return sanitize_response(raw_response)

def sanitize_response(raw: str) -> str:
    cleaned = re.sub(r"^```(?:json)?\n", "", raw.strip())
    cleaned = re.sub(r"```$", "", cleaned)

    try:
        response_json = json.loads(cleaned)
        if isinstance(response_json, dict) and "title" in response_json:
            return response_json["title"].strip()
    except json.JSONDecodeError:
        pass

    return cleaned

# ---------- Embedding + Batch Embeddings ----------

# chroma_client = chromadb.Client()
# collection = chroma_client.get_or_create_collection(name="docs")

def generate_embeddings(texts: List[str], model: str = "mxbai-embed-large") -> List[List[float]]:
    if not texts:
        return []

    all_embeddings = []
    for text in texts:
        response = ollama.embeddings(
            model=model,
            prompt=text
        )
        embedding = response.get("embedding", [])
        if embedding:
            all_embeddings.append(embedding)
        else:
            print(f"[Warning] No embedding returned for: {text}")
    return all_embeddings

# ---------- Similarity ----------

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    dot_product = np.dot(vec1, vec2)
    norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if norm_product == 0:
        return 0.0
    return float(dot_product / norm_product)


def find_similarities(normal_text: str, test_texts: List[str]) -> List[Dict[str, float]]:
    if not normal_text or not test_texts:
        return []

    texts = [normal_text] + test_texts
    embeddings = generate_embeddings(texts)

    base_vector = np.array(embeddings[0])
    comparison_vectors = [np.array(vec) for vec in embeddings[1:]]

    results = []
    for text, vector in zip(test_texts, comparison_vectors):
        similarity = cosine_similarity(base_vector, vector)
        results.append({
            "text": text,
            "similarity": round(similarity, 4)
        })

    return results


# TEST ABOVE FUNCTIONS

"""

# --- Embedding Test ---
texts = ["Hey how are you", "Llamas carry loads"]
embeddings = generate_embeddings(texts)
print("Embedding Test:")
for text, emb in zip(texts, embeddings):
    print(f"{text} => Embedding size: {len(emb)} | Sample: {emb[:5]}")

# --- Similarity Test ---
similarities = find_similarities(texts[0], [texts[1]])
print("\nSimilarity Test:")
for s in similarities:
    print(f"{s['similarity']} - {s['text']}")

# --- LLM Response Test ---
prompt = "Give me a creative idea to reduce plastic waste"
llm_output = generate_response(prompt)
print("\nLLM Output:")
print(llm_output)

"""