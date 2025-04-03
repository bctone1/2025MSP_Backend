from langchain_service.embeddings.get_vector import text_to_vector
from langchain_service.llms.setup import get_llm
from crud.langchain import *
from langchain.prompts import PromptTemplate
from sqlalchemy.orm import Session
import numpy as np

def get_relevant_messages(db: Session, session_id: str, query_vector: list, top_n=5):
    """
    벡터 검색을 수행하여 가장 유사한 대화 기록을 반환하는 함수
    """
    history_messages = get_chat_history(db, session_id)
    print(f"✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅history message : {history_messages}✅✅✅✅✅✅✅✅✅✅✅")
    # 벡터가 없는 경우 (최초 대화)
    if not history_messages:
        return []

    # 벡터 유사도 계산 (코사인 유사도)
    def cosine_similarity(vec1, vec2):
        vec1, vec2 = np.array(vec1), np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    # 각 메시지의 벡터와 유사도 계산
    ranked_messages = []
    for msg in history_messages:
        vector = msg.get("vector_memory")
        print(f"✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅history message : {vector}✅✅✅✅✅✅✅✅✅✅✅")
        if vector is not None and len(vector) > 0 and len(vector) == len(query_vector):  # 벡터가 존재하는 경우
            similarity = cosine_similarity(query_vector, msg["vector_memory"])
            ranked_messages.append((similarity, msg))

    # 유사도가 높은 순으로 정렬 후 상위 N개 선택
    ranked_messages.sort(reverse=True, key=lambda x: x[0])
    relevant_messages = [msg for _, msg in ranked_messages[:top_n]]

    return relevant_messages

