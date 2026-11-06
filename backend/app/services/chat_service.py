"""Repository chat: retrieve relevant code, build the prompt, stream the answer."""
import json
from collections.abc import Iterator
from dataclasses import dataclass

from app.ai import providers
from app.ai.llm import LLM, LLMMessage
from app.ai.prompts import CHAT_SYSTEM_PROMPT, build_chat_prompt
from app.ai.retriever import Retriever
from app.core.exceptions import ChatNotFoundError, LLMError, RepoNotFoundError, RepoNotIndexedError
from app.database.session import SessionLocal
from app.models.chat import Chat
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.repo_repository import RepoRepository
from app.schemas.chat import ChatRequest, SourceRef

HISTORY_LIMIT = 6


@dataclass
class PreparedTurn:
    chat_id: int
    messages: list[LLMMessage]
    sources: list[SourceRef]
    llm: LLM


class ChatService:
    def __init__(self, chats: ChatRepository, repos: RepoRepository, top_k: int) -> None:
        self.chats = chats
        self.repos = repos
        self.top_k = top_k

    def list_chats(self, user: User, repo_id: int) -> list[Chat]:
        return self.chats.list_for_repo(user.id, repo_id)

    def get_chat(self, user: User, chat_id: int) -> Chat:
        chat = self.chats.get_for_user(user.id, chat_id)
        if chat is None:
            raise ChatNotFoundError()
        return chat

    def delete_chat(self, user: User, chat_id: int) -> None:
        self.chats.delete(self.get_chat(user, chat_id))

    def prepare_turn(self, user: User, data: ChatRequest) -> PreparedTurn:
        repo = self.repos.get_for_user(user.id, data.repo_id)
        if repo is None:
            raise RepoNotFoundError()
        if repo.index_status != "ready":
            raise RepoNotIndexedError(f"Repository is not ready for chat (status: {repo.index_status})")
        llm = providers.get_llm()

        if data.chat_id is None:
            chat = self.chats.create(user.id, repo.id, title=data.message[:60])
        else:
            chat = self.chats.get_for_user(user.id, data.chat_id)
            if chat is None or chat.repo_id != repo.id:
                raise ChatNotFoundError()

        history = self.chats.recent_messages(chat.id, HISTORY_LIMIT)
        last_question = [m.content for m in history if m.role == "user"][-1:]
        retriever = Retriever(providers.get_embedder(), providers.get_vector_store(), self.top_k)
        hits = retriever.search(repo.id, " ".join([*last_question, data.message]))

        self.chats.add_message(chat.id, "user", data.message, None)
        prompt = build_chat_prompt(repo.full_name, data.message, hits)
        messages = [LLMMessage(m.role, m.content) for m in history] + [LLMMessage("user", prompt)]
        sources = [SourceRef(path=h.path, start_line=h.start_line, end_line=h.end_line) for h in hits]
        return PreparedTurn(chat.id, messages, sources, llm)


def _event(payload: dict) -> str:
    return json.dumps(payload) + "\n"


def stream_answer(turn: PreparedTurn) -> Iterator[str]:
    sources = [s.model_dump() for s in turn.sources]
    yield _event({"type": "meta", "chat_id": turn.chat_id, "sources": sources})

    parts: list[str] = []
    try:
        for token in turn.llm.stream(CHAT_SYSTEM_PROMPT, turn.messages):
            parts.append(token)
            yield _event({"type": "token", "text": token})
    except LLMError as exc:
        yield _event({"type": "error", "message": str(exc)})
        return
    if not parts:
        yield _event({"type": "error", "message": "The model returned an empty answer"})
        return

    with SessionLocal() as db:
        ChatRepository(db).add_message(turn.chat_id, "assistant", "".join(parts), sources)
    yield _event({"type": "done"})
