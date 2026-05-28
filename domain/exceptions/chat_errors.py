class ChatSessionNotFoundError(Exception):
    """Raised when a chat session is not found."""

    def __init__(self, session_id: str | None = None):
        msg = f"Chat session '{session_id}' not found." if session_id else "Chat session not found."
        super().__init__(msg)


class ChatSessionAccessDeniedError(Exception):
    """Raised when a user tries to access a session that doesn't belong to them."""

    def __init__(self, session_id: str | None = None):
        msg = f"Access denied for chat session '{session_id}'." if session_id else "Access denied for chat session."
        super().__init__(msg)


class ChatLLMError(Exception):
    """Raised when the LLM call for chat or feedback fails."""

    def __init__(self, provider: str, detail: str):
        self.provider = provider
        self.detail = detail
        super().__init__(f"LLM error ({provider}): {detail}")
