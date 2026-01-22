import sys
from datetime import datetime
from passlib.context import CryptContext

sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models import User, Book, Library

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_data():
    """Create test data for library management system"""
    db = SessionLocal()
    
    try:
        print("🚀 Creating test data for Library Management System...")
        
        # --- CREATE OR GET ADMIN USER ---
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@library.com",
                hashed_password=pwd_context.hash("Admin@123"),
                full_name="Library Admin",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"✅ Created admin user: {admin.username}")
        else:
            print(f"ℹ️  Admin user already exists (ID: {admin.id})")
        
        # --- CREATE OR GET REGULAR USER ---
        user = db.query(User).filter(User.username == "john_doe").first()
        if not user:
            # Check if email exists
            user = db.query(User).filter(User.email == "john@example.com").first()
            if user:
                print(f"ℹ️  User with email john@example.com already exists (username: {user.username})")
            else:
                user = User(
                    username="john_doe",
                    email="john@example.com",
                    hashed_password=pwd_context.hash("User@123"),
                    full_name="John Doe",
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Created user: {user.username}")
        else:
            print(f"ℹ️  User 'john_doe' already exists (ID: {user.id})")
        
        # Use admin for all operations if user wasn't created
        if not user:
            user = admin
        
        # --- CREATE LIBRARIES ---
        libraries_data = [
            {"name": "Central Library", "location": "Downtown", "description": "Main city library", "user_id": admin.id},
            {"name": "West Branch", "location": "West District", "description": "Western branch", "user_id": admin.id},
            {"name": "East Branch", "location": "East District", "description": "Eastern branch", "user_id": admin.id}
        ]
        
        created_libraries = []
        for lib_data in libraries_data:
            lib = db.query(Library).filter(Library.name == lib_data["name"]).first()
            if not lib:
                lib = Library(**lib_data)
                db.add(lib)
                db.commit()
                db.refresh(lib)
                print(f"✅ Created library: {lib_data['name']}")
            else:
                print(f"ℹ️  Library '{lib_data['name']}' already exists (ID: {lib.id})")
            created_libraries.append(lib)
        
        # --- CREATE BOOKS ---
        books_data = [
            {
                "title": "Python Programming",
                "author": "John Smith",
                "isbn": "978-1234567890",
                "description": "Comprehensive guide to Python",
                "published_year": 2023,
                "user_id": admin.id
            },
            {
                "title": "Data Science Basics",
                "author": "Jane Doe",
                "isbn": "978-0987654321",
                "description": "Introduction to data science",
                "published_year": 2022,
                "user_id": admin.id
            },
            {
                "title": "The Great Novel",
                "author": "Famous Author",
                "isbn": "978-1111222233",
                "description": "A classic work of fiction",
                "published_year": 2021,
                "user_id": user.id
            },
            {
                "title": "History of Computing",
                "author": "Tech Historian",
                "isbn": "978-4444555566",
                "description": "Evolution of computers",
                "published_year": 2020,
                "user_id": admin.id
            },
            {
                "title": "Web Development Guide",
                "author": "Web Expert",
                "isbn": "978-7777888899",
                "description": "Modern web development",
                "published_year": 2024,
                "user_id": admin.id
            }
        ]
        
        for book_data in books_data:
            book = db.query(Book).filter(Book.isbn == book_data["isbn"]).first()
            if not book:
                book = Book(**book_data)
                # Assign to first library
                if created_libraries:
                    book.libraries.append(created_libraries[0])
                db.add(book)
                db.commit()
                db.refresh(book)
                print(f"✅ Created book: {book_data['title']}")
            else:
                print(f"ℹ️  Book '{book_data['title']}' already exists (ID: {book.id})")
        
        # --- SUMMARY ---
        total_users = db.query(User).count()
        total_books = db.query(Book).count()
        total_libraries = db.query(Library).count()
        
        print("\n" + "="*60)
        print("📊 DATABASE SUMMARY")
        print("="*60)
        print(f"Total Users: {total_users}")
        print(f"Total Books: {total_books}")
        print(f"Total Libraries: {total_libraries}")
        print("="*60)
        print("\n🔐 LOGIN CREDENTIALS:")
        print("-" * 60)
        print("ADMIN LOGIN:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("-" * 60)
        print("\n✨ NEXT STEPS:")
        print("  1. Start FastAPI: uvicorn app.main:app --reload")
        print("  2. Go to: http://localhost:8000/docs")
        print("  3. Login with admin credentials")
        print("  4. Test export endpoints under 'Admin Export' section")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()