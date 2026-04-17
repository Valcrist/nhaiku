from typing import Union, Dict, Any
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from db.model.manga import Tag
from db.schema.manga import TagSchema
from db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from helpers.exceptions import LoggedHTTPException
from toolbox.date import utc_now
from toolbox.utils import err, warn, debug


router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)
