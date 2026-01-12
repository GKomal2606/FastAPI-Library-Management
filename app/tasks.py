# ============================================
# CELERY BACKGROUND TASKS
# ============================================

from .celery_app import celery_app
from .database import SessionLocal
from . import models
from datetime import datetime, timedelta
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)


# ============================================
# EMAIL TASKS
# ============================================

@celery_app.task(name="app.tasks.send_welcome_email")
def send_welcome_email(email: str, username: str):
    """
    Send welcome email to new user.
    Called after signup.
    """
    logger.info(f"Sending welcome email to {email}")
    
    # In production, use SendGrid, AWS SES, or similar
    # For now, just log it
    
    email_content = f"""
    Welcome to Library Management System!
    
    Hi {username},
    
    Thank you for signing up! Your account is now active.
    
    You can now:
    - Create your own libraries
    - Add books to your collection
    - Assign books to libraries
    
    Happy reading!
    """
    
    logger.info(f"Email sent to {email}")
    logger.info(email_content)
    
    return {"status": "success", "email": email}


@celery_app.task(name="app.tasks.send_password_reset_email")
def send_password_reset_email(email: str, reset_token: str):
    """
    Send password reset email.
    Called when user requests password reset.
    """
    logger.info(f"Sending password reset email to {email}")
    
    reset_link = f"http://yourdomain.com/reset-password?token={reset_token}"
    
    email_content = f"""
    Password Reset Request
    
    Hi,
    
    You requested a password reset. Click the link below to reset your password:
    
    {reset_link}
    
    This link expires in 1 hour.
    
    If you didn't request this, please ignore this email.
    """
    
    logger.info(f"Password reset email sent to {email}")
    logger.info(email_content)
    
    return {"status": "success", "email": email}


@celery_app.task(name="app.tasks.send_bulk_notification")
def send_bulk_notification(user_ids: list, message: str):
    """
    Send notification to multiple users.
    """
    logger.info(f"Sending bulk notification to {len(user_ids)} users")
    
    db = SessionLocal()
    try:
        users = db.query(models.User).filter(models.User.id.in_(user_ids)).all()
        
        for user in users:
            logger.info(f"Notification sent to {user.email}: {message}")
        
        return {"status": "success", "sent_to": len(users)}
    finally:
        db.close()


# ============================================
# REPORT GENERATION TASKS
# ============================================

@celery_app.task(name="app.tasks.generate_library_report")
def generate_library_report(library_id: int):
    """
    Generate detailed report for a library.
    Includes: total books, popular books, statistics.
    """
    logger.info(f"Generating report for library {library_id}")
    
    db = SessionLocal()
    try:
        library = db.query(models.Library).filter(
            models.Library.id == library_id
        ).first()
        
        if not library:
            return {"status": "error", "message": "Library not found"}
        
        total_books = len(library.books)
        
        report = {
            "library_id": library_id,
            "library_name": library.name,
            "total_books": total_books,
            "location": library.location,
            "created_at": str(library.created_at),
            "books": [
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                }
                for book in library.books
            ]
        }
        
        logger.info(f"Report generated for {library.name}: {total_books} books")
        
        return report
    finally:
        db.close()


@celery_app.task(name="app.tasks.generate_user_statistics")
def generate_user_statistics(user_id: int):
    """
    Generate statistics for a user.
    Includes: total books, total libraries, etc.
    """
    logger.info(f"Generating statistics for user {user_id}")
    
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        
        if not user:
            return {"status": "error", "message": "User not found"}
        
        total_books = len(user.books)
        total_libraries = len(user.libraries)
        
        stats = {
            "user_id": user_id,
            "username": user.username,
            "total_books": total_books,
            "total_libraries": total_libraries,
            "account_created": str(user.created_at),
        }
        
        logger.info(f"Statistics generated for {user.username}")
        
        return stats
    finally:
        db.close()


# ============================================
# SCHEDULED CRON JOB TASKS
# ============================================

@celery_app.task(name="app.tasks.send_daily_reminders")
def send_daily_reminders():
    """
    CRON Job: Runs daily at 9 AM
    Send reminders to users about their books.
    """
    logger.info("Running daily reminders task")
    
    db = SessionLocal()
    try:
        users = db.query(models.User).filter(models.User.is_active == True).all()
        
        reminders_sent = 0
        for user in users:
            if len(user.books) > 0:
                logger.info(f"Reminder sent to {user.email}: You have {len(user.books)} books")
                reminders_sent += 1
        
        logger.info(f"Daily reminders completed. Sent {reminders_sent} reminders.")
        
        return {
            "status": "success",
            "reminders_sent": reminders_sent,
            "timestamp": str(datetime.utcnow())
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.generate_weekly_statistics")
def generate_weekly_statistics():
    """
    CRON Job: Runs every Monday at 8 AM
    Generate weekly statistics report.
    """
    logger.info("Generating weekly statistics")
    
    db = SessionLocal()
    try:
        total_users = db.query(models.User).count()
        total_books = db.query(models.Book).count()
        total_libraries = db.query(models.Library).count()
        
        # Users created this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_this_week = db.query(models.User).filter(
            models.User.created_at >= week_ago
        ).count()
        
        stats = {
            "report_type": "weekly",
            "generated_at": str(datetime.utcnow()),
            "total_users": total_users,
            "total_books": total_books,
            "total_libraries": total_libraries,
            "new_users_this_week": new_users_this_week,
        }
        
        logger.info(f"Weekly statistics: {stats}")
        
        return stats
    finally:
        db.close()


@celery_app.task(name="app.tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    CRON Job: Runs on 1st of every month at midnight
    Clean up expired password reset tokens.
    """
    logger.info("Running monthly token cleanup")
    
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Find users with expired tokens
        expired_users = db.query(models.User).filter(
            models.User.reset_token_expires < now,
            models.User.reset_token.isnot(None)
        ).all()
        
        cleaned = 0
        for user in expired_users:
            user.reset_token = None
            user.reset_token_expires = None
            cleaned += 1
        
        db.commit()
        
        logger.info(f"Cleaned up {cleaned} expired tokens")
        
        return {
            "status": "success",
            "tokens_cleaned": cleaned,
            "timestamp": str(datetime.utcnow())
        }
    finally:
        db.close()


@celery_app.task(name="app.tasks.backup_database")
def backup_database():
    """
    CRON Job: Runs daily at 2 AM
    Create database backup.
    """
    logger.info("Starting database backup")
    
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_sql_app_{timestamp}.db"
        
        # Copy database file
        shutil.copy("sql_app.db", f"backups/{backup_name}")
        
        logger.info(f"Database backed up: {backup_name}")
        
        return {
            "status": "success",
            "backup_file": backup_name,
            "timestamp": str(datetime.utcnow())
        }
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return {"status": "error", "message": str(e)}


@celery_app.task(name="app.tasks.system_health_check")
def system_health_check():
    """
    CRON Job: Runs every 5 minutes
    Check system health and log status.
    """
    logger.info("Running system health check")
    
    db = SessionLocal()
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check counts
        user_count = db.query(models.User).count()
        book_count = db.query(models.Book).count()
        library_count = db.query(models.Library).count()
        
        health = {
            "status": "healthy",
            "database": "connected",
            "users": user_count,
            "books": book_count,
            "libraries": library_count,
            "timestamp": str(datetime.utcnow())
        }
        
        logger.info(f"System health: {health}")
        
        return health
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}
    finally:
        db.close()


# ============================================
# BULK PROCESSING TASKS
# ============================================

@celery_app.task(name="app.tasks.import_books_bulk")
def import_books_bulk(books_data: list, user_id: int):
    """
    Import multiple books at once.
    Useful for bulk CSV imports.
    """
    logger.info(f"Importing {len(books_data)} books for user {user_id}")
    
    db = SessionLocal()
    try:
        imported = 0
        failed = 0
        
        for book_data in books_data:
            try:
                book = models.Book(
                    title=book_data["title"],
                    author=book_data["author"],
                    isbn=book_data.get("isbn"),
                    description=book_data.get("description"),
                    published_year=book_data.get("published_year"),
                    user_id=user_id
                )
                db.add(book)
                imported += 1
            except Exception as e:
                logger.error(f"Failed to import book: {str(e)}")
                failed += 1
        
        db.commit()
        
        logger.info(f"Bulk import completed: {imported} succeeded, {failed} failed")
        
        return {
            "status": "completed",
            "imported": imported,
            "failed": failed,
            "timestamp": str(datetime.utcnow())
        }
    finally:
        db.close()