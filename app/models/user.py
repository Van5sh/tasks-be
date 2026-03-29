from pydantic import BaseModel, EmailStr, Field
from datetime import date
from enum import Enum

class Gender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    dob: date
    gender: Gender


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
