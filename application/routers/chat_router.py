from uuid import UUID

from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    ChatSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.chat_schema import (
    CreateSessionRequest,
    ChatSessionResponse,
    ChatSessionDetailResponse,
    ChatMessageResponse,
    MessageFeedbackResponse,
    CorrectionItemResponse,
    RecommendationItemResponse,
    SendMessageRequest,
    SendMessageResponse,
)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Chat Practice"],
    dependencies=[Depends(require_role("english-user"))],
)


def _feedback_to_response(fb) -> MessageFeedbackResponse | None:
    if fb is None:
        return None
    return MessageFeedbackResponse(
        id=fb.id,
        message_id=fb.message_id,
        corrections=[
            CorrectionItemResponse(
                original=c.original, issue=c.issue, suggestion=c.suggestion
            )
            for c in fb.corrections
        ],
        recommendations=[
            RecommendationItemResponse(
                original=r.original, better_expression=r.better_expression, reason=r.reason
            )
            for r in fb.recommendations
        ],
        created_at=fb.created_at,
    )


def _message_to_response(msg) -> ChatMessageResponse:
    return ChatMessageResponse(
        id=msg.id,
        session_id=msg.session_id,
        role=msg.role,
        content=msg.content,
        created_at=msg.created_at,
        feedback=_feedback_to_response(msg.feedback),
    )


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_session(
    payload: CreateSessionRequest,
    svc: ChatSvcDep,
    current_user: CurrentUserDep,
):
    session = await svc.create_session(
        user_id=current_user.user_id,
        topic=payload.topic,
    )
    return ChatSessionResponse(
        id=session.id,
        user_id=session.user_id,
        topic=session.topic,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    svc: ChatSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    sessions = await svc.list_sessions(
        user_id=current_user.user_id, skip=skip, limit=limit
    )
    return [
        ChatSessionResponse(
            id=s.id,
            user_id=s.user_id,
            topic=s.topic,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in sessions
    ]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_session(
    session_id: UUID,
    svc: ChatSvcDep,
    current_user: CurrentUserDep,
):
    session, messages = await svc.get_session(
        user_id=current_user.user_id, session_id=session_id
    )
    return ChatSessionDetailResponse(
        id=session.id,
        user_id=session.user_id,
        topic=session.topic,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[_message_to_response(m) for m in messages],
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: UUID,
    svc: ChatSvcDep,
    current_user: CurrentUserDep,
):
    await svc.delete_session(user_id=current_user.user_id, session_id=session_id)


@router.post("/sessions/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    session_id: UUID,
    payload: SendMessageRequest,
    svc: ChatSvcDep,
    current_user: CurrentUserDep,
):
    assistant_msg, feedback = await svc.send_message(
        user_id=current_user.user_id,
        session_id=session_id,
        content=payload.content,
    )
    return SendMessageResponse(
        assistant_message=_message_to_response(assistant_msg),
        feedback=_feedback_to_response(feedback),
    )
