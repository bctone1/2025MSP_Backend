from crud.llm import *
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
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

def get_session_log_by_user_info(
    db: Session,
    user_email: str,
    embedding_message: list[float],
    top_k: int = 5
) -> str:
    vector_str = "[" + ",".join(map(str, embedding_message)) + "]"

    query = text("""
        SELECT id, message_role, conversation, vector_memory <-> CAST(:embedding AS vector) AS distance
        FROM conversation_logs
        WHERE user_email = :user_email
        ORDER BY distance ASC
        LIMIT :top_k;
    """)

    rows = db.execute(query, {
        "embedding": vector_str,
        "user_email": user_email,
        "top_k": top_k
    }).fetchall()

    if not rows:
        return ""

    # id로 정렬 후 message_role: conversation 형식으로 묶기
    sorted_rows = sorted(rows, key=lambda row: row._mapping["id"])

    chat_lines = [
        f"{row._mapping['message_role']}: {row._mapping['conversation']}"
        for row in sorted_rows
    ]

    return "\n".join(chat_lines)