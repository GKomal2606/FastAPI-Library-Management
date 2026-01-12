from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    token: str
    new_password: str

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str


# ============================================
# LIBRARY SCHEMAS
# ============================================

class LibraryBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None

class LibraryCreate(LibraryBase):
    pass

class LibraryUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class Library(LibraryBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True


# ============================================
# BOOK SCHEMAS
# ============================================

class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    published_year: Optional[int] = None

class Book(BookBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        from_attributes = True

class BookWithLibraries(Book):
    libraries: List[Library] = []
    
    class Config:
        from_attributes = True


# ============================================
# ASSIGNMENT SCHEMAS
# ============================================

class BookLibraryAssignment(BaseModel):
    book_id: int
    library_ids: List[int]

class LibraryWithBooks(Library):
    books: List[Book] = []
    
    class Config:
        from_attributes = True