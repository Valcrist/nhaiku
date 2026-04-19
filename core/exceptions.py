from typing import Any
from fastapi import HTTPException
from toolbox.exceptions import ToolboxError, ToolboxWarning
from toolbox.utils import err, warn


class LoggedHTTPException(HTTPException):
    """HTTP exception with logging support."""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: dict[str, str] | None = None,
        level: str = "EXCEPTION",
        log_exc: bool = False,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        if level == "EXCEPTION":
            warn(f"[{level}:{status_code}] {detail}", traceback=log_exc)
        else:
            err(f"[{level}:{status_code}] {detail}", traceback=log_exc)


class NHaikuError(ToolboxError):
    """Base exception for NHaiku application errors."""

    pass


class NHaikuWarning(ToolboxWarning):
    """Base warning for NHaiku application warnings."""

    pass
