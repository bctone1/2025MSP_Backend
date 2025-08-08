from sqlalchemy.orm import Session
from sqlalchemy import select
from models.llm import ConversationLog
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

class ChatHistoryManager:
    def __init__(self, db: Session, session_id: int):
        self.db = db
        self.session_id = session_id

    def get_messages(self):
        stmt = select(ConversationLog).where(ConversationLog.session_id == self.session_id).order_by(
            ConversationLog.request_at)
        results = self.db.execute(stmt).scalars().all()

        messages = []
        for msg in results:
            if msg.message_role == "system":
                messages.append(SystemMessage(content=msg.conversation))
            elif msg.message_role == "ai":
                messages.append(AIMessage(content=msg.conversation))
            elif msg.message_role == "human":
                messages.append(HumanMessage(content=msg.conversation))

        return messages





