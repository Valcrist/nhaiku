from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from db.global_enums import ErrorType


class ErrorLogCreate(BaseModel):
    id: str
    manga_id: Optional[int] = None
    location: str
    error_type: ErrorType
    remark: str
    exception: Optional[str] = None
    traceback: Optional[str] = None


class ErrorLogSchema(ErrorLogCreate):
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
