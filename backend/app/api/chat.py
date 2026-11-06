from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_chat_service, get_current_user
from app.models.user import User
from app.schemas.chat import ChatDetail, ChatRead, ChatRequest
from app.services.chat_service import ChatService, stream_answer

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("", response_model=list[ChatRead])
def list_chats(repo_id: int, user: User = Depends(get_current_user), service: ChatService = Depends(get_chat_service)):
    return service.list_chats(user, repo_id)


@router.get("/{chat_id}", response_model=ChatDetail)
def get_chat(chat_id: int, user: User = Depends(get_current_user), service: ChatService = Depends(get_chat_service)):
    return service.get_chat(user, chat_id)


@router.delete("/{chat_id}", status_code=204)
def delete_chat(chat_id: int, user: User = Depends(get_current_user), service: ChatService = Depends(get_chat_service)):
    service.delete_chat(user, chat_id)


@router.post("/stream")
def stream_chat(data: ChatRequest, user: User = Depends(get_current_user), service: ChatService = Depends(get_chat_service)):
    turn = service.prepare_turn(user, data)
    return StreamingResponse(
        stream_answer(turn), media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
