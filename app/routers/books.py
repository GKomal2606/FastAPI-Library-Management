from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_active_user


router = APIRouter(
    prefix="/api/books",
    tags=["books"]
)


# ============================================
# CREATE BOOK
# ============================================

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new book.
    Book is owned by the current user.
    """
    
    # Check if ISBN already exists
    if book.isbn:
        existing_book = db.query(models.Book).filter(
            models.Book.isbn == book.isbn
        ).first()
        
        if existing_book:
            raise HTTPException(
                status_code=400,
                detail="Book with this ISBN already exists"
            )
    
    db_book = models.Book(
        title=book.title,
        author=book.author,
        isbn=book.isbn,
        description=book.description,
        published_year=book.published_year,
        user_id=current_user.id
    )
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book


# ============================================
# GET ALL BOOKS (for current user)
# ============================================

@router.get("/", response_model=List[schemas.BookWithLibraries])
def get_my_books(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all books owned by current user.
    Includes library assignments.
    """
    
    books = db.query(models.Book).filter(
        models.Book.user_id == current_user.id
    ).all()
    
    return books


# ============================================
# GET BOOK BY ID
# ============================================

@router.get("/{book_id}", response_model=schemas.BookWithLibraries)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific book by ID.
    Only owner can view their book.
    """
    
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    
    return book


# ============================================
# UPDATE BOOK
# ============================================

@router.put("/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a book.
    Only owner can update their book.
    """
    
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update fields
    if book_update.title is not None:
        book.title = book_update.title
    if book_update.author is not None:
        book.author = book_update.author
    if book_update.isbn is not None:
        book.isbn = book_update.isbn
    if book_update.description is not None:
        book.description = book_update.description
    if book_update.published_year is not None:
        book.published_year = book_update.published_year
    
    db.commit()
    db.refresh(book)
    
    return book


# ============================================
# DELETE BOOK
# ============================================

@router.delete("/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a book.
    Only owner can delete their book.
    """
    
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}


# ============================================
# ASSIGN BOOK TO LIBRARIES
# ============================================

@router.post("/{book_id}/assign", response_model=schemas.BookWithLibraries)
def assign_book_to_libraries(
    book_id: int,
    library_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Assign a book to one or more libraries.
    Only owner can assign their book.
    """
    
    # Get the book
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Clear existing assignments
    book.libraries.clear()
    
    # Add new assignments
    for library_id in library_ids:
        library = db.query(models.Library).filter(
            models.Library.id == library_id
        ).first()
        
        if not library:
            raise HTTPException(
                status_code=404,
                detail=f"Library with id {library_id} not found"
            )
        
        book.libraries.append(library)
    
    db.commit()
    db.refresh(book)
    
    return book


# ============================================
# REMOVE BOOK FROM LIBRARY
# ============================================

@router.delete("/{book_id}/libraries/{library_id}")
def remove_book_from_library(
    book_id: int,
    library_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Remove a book from a specific library.
    Only owner can remove their book assignment.
    """
    
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    library = db.query(models.Library).filter(
        models.Library.id == library_id
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if library in book.libraries:
        book.libraries.remove(library)
        db.commit()
        return {"message": "Book removed from library successfully"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Book is not assigned to this library"
        )