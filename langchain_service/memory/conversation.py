from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, PostgresChatMessageHistory
import core.config as config


def get_memory(session_id, memory_type="buffer", window_size=5):
    """
    대화 메모리 인스턴스를 반환합니다.
    """
    if memory_type == "postgres":
        # PostgreSQL에 채팅 기록 저장
        history = PostgresChatMessageHistory(
            connection_string=config.VECTOR_DB_CONNECTION,
            session_id=session_id,
            table_name="chat_history"
        )
        return ConversationBufferMemory(memory_key="chat_history", chat_memory=history)

    elif memory_type == "window":
        # 최근 N개 메시지만 기억
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=window_size
        )

    else:
        # 기본 메모리 (모든 메시지 기억)
        return ConversationBufferMemory(memory_key="chat_history")