from typing import List, Dict, Tuple


def get_answer(query: str) -> Tuple[str, List[Dict]]:
    # Minimal placeholder logic for MVP. In production this would invoke
    # a local Qwen3 inference context with optional retrieved chunks.
    answer = f"Grounded answer for: {query}"
    sources = [
        {
            "path": "/docs/example.txt",
            "name": "example.txt",
            "section": "Sec 1",
            "confidence": 0.85,
        }
    ]
    return answer, sources
