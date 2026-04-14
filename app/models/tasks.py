from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskInvite(BaseModel):
    email: EmailStr


class TaskInviteOut(BaseModel):
    user_id: str
    email: EmailStr
    access: str = "normal"


class TaskOut(TaskBase):
    id: str
    owner_id: str
    access: str = "normal"
    invited_users: list[TaskInviteOut] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
