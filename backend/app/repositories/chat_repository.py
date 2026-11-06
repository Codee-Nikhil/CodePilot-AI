from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat import Chat, ChatMessage


class ChatRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_repo(self, user_id: int, repo_id: int) -> list[Chat]:
        stmt = select(Chat).where(Chat.user_id == user_id, Chat.repo_id == repo_id).order_by(Chat.id.desc())
        return list(self.db.scalars(stmt))

    def count_for_user(self, user_id: int) -> int:
        return len(list(self.db.scalars(select(Chat.id).where(Chat.user_id == user_id))))

    def get_for_user(self, user_id: int, chat_id: int) -> Chat | None:
        return self.db.scalar(select(Chat).where(Chat.id == chat_id, Chat.user_id == user_id))

    def create(self, user_id: int, repo_id: int, title: str) -> Chat:
        chat = Chat(user_id=user_id, repo_id=repo_id, title=title)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def add_message(self, chat_id: int, role: str, content: str, sources: list[dict] | None) -> ChatMessage:
        message = ChatMessage(chat_id=chat_id, role=role, content=content, sources=sources)
        self.db.add(message)
        self.db.commit()
        return message

    def recent_messages(self, chat_id: int, limit: int) -> list[ChatMessage]:
        stmt = select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.id.desc()).limit(limit)
        return list(reversed(list(self.db.scalars(stmt))))

    def delete(self, chat: Chat) -> None:
        self.db.delete(chat)
        self.db.commit()
