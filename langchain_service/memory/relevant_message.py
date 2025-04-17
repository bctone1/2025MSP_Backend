from crud.langchain import *
from sqlalchemy.orm import Session
import numpy as np

def get_relevant_messages(db: Session, session_id: str, query_vector: list, top_n=5):
    history_messages = get_chat_history(db, session_id)
    print(f"✅ history_messages : {history_messages}")
    if not history_messages:
        return []

    def cosine_similarity(vec1, vec2):
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    ranked_messages = []
    for msg in history_messages:
        vector = msg.get("vector_memory")
        if vector is not None and len(vector) > 0 and len(vector) == len(query_vector):
            similarity = cosine_similarity(query_vector, msg["vector_memory"])
            ranked_messages.append((similarity, msg))

    ranked_messages.sort(reverse=True, key=lambda x: x[0])
    relevant_messages = [msg for _, msg in ranked_messages[:top_n]]

    return relevant_messages

