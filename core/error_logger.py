import traceback as tb
from datetime import datetime, timezone
from typing import Optional
from db.global_enums import ErrorType
from db.model.error_log import ErrorLog
from db.session import AsyncSessionLocal
from toolbox.utils import err


def _make_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%d_%H%M%S.") + f"{now.microsecond:06d}"


async def log_error(
    location: str,
    remark: str,
    error_type: ErrorType = ErrorType.unknown,
    exc: BaseException | None = None,
    manga_id: int | None = None,
) -> None:
    exc_name = type(exc).__name__ if exc is not None else None
    exc_tb = "".join(tb.format_exception(exc)) if exc is not None else None
    entry = ErrorLog(
        id=_make_id(),
        manga_id=manga_id,
        location=location,
        error_type=error_type,
        remark=remark,
        exception=exc_name,
        traceback=exc_tb,
    )
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(entry)
    except Exception as db_exc:
        # DB is down — fall back to stderr so errors are never silently lost
        err(
            f"[error_logger] Failed to write error log to DB: {db_exc}", traceback=False
        )
        err(
            f"[error_logger] Original error @ {location} ({error_type}): {remark}",
            traceback=False,
        )
        if exc_tb:
            err(exc_tb)
