from pydantic import BaseModel
from typing import List, Optional

# File
class FileBase(BaseModel):
    title: str
    description: str | None = None

class File(FileBase):
    id: int
    description: str | None = None
    owner_id: int

    class Config:
        orm_mode = True

class FileSchema(BaseModel):
    own_files: list[File] = []
    shared_files: list[File] = []

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

# User
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True

class UserSchema(User):
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: bool
    files: list[File] = []

class Perm(BaseModel):
    id: int
    user_id: int
    file_id: int
    view: bool
    rename: bool
    delete: bool

    class Config:
        orm_mode = True

# Sessions
class SessionData(BaseModel):
    token: str