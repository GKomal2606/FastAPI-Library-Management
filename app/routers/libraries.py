from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_active_user


router = APIRouter(
    prefix="/api/libraries",
    tags=["libraries"]
)


# ============================================
# CREATE LIBRARY
# ============================================

@router.post("/", response_model=schemas.Library, status_code=status.HTTP_201_CREATED)
def create_library(
    library: schemas.LibraryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new library.
    Only authenticated users can create libraries.
    """
    
    db_library = models.Library(
        name=library.name,
        location=library.location,
        description=library.description,
        user_id=current_user.id
    )
    
    db.add(db_library)
    db.commit()
    db.refresh(db_library)
    
    return db_library


# ============================================
# GET ALL LIBRARIES
# ============================================

@router.get("/", response_model=List[schemas.Library])
def get_libraries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all libraries.
    Returns all libraries in the system.
    """
    
    libraries = db.query(models.Library).offset(skip).limit(limit).all()
    return libraries


# ============================================
# GET MY LIBRARIES
# ============================================

@router.get("/my-libraries", response_model=List[schemas.Library])
def get_my_libraries(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get libraries created by current user.
    """
    
    libraries = db.query(models.Library).filter(
        models.Library.user_id == current_user.id
    ).all()
    
    return libraries


# ============================================
# GET LIBRARY BY ID
# ============================================

@router.get("/{library_id}", response_model=schemas.LibraryWithBooks)
def get_library(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get a specific library by ID with its books.
    """
    
    library = db.query(models.Library).filter(
        models.Library.id == library_id
    ).first()
    
    if not library:
        raise HTTPException(
            status_code=404,
            detail="Library not found"
        )
    
    return library


# ============================================
# UPDATE LIBRARY
# ============================================

@router.put("/{library_id}", response_model=schemas.Library)
def update_library(
    library_id: int,
    library_update: schemas.LibraryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update a library.
    Only the creator can update their library.
    """
    
    library = db.query(models.Library).filter(
        models.Library.id == library_id
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if library.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this library"
        )
    
    # Update fields
    if library_update.name is not None:
        library.name = library_update.name
    if library_update.location is not None:
        library.location = library_update.location
    if library_update.description is not None:
        library.description = library_update.description
    
    db.commit()
    db.refresh(library)
    
    return library


# ============================================
# DELETE LIBRARY
# ============================================

@router.delete("/{library_id}")
def delete_library(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a library.
    Only the creator can delete their library.
    """
    
    library = db.query(models.Library).filter(
        models.Library.id == library_id
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    if library.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this library"
        )
    
    db.delete(library)
    db.commit()
    
    return {"message": "Library deleted successfully"}