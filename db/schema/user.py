import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# -------------------------------------------------------------------------------------
# User
# -------------------------------------------------------------------------------------


class UserBase(BaseModel):
    auth0_id: Optional[str] = None
    email: Optional[str] = None


class UserUTID(BaseModel):
    id: uuid.UUID


class UserCreate(UserBase):
    pass


class UserSchema(UserBase, UserUTID):
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    auth0_id: Optional[str] = None
    email: Optional[str] = None
