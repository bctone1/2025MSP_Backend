from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_community.chat_message_histories import PostgresChatMessageHistory
import core.config as config


def get_memory(session_id, memory_type="buffer", window_size=5):
    """
    대화 메모리 인스턴스를 반환합니다.
    """
    if memory_type == "postgres":
        history = PostgresChatMessageHistory(
            connection_string=config.VECTOR_DB_CONNECTION,
            session_id=session_id,
            table_name="chat_history"
        )
        return ConversationBufferMemory(memory_key="chat_history", chat_memory=history)

    elif memory_type == "window":
        return ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=window_size
        )

    else:
        return ConversationBufferMemory(memory_key="chat_history")