import os
import numpy as np
import requests
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def embed_text(text: str) -> np.ndarray:
    """Generate Gemini embeddings for text."""
    res = genai.embed_content(model="models/embedding-001", content=text)
    return np.array(res["embedding"], dtype=np.float32)

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def find_relevant_kb(query: str, kb_repo: str, github_token: str, kb_path: str = "knowledge") -> dict:
    """
    Fetch all Markdown KB files from a specific folder (e.g., /knowledge)
    in a GitHub repo and return the best semantic match.
    """
    query_vec = embed_text(query)
    best_score, best_name, best_content, best_url = 0.0, None, None, None

    headers = {"Authorization": f"token {github_token}"} if github_token else {}
    # ✅ point directly to your /knowledge folder
    base_api = f"https://api.github.com/repos/{kb_repo}/contents/{kb_path}"
    base_blob = f"https://github.com/{kb_repo}/blob/master/{kb_path}"

    try:
        resp = requests.get(base_api, headers=headers, timeout=10)
        resp.raise_for_status()
        items = resp.json()

        for file in items:
            if not file["name"].endswith(".md"):
                continue

            raw_content = requests.get(file["download_url"], headers=headers, timeout=10).text
            vec = embed_text(raw_content)
            score = cosine_similarity(query_vec, vec)
            if score > best_score:
                best_score = score
                best_name, best_content = file["name"], raw_content
                best_url = f"{base_blob}/{file['name']}"

    except Exception as e:
        print(f"⚠️ KB fetch error: {e}")

    return {
        "file": best_name,
        "content": best_content,
        "url": best_url,
        "score": round(best_score, 3)
    }
