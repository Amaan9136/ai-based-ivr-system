import re
import json
import ollama
import numpy as np
from typing import List, Dict, Any
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------- LLM: Generate and sanitize response ----------

# llama3.2:latest
# or
# gemma2:latest

def generate_response(prompt: str, model: str = "llama3.2:latest") -> str:
    response_text = ""
    print("[PROMPT]",prompt)

    try:
        # Use streaming correctly — accumulate chunks
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False,
        )

        response_text = response.get("response", "")

    except Exception as e:
        return f"Error generating response: {str(e)}"

    return sanitize_response(response_text.strip())


def sanitize_response(raw: str) -> str:
    # Clean up response if it includes code blocks or extra formatting
    cleaned = re.sub(r"^```(?:json)?\n", "", raw.strip())
    cleaned = re.sub(r"```$", "", cleaned)
    try:
        response_json = json.loads(cleaned)
        if isinstance(response_json, dict) and "title" in response_json:
            return response_json["title"].strip()
    except json.JSONDecodeError:
        pass
    return cleaned


# ---------- Batch Embedding Helper ----------
def embed_text(text: str, model: str) -> List[float]:
    try:
        response = ollama.embeddings(model=model, prompt=text)
        return response.get("embedding", [])
    except Exception as e:
        return None


# ---------- Main Embedding Function ----------
def generate_embeddings(
    texts: List[str],
    model: str = "mxbai-embed-large",
    chunk_size: int = 100,
    max_workers: int = 6,
    collection: Any = None,
    ids: List[str] = None,
    documents: List[str] = None,
) -> List[List[float]]:

    if not texts:
        return []

    total = len(texts)
    batches = []
    for i in range(0, total, chunk_size):
        batch = texts[i:i + chunk_size]
        batch_ids = ids[i:i + chunk_size] if ids else None
        batch_docs = documents[i:i + chunk_size] if documents else batch
        batches.append((i, batch, batch_ids, batch_docs))

    tqdm.write(f"🔍 Starting embedding in {len(batches)} batches (chunk size = {chunk_size})")

    all_embeddings = []

    with tqdm(total=len(batches), desc="🚀 Total Progress") as overall_progress:
        for batch_index, batch, batch_ids, batch_docs in batches:
            batch_embeddings = []
            successful = 0
            failed = 0

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_text = {
                    executor.submit(embed_text, text, model): (text, idx)
                    for idx, text in enumerate(batch)
                }

                for future in as_completed(future_to_text):
                    text, idx = future_to_text[future]
                    embedding = future.result()
                    batch_embeddings.append(embedding)
                    if embedding:
                        successful += 1
                    else:
                        failed += 1

            # Store in collection (if passed)
            if collection and batch_ids:
                filtered = [(e, i, d) for e, i, d in zip(batch_embeddings, batch_ids, batch_docs) if e]
                if filtered:
                    emb, id_, doc_ = zip(*filtered)
                    collection.add(embeddings=emb, ids=id_, documents=doc_)

            all_embeddings.extend([e for e in batch_embeddings if e])
            tqdm.write(f"✅ Batch {batch_index}-{batch_index+len(batch)-1}: {successful} stored, {failed} failed.")
            overall_progress.update(1)

    tqdm.write(f"\n🎉 Done! Embedded {len(all_embeddings)} total entries.\n")
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
        if similarity >= 0.20:
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

# --- LLM Response Test ---
prompt = "Give me a creative idea to reduce plastic waste"
llm_output = generate_response(prompt)
print("\nLLM Output:")
print(llm_output)

"""