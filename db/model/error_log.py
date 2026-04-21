from sqlalchemy import Text
from db.common import Column, String, DateTime, Integer, Enum, func, Base
from db.global_enums import ErrorType


class ErrorLog(Base):
    __tablename__ = "error_log"
    # "yyyymmdd_hhmmss.ffffff" — lexicographically chronological
    id = Column(String, primary_key=True, index=True)
    manga_id = Column(Integer, nullable=True, index=True)
    location = Column(String, nullable=False, index=True)  # "module.function"
    error_type = Column(Enum(ErrorType), nullable=False, index=True)
    remark = Column(String, nullable=False)
    exception = Column(String, nullable=True)  # exception class name
    traceback = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), index=True)
