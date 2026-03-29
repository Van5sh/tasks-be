from pydantic import BaseModel
from enum import Enum

class Gender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"

class User(BaseModel):
    username: str
    email: str
    password: str
    dob: str
    gender: Gender