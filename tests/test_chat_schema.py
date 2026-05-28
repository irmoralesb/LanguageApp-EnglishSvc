import pytest
from pydantic import ValidationError

from application.schemas.chat_schema import CreateSessionRequest, SendMessageRequest


def test_create_session_accepts_empty_topic():
    payload = CreateSessionRequest()
    assert payload.topic is None


def test_send_message_requires_non_empty_content():
    with pytest.raises(ValidationError):
        SendMessageRequest(content="")
