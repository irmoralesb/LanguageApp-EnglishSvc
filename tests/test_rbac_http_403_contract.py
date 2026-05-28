"""
HTTP contract for RBAC failures: Prepositions API returns 403 with JSON body
when ``MissingRoleError`` is raised (see ``main.role_exception_handler``).

This is what the browser Network tab should show for app-level RBAC 403s
(vs a proxy/WAF 403, which is usually HTML or a generic body without ``role``).
"""

import asyncio
import json
from unittest.mock import MagicMock

from domain.exceptions.auth_errors import MissingPermissionError, MissingRoleError


def test_missing_role_handler_returns_403_with_role_field() -> None:
    from main import role_exception_handler

    resp = asyncio.run(
        role_exception_handler(
            MagicMock(), MissingRoleError("english-user")
        )
    )
    assert resp.status_code == 403
    body = json.loads(resp.body.decode())
    assert "detail" in body
    assert body.get("role") == "english-user"


def test_missing_permission_handler_returns_403_with_resource_action() -> None:
    from main import permission_exception_handler

    exc = MissingPermissionError(resource="PracticeTerm", action="delete")
    resp = asyncio.run(permission_exception_handler(MagicMock(), exc))
    assert resp.status_code == 403
    body = json.loads(resp.body.decode())
    assert "detail" in body
    assert body.get("resource") == "PracticeTerm"
    assert body.get("action") == "delete"
