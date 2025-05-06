from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserModel(BaseModel):
    userId: int
    email: EmailStr
    password: str
    name: str
    deleted: Optional[bool] = False

class LikeModel(BaseModel):
    userId: int
    animeId: int

class ClickModel(BaseModel):
    userId: int
    animeId: int
    clickCount: int = Field(default=1)