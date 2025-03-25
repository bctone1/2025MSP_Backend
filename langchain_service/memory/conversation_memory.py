from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
'''
class CustomChatHistory(ChatMessageHistory):
    """LangChain 스타일의 ChatMessageHistory를 SQLAlchemy 기반으로 구현"""

    def __init__(self, db: Session, session_id: int):
        self.manager = ChatHistoryManager(db, session_id)

    def add_message(self, message):
        role = "human" if isinstance(message, HumanMessage) else "ai"
        self.manager.add_message(role, message.content, "example@example.com", 1)  # 유저 이메일, 프로젝트 ID는 예시

    def messages(self):
        return self.manager.get_messages()

def get_langchain_memory(db: Session, session_id: int):
    chat_history = CustomChatHistory(db, session_id)
    memory = ConversationBufferMemory(chat_memory=chat_history, return_messages=True)
    return memory

def ask_langchain_question(db: Session, session_id: int, user_input: str):
    memory = get_langchain_memory(db, session_id)
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    prompt = PromptTemplate(input_variables=["history", "input"], template="{history}\nHuman: {input}\nAI:")
    chain = prompt | llm | memory
    response = chain.invoke({"input": user_input})
    return response
'''