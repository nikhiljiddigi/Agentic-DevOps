import os
import numpy as np
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def embed_text(text: str) -> np.ndarray:
    try:
        res = genai.embed_content(model="models/embedding-001", content=text)
        return np.array(res["embedding"], dtype=np.float32)
    except Exception as e:
        print(f"⚠️ Embedding failed: {e}")
        return np.zeros(768, dtype=np.float32)

def cosine_similarity(a, b):
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def find_similar_issues(new_issue, all_issues, threshold=0.85):
    """Detect similar issues semantically"""
    query_vec = embed_text(f"{new_issue.get('title', '')}\n{new_issue.get('body', '')}")
    matches = []
    for issue in all_issues:
        if issue["number"] == new_issue["number"]:
            continue
        text = f"{issue.get('title', '')}\n{issue.get('body', '')}"
        vec = embed_text(text)
        score = cosine_similarity(query_vec, vec)
        if score >= threshold:
            matches.append({
                "number": issue["number"],
                "title": issue["title"],
                "score": round(score, 3)
            })
    return matches
