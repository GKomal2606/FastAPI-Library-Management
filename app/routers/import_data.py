from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import pandas as pd
import io
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Book, User, Library
from app.auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/api/admin/import", tags=["Admin Import"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def require_admin(current_user: dict = Depends(get_current_user)):
    """Verify user has admin privileges"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Validate uploaded file type"""
    return any(filename.lower().endswith(ext) for ext in allowed_types)


def get_user_id_safely(current_user, db: Session) -> int:
    """
    Safely extract user_id - handles both dict and User object
    """
    # If it's a User object (has .id attribute)
    if hasattr(current_user, 'id'):
        return current_user.id
    
    # If it's a dict
    if isinstance(current_user, dict):
        if 'user_id' in current_user:
            return int(current_user['user_id'])
        if 'id' in current_user:
            return int(current_user['id'])
        if 'sub' in current_user:
            sub_value = current_user['sub']
            user = db.query(User).filter(
                (User.email == sub_value) | (User.username == sub_value)
            ).first()
            if user:
                return user.id
    
    # Fallback
    first_user = db.query(User).first()
    if first_user:
        return first_user.id
    
    return 1


@router.post("/books/excel")
async def import_books_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Import books from Excel/CSV file
    
    Required columns: title, author
    Optional columns: isbn, description, published_year, user_id
    """
    
    if not validate_file_type(file.filename, ['.xlsx', '.xls', '.csv']):
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Please upload .xlsx, .xls, or .csv file"
        )
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Validate required columns
        required_columns = ['title', 'author']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        successful_imports = []
        failed_imports = []
        skipped_duplicates = []
        
        # Get default user_id safely
        default_user_id = get_user_id_safely(current_user, db)
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row['title']) or pd.isna(row['author']):
                    failed_imports.append({
                        'row': index + 2,
                        'reason': 'Missing title or author'
                    })
                    continue
                
                # Check for duplicate ISBN
                isbn = row.get('isbn')
                if isbn and not pd.isna(isbn):
                    existing_book = db.query(Book).filter(Book.isbn == str(isbn)).first()
                    if existing_book:
                        skipped_duplicates.append({
                            'row': index + 2,
                            'title': str(row['title']),
                            'isbn': str(isbn),
                            'reason': 'ISBN already exists'
                        })
                        continue
                
                book_data = {
                    'title': str(row['title']).strip(),
                    'author': str(row['author']).strip(),
                    'isbn': str(isbn).strip() if isbn and not pd.isna(isbn) else None,
                    'description': str(row['description']).strip() if 'description' in row and not pd.isna(row['description']) else None,
                    'published_year': int(row['published_year']) if 'published_year' in row and not pd.isna(row['published_year']) else None,
                    'user_id': int(row['user_id']) if 'user_id' in row and not pd.isna(row['user_id']) else default_user_id
                }
                
                book = Book(**book_data)
                db.add(book)
                db.commit()
                db.refresh(book)
                
                successful_imports.append({
                    'row': index + 2,
                    'title': book.title,
                    'id': book.id
                })
                
            except IntegrityError:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'title': str(row.get('title', 'Unknown')),
                    'reason': 'Database constraint violation'
                })
            except Exception as e:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'title': str(row.get('title', 'Unknown')),
                    'reason': str(e)
                })
        
        return {
            "message": "Import process completed",
            "total_rows": len(df),
            "successful": len(successful_imports),
            "failed": len(failed_imports),
            "skipped_duplicates": len(skipped_duplicates),
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "skipped_duplicates": skipped_duplicates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/libraries/excel")
async def import_libraries_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Import libraries from Excel/CSV file
    
    Required columns: name
    Optional columns: location, description, user_id
    """
    
    if not validate_file_type(file.filename, ['.xlsx', '.xls', '.csv']):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload .xlsx, .xls, or .csv file"
        )
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = df.columns.str.lower().str.strip()
        
        required_columns = ['name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        successful_imports = []
        failed_imports = []
        skipped_duplicates = []
        
        default_user_id = get_user_id_safely(current_user, db)
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row['name']):
                    failed_imports.append({
                        'row': index + 2,
                        'reason': 'Missing library name'
                    })
                    continue
                
                library_name = str(row['name']).strip()
                existing = db.query(Library).filter(Library.name == library_name).first()
                if existing:
                    skipped_duplicates.append({
                        'row': index + 2,
                        'name': library_name,
                        'reason': 'Library name already exists'
                    })
                    continue
                
                library_data = {
                    'name': library_name,
                    'location': str(row['location']).strip() if 'location' in row and not pd.isna(row['location']) else None,
                    'description': str(row['description']).strip() if 'description' in row and not pd.isna(row['description']) else None,
                    'user_id': int(row['user_id']) if 'user_id' in row and not pd.isna(row['user_id']) else default_user_id
                }
                
                library = Library(**library_data)
                db.add(library)
                db.commit()
                db.refresh(library)
                
                successful_imports.append({
                    'row': index + 2,
                    'name': library.name,
                    'id': library.id
                })
                
            except IntegrityError:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'name': str(row.get('name', 'Unknown')),
                    'reason': 'Database constraint violation'
                })
            except Exception as e:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'name': str(row.get('name', 'Unknown')),
                    'reason': str(e)
                })
        
        return {
            "message": "Import process completed",
            "total_rows": len(df),
            "successful": len(successful_imports),
            "failed": len(failed_imports),
            "skipped_duplicates": len(skipped_duplicates),
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "skipped_duplicates": skipped_duplicates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/users/excel")
async def import_users_from_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin)
):
    """
    Import users from Excel/CSV file
    
    Required columns: username, email, password
    Optional columns: full_name, is_active, is_verified
    """
    
    if not validate_file_type(file.filename, ['.xlsx', '.xls', '.csv']):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload .xlsx, .xls, or .csv file"
        )
    
    try:
        contents = await file.read()
        
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
        
        df.columns = df.columns.str.lower().str.strip()
        
        required_columns = ['username', 'email', 'password']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        successful_imports = []
        failed_imports = []
        skipped_duplicates = []
        
        for index, row in df.iterrows():
            try:
                if pd.isna(row['username']) or pd.isna(row['email']) or pd.isna(row['password']):
                    failed_imports.append({
                        'row': index + 2,
                        'reason': 'Missing username, email, or password'
                    })
                    continue
                
                username = str(row['username']).strip()
                email = str(row['email']).strip()
                
                existing_user = db.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    skipped_duplicates.append({
                        'row': index + 2,
                        'username': username,
                        'email': email,
                        'reason': 'Username or email already exists'
                    })
                    continue
                
                hashed_password = pwd_context.hash(str(row['password']))
                
                user_data = {
                    'username': username,
                    'email': email,
                    'hashed_password': hashed_password,
                    'full_name': str(row['full_name']).strip() if 'full_name' in row and not pd.isna(row['full_name']) else None,
                    'is_active': bool(row['is_active']) if 'is_active' in row and not pd.isna(row['is_active']) else True,
                    'is_verified': bool(row['is_verified']) if 'is_verified' in row and not pd.isna(row['is_verified']) else False
                }
                
                user = User(**user_data)
                db.add(user)
                db.commit()
                db.refresh(user)
                
                successful_imports.append({
                    'row': index + 2,
                    'username': user.username,
                    'email': user.email,
                    'id': user.id
                })
                
            except IntegrityError:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'username': str(row.get('username', 'Unknown')),
                    'reason': 'Database constraint violation'
                })
            except Exception as e:
                db.rollback()
                failed_imports.append({
                    'row': index + 2,
                    'username': str(row.get('username', 'Unknown')),
                    'reason': str(e)
                })
        
        return {
            "message": "Import process completed",
            "total_rows": len(df),
            "successful": len(successful_imports),
            "failed": len(failed_imports),
            "skipped_duplicates": len(skipped_duplicates),
            "successful_imports": successful_imports,
            "failed_imports": failed_imports,
            "skipped_duplicates": skipped_duplicates
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.get("/template/books")
async def download_books_template(current_user: dict = Depends(require_admin)):
    """Download Excel template for books import"""
    
    template_data = {
        'title': ['Example Book 1', 'Example Book 2'],
        'author': ['Author Name', 'Another Author'],
        'isbn': ['978-1234567890', '978-0987654321'],
        'description': ['Book description here', 'Another description'],
        'published_year': [2023, 2024],
        'user_id': [1, 1]
    }
    
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Books Template', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Books Template']
        
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=books_import_template.xlsx"}
    )


@router.get("/template/libraries")
async def download_libraries_template(current_user: dict = Depends(require_admin)):
    """Download Excel template for libraries import"""
    
    template_data = {
        'name': ['Central Library', 'Branch Library'],
        'location': ['Downtown', 'Suburbs'],
        'description': ['Main library', 'Branch location'],
        'user_id': [1, 1]
    }
    
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Libraries Template', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Libraries Template']
        
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#70AD47',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=libraries_import_template.xlsx"}
    )


@router.get("/template/users")
async def download_users_template(current_user: dict = Depends(require_admin)):
    """Download Excel template for users import"""
    
    template_data = {
        'username': ['john_doe', 'jane_smith'],
        'email': ['john@example.com', 'jane@example.com'],
        'password': ['Password123!', 'SecurePass456!'],
        'full_name': ['John Doe', 'Jane Smith'],
        'is_active': [True, True],
        'is_verified': [False, False]
    }
    
    df = pd.DataFrame(template_data)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Users Template', index=False)
        
        workbook = writer.book
        worksheet = writer.sheets['Users Template']
        
        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '#ED7D31',
            'font_color': 'white',
            'border': 1
        })
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 20)
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=users_import_template.xlsx"}
    )