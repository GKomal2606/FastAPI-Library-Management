# ============================================
# CELERY TASK MANAGEMENT ENDPOINTS
# ============================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models
from ..database import get_db
from ..auth import get_current_active_user
from ..tasks import (
    generate_library_report,
    generate_user_statistics,
    import_books_bulk,
    send_bulk_notification
)


router = APIRouter(
    prefix="/api/tasks",
    tags=["background-tasks"]
)


# ============================================
# TRIGGER BACKGROUND TASKS
# ============================================

@router.post("/generate-library-report/{library_id}")
def trigger_library_report(
    library_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Trigger library report generation (runs in background).
    """
    
    library = db.query(models.Library).filter(
        models.Library.id == library_id
    ).first()
    
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    
    # Start background task
    task = generate_library_report.delay(library_id)
    
    return {
        "message": "Report generation started",
        "task_id": task.id,
        "status": "processing"
    }


@router.post("/generate-my-statistics")
def trigger_user_statistics(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Generate statistics for current user (runs in background).
    """
    
    task = generate_user_statistics.delay(current_user.id)
    
    return {
        "message": "Statistics generation started",
        "task_id": task.id,
        "status": "processing"
    }


@router.post("/import-books-bulk")
def trigger_bulk_import(
    books: List[dict],
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Import multiple books at once (runs in background).
    
    Example request body:
    [
        {
            "title": "Book 1",
            "author": "Author 1",
            "isbn": "123456",
            "published_year": 2020
        },
        {
            "title": "Book 2",
            "author": "Author 2",
            "published_year": 2021
        }
    ]
    """
    
    task = import_books_bulk.delay(books, current_user.id)
    
    return {
        "message": f"Bulk import started for {len(books)} books",
        "task_id": task.id,
        "status": "processing"
    }


@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    """
    Check status of a background task.
    """
    from ..celery_app import celery_app
    
    task = celery_app.AsyncResult(task_id)
    
    return {
        "task_id": task_id,
        "status": task.state,
        "result": task.result if task.ready() else None
    }