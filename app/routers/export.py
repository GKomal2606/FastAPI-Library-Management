 
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime

from app.database import get_db
from app.models import Book, User, Library
from app.auth import get_current_user

router = APIRouter(tags=["Export"])


# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def require_admin(current_user: User = Depends(get_current_user)):
    """Verify user has admin privileges"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


def require_authenticated_user(current_user: User = Depends(get_current_user)):
    """Verify user is authenticated"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user


# ============================================
# ADMIN EXPORTS - FULL ACCESS
# ============================================

@router.get("/api/admin/export/books/excel")
async def admin_export_all_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export ALL books - Admin only"""
    try:
        books = db.query(Book).all()
        
        if not books:
            df = pd.DataFrame(columns=[
                "Book ID", "Title", "Author", "ISBN", 
                "Published Year", "Description", "Owner ID", "Created At"
            ])
        else:
            books_data = []
            for book in books:
                books_data.append({
                    "Book ID": book.id,
                    "Title": book.title,
                    "Author": book.author,
                    "ISBN": book.isbn if book.isbn else "N/A",
                    "Published Year": book.published_year if book.published_year else "N/A",
                    "Description": book.description if book.description else "N/A",
                    "Owner ID": book.user_id if book.user_id else "N/A",
                    "Created At": book.created_at.strftime("%Y-%m-%d %H:%M:%S") if book.created_at else "N/A"
                })
            df = pd.DataFrame(books_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='All Books', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['All Books']
            
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"admin_all_books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting books: {str(e)}")


@router.get("/api/admin/export/libraries/excel")
async def admin_export_all_libraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export ALL libraries - Admin only"""
    try:
        libraries = db.query(Library).all()
        
        if not libraries:
            df = pd.DataFrame(columns=[
                "Library ID", "Name", "Location", "Description", "Owner ID", "Created At"
            ])
        else:
            libraries_data = []
            for library in libraries:
                libraries_data.append({
                    "Library ID": library.id,
                    "Name": library.name,
                    "Location": library.location if library.location else "N/A",
                    "Description": library.description if library.description else "N/A",
                    "Owner ID": library.user_id if library.user_id else "N/A",
                    "Created At": library.created_at.strftime("%Y-%m-%d %H:%M:%S") if library.created_at else "N/A"
                })
            df = pd.DataFrame(libraries_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='All Libraries', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['All Libraries']
            
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#70AD47',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"admin_all_libraries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting libraries: {str(e)}")


@router.get("/api/admin/export/users/excel")
async def admin_export_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export ALL users - Admin only"""
    try:
        users = db.query(User).all()
        
        if not users:
            df = pd.DataFrame(columns=[
                "User ID", "Username", "Email", "Full Name", 
                "Is Active", "Is Verified", "Created At"
            ])
        else:
            users_data = []
            for user in users:
                users_data.append({
                    "User ID": user.id,
                    "Username": user.username,
                    "Email": user.email if user.email else "N/A",
                    "Full Name": user.full_name if user.full_name else "N/A",
                    "Is Active": "Yes" if user.is_active else "No",
                    "Is Verified": "Yes" if user.is_verified else "No",
                    "Created At": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else "N/A"
                })
            df = pd.DataFrame(users_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='All Users', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['All Users']
            
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#ED7D31',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"admin_all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting users: {str(e)}")


@router.get("/api/admin/export/complete-report/excel")
async def admin_export_complete_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Export complete database report - Admin only"""
    try:
        books = db.query(Book).all()
        libraries = db.query(Library).all()
        users = db.query(User).all()
        
        books_data = [
            {
                "ID": b.id,
                "Title": b.title,
                "Author": b.author,
                "ISBN": b.isbn if b.isbn else "N/A",
                "Published Year": b.published_year if b.published_year else "N/A",
                "Owner ID": b.user_id if b.user_id else "N/A"
            } for b in books
        ] if books else []
        
        libraries_data = [
            {
                "ID": lib.id,
                "Name": lib.name,
                "Location": lib.location if lib.location else "N/A",
                "Description": lib.description if lib.description else "N/A",
                "Owner ID": lib.user_id if lib.user_id else "N/A"
            } for lib in libraries
        ] if libraries else []
        
        users_data = [
            {
                "ID": u.id,
                "Username": u.username,
                "Email": u.email if u.email else "N/A",
                "Full Name": u.full_name if u.full_name else "N/A",
                "Active": "Yes" if u.is_active else "No",
                "Verified": "Yes" if u.is_verified else "No"
            } for u in users
        ] if users else []
        
        stats_data = [
            {"Metric": "Total Books", "Value": len(books)},
            {"Metric": "Total Libraries", "Value": len(libraries)},
            {"Metric": "Total Users", "Value": len(users)},
            {"Metric": "Active Users", "Value": sum(1 for u in users if u.is_active)},
            {"Metric": "Verified Users", "Value": sum(1 for u in users if u.is_verified)}
        ]
        
        books_df = pd.DataFrame(books_data) if books_data else pd.DataFrame(columns=["ID", "Title", "Author", "ISBN", "Published Year", "Owner ID"])
        libraries_df = pd.DataFrame(libraries_data) if libraries_data else pd.DataFrame(columns=["ID", "Name", "Location", "Description", "Owner ID"])
        users_df = pd.DataFrame(users_data) if users_data else pd.DataFrame(columns=["ID", "Username", "Email", "Full Name", "Active", "Verified"])
        stats_df = pd.DataFrame(stats_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            books_df.to_excel(writer, sheet_name='Books', index=False)
            libraries_df.to_excel(writer, sheet_name='Libraries', index=False)
            users_df.to_excel(writer, sheet_name='Users', index=False)
            
            workbook = writer.book
            
            for sheet_name in ['Statistics', 'Books', 'Libraries', 'Users']:
                worksheet = writer.sheets[sheet_name]
                
                header_format = workbook.add_format({
                    'bold': True,
                    'fg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                
                if sheet_name == 'Statistics':
                    current_df = stats_df
                elif sheet_name == 'Books':
                    current_df = books_df
                elif sheet_name == 'Libraries':
                    current_df = libraries_df
                else:
                    current_df = users_df
                
                for col_num, value in enumerate(current_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                for idx in range(len(current_df.columns)):
                    worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"admin_complete_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating complete report: {str(e)}")


# ============================================
# USER EXPORTS - PERSONAL DATA ONLY
# ============================================

@router.get("/api/user/export/my-books/excel")
async def user_export_my_books(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Export MY books only - User access"""
    try:
        user_id = current_user.id
        books = db.query(Book).filter(Book.user_id == user_id).all()
        
        if not books:
            df = pd.DataFrame(columns=[
                "Book ID", "Title", "Author", "ISBN", 
                "Published Year", "Description", "Created At"
            ])
        else:
            books_data = []
            for book in books:
                books_data.append({
                    "Book ID": book.id,
                    "Title": book.title,
                    "Author": book.author,
                    "ISBN": book.isbn if book.isbn else "N/A",
                    "Published Year": book.published_year if book.published_year else "N/A",
                    "Description": book.description if book.description else "N/A",
                    "Created At": book.created_at.strftime("%Y-%m-%d %H:%M:%S") if book.created_at else "N/A"
                })
            df = pd.DataFrame(books_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='My Books', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['My Books']
            
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#4472C4',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"my_books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting your books: {str(e)}")


@router.get("/api/user/export/my-libraries/excel")
async def user_export_my_libraries(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Export MY libraries only - User access"""
    try:
        user_id = current_user.id
        libraries = db.query(Library).filter(Library.user_id == user_id).all()
        
        if not libraries:
            df = pd.DataFrame(columns=[
                "Library ID", "Name", "Location", "Description", "Created At"
            ])
        else:
            libraries_data = []
            for library in libraries:
                libraries_data.append({
                    "Library ID": library.id,
                    "Name": library.name,
                    "Location": library.location if library.location else "N/A",
                    "Description": library.description if library.description else "N/A",
                    "Created At": library.created_at.strftime("%Y-%m-%d %H:%M:%S") if library.created_at else "N/A"
                })
            df = pd.DataFrame(libraries_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='My Libraries', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['My Libraries']
            
            header_format = workbook.add_format({
                'bold': True,
                'fg_color': '#70AD47',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, 15)
        
        output.seek(0)
        filename = f"my_libraries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting your libraries: {str(e)}")


@router.get("/api/user/export/my-data/excel")
async def user_export_my_complete_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated_user)
):
    """Export MY complete data - User access"""
    try:
        user_id = current_user.id
        books = db.query(Book).filter(Book.user_id == user_id).all()
        libraries = db.query(Library).filter(Library.user_id == user_id).all()
        user = db.query(User).filter(User.id == user_id).first()
        
        books_data = [
            {
                "ID": b.id,
                "Title": b.title,
                "Author": b.author,
                "ISBN": b.isbn if b.isbn else "N/A",
                "Published Year": b.published_year if b.published_year else "N/A"
            } for b in books
        ] if books else []
        
        libraries_data = [
            {
                "ID": lib.id,
                "Name": lib.name,
                "Location": lib.location if lib.location else "N/A",
                "Description": lib.description if lib.description else "N/A"
            } for lib in libraries
        ] if libraries else []
        
        profile_data = [{
            "Username": user.username,
            "Email": user.email if user.email else "N/A",
            "Full Name": user.full_name if user.full_name else "N/A",
            "Account Status": "Active" if user.is_active else "Inactive",
            "Verified": "Yes" if user.is_verified else "No",
            "Member Since": user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A"
        }] if user else []
        
        stats_data = [
            {"Metric": "Total Books", "Value": len(books)},
            {"Metric": "Total Libraries", "Value": len(libraries)}
        ]
        
        books_df = pd.DataFrame(books_data) if books_data else pd.DataFrame(columns=["ID", "Title", "Author", "ISBN", "Published Year"])
        libraries_df = pd.DataFrame(libraries_data) if libraries_data else pd.DataFrame(columns=["ID", "Name", "Location", "Description"])
        profile_df = pd.DataFrame(profile_data) if profile_data else pd.DataFrame(columns=["Username", "Email", "Full Name", "Account Status", "Verified", "Member Since"])
        stats_df = pd.DataFrame(stats_data)
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            profile_df.to_excel(writer, sheet_name='My Profile', index=False)
            stats_df.to_excel(writer, sheet_name='Summary', index=False)
            books_df.to_excel(writer, sheet_name='My Books', index=False)
            libraries_df.to_excel(writer, sheet_name='My Libraries', index=False)
            
            workbook = writer.book
            
            for sheet_name in ['My Profile', 'Summary', 'My Books', 'My Libraries']:
                worksheet = writer.sheets[sheet_name]
                
                header_format = workbook.add_format({
                    'bold': True,
                    'fg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                
                if sheet_name == 'My Profile':
                    current_df = profile_df
                elif sheet_name == 'Summary':
                    current_df = stats_df
                elif sheet_name == 'My Books':
                    current_df = books_df
                else:
                    current_df = libraries_df
                
                for col_num, value in enumerate(current_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                for idx in range(len(current_df.columns)):
                    worksheet.set_column(idx, idx, 18)
        
        output.seek(0)
        filename = f"my_complete_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        import traceback
        print(f"❌ Export error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error exporting your complete data: {str(e)}")