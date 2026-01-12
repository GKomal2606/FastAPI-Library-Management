from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


# ============================================
# ASSOCIATION TABLE (Many-to-Many)
# ============================================

book_libraries = Table(
    'book_libraries',
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True),
    Column('library_id', Integer, ForeignKey('libraries.id', ondelete='CASCADE'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)


# ============================================
# USER MODEL
# ============================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    books = relationship("Book", back_populates="owner")
    libraries = relationship("Library", back_populates="created_by_user")


# ============================================
# LIBRARY MODEL
# ============================================

class Library(Base):
    __tablename__ = "libraries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    created_by_user = relationship("User", back_populates="libraries")
    books = relationship("Book", secondary=book_libraries, back_populates="libraries")


# ============================================
# BOOK MODEL
# ============================================

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=True)
    description = Column(String)
    published_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    owner = relationship("User", back_populates="books")
    libraries = relationship("Library", secondary=book_libraries, back_populates="books")  # ← FIXED: Changed from "libraries" to "books"