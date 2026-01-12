# ============================================
# IMPORTS
# ============================================

from fastapi import FastAPI
from .database import engine, Base
from .routers import users, libraries, books, tasks


# ============================================
# CREATE DATABASE TABLES
# ============================================

# Create all database tables
Base.metadata.create_all(bind=engine)

"""
What this does:
- Looks at all models (User, Library, Book)
- Creates corresponding tables in database
- Only creates if tables don't exist
- Run once at startup

Result:
Creates 'users', 'libraries', 'books', and 'book_libraries' tables
"""


# ============================================
# CREATE FASTAPI APP
# ============================================

app = FastAPI(
    title="FastAPI Library Management System with Celery",
    description="A complete library management system with JWT authentication, books, libraries, and background tasks",
    version="2.0.0"
)

"""
FastAPI app configuration:
- title: Shows in Swagger docs
- description: API description
- version: API version number

This creates the main application instance
"""


# ============================================
# INCLUDE ROUTERS
# ============================================

# Include routers
app.include_router(users.router)
app.include_router(libraries.router)
app.include_router(books.router)
app.include_router(tasks.router) 

"""
What this does:
- Adds all routes from users.router to the app
- Adds all routes from libraries.router to the app
- Adds all routes from books.router to the app

Available routes:
Users:
  - POST /api/users/signup
  - POST /api/users/login
  - GET  /api/users/me
  - PUT  /api/users/me
  - POST /api/users/forgot-password
  - POST /api/users/reset-password

Libraries:
  - POST /api/libraries/
  - GET  /api/libraries/
  - GET  /api/libraries/my-libraries
  - GET  /api/libraries/{id}
  - PUT  /api/libraries/{id}
  - DELETE /api/libraries/{id}

Books:
  - POST /api/books/
  - GET  /api/books/
  - GET  /api/books/{id}
  - PUT  /api/books/{id}
  - DELETE /api/books/{id}
  - POST /api/books/{id}/assign
  - DELETE /api/books/{id}/libraries/{library_id}
"""


# ============================================
# ROOT ENDPOINT
# ============================================

@app.get("/")
def root():
    """
    Root endpoint - API welcome message.
    
    This is the first endpoint users see when they visit:
    http://127.0.0.1:8000/
    
    Returns:
        Welcome message and links to documentation
    """
    return {
        "message": "Welcome to Library Management API",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to Library Management API with Background Tasks",
        "docs": "/docs",
        "redoc": "/redoc",
        "flower": "http://localhost:5555"  # Celery monitoring
    }


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@app.get("/health")
def health_check():
    """
    Health check endpoint.
    
    Used to verify the API is running.
    Useful for monitoring and deployment.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to Library Management API with Background Tasks",
        "docs": "/docs",
        "redoc": "/redoc",
        "flower": "http://localhost:5555"  # Celery monitoring
    }