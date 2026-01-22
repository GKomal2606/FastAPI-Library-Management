# FastAPI Library Management System with Import/Export

A complete library management system featuring JWT authentication, CRUD operations, Celery background tasks, and **Excel/CSV import/export functionality**.

## 🚀 Features

- 🔐 **JWT Authentication** - Secure signup, login, password reset
- 📚 **Books Management** - Full CRUD operations
- 🏛️ **Libraries Management** - Manage multiple library locations
- 👥 **User Management** - Admin and user roles
- 🔄 **Background Tasks** - Celery integration for async processing
- 📊 **Import/Export** - Bulk data operations with Excel/CSV

### Import/Export Features ✨

**Export:**
- Download books, libraries, and users as formatted Excel files
- Generate complete database reports with multiple sheets
- Beautifully formatted with colored headers and auto-sized columns

**Import:**
- Bulk upload data from Excel or CSV files
- Automatic duplicate detection
- Comprehensive validation and error reporting
- Download pre-formatted templates

## 📋 API Endpoints

### Authentication
- `POST /api/users/signup` - Register new user
- `POST /api/users/login` - Login and get JWT token
- `GET /api/users/me` - Get current user info
- `POST /api/users/forgot-password` - Request password reset
- `POST /api/users/reset-password` - Reset password

### Books
- `GET /api/books/` - List all books
- `POST /api/books/` - Create new book
- `GET /api/books/{id}` - Get book details
- `PUT /api/books/{id}` - Update book
- `DELETE /api/books/{id}` - Delete book

### Libraries
- `GET /api/libraries/` - List all libraries
- `POST /api/libraries/` - Create library
- `GET /api/libraries/{id}` - Get library details
- `PUT /api/libraries/{id}` - Update library
- `DELETE /api/libraries/{id}` - Delete library

### Export (Admin Only)
- `GET /api/admin/export/books/excel` - Export books
- `GET /api/admin/export/libraries/excel` - Export libraries
- `GET /api/admin/export/users/excel` - Export users
- `GET /api/admin/export/complete-report/excel` - Complete report

### Import (Admin Only)
- `POST /api/admin/import/books/excel` - Import books
- `POST /api/admin/import/libraries/excel` - Import libraries
- `POST /api/admin/import/users/excel` - Import users
- `GET /api/admin/import/template/books` - Download books template
- `GET /api/admin/import/template/libraries` - Download libraries template
- `GET /api/admin/import/template/users` - Download users template

## 🛠️ Tech Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Celery** - Distributed task queue
- **Redis** - Message broker for Celery
- **Pandas** - Data processing for import/export
- **OpenPyXL/XlsxWriter** - Excel file generation
- **JWT** - Secure authentication
- **Passlib** - Password hashing

## 📦 Installation

### Prerequisites
- Python 3.11+
- Redis server
- Anaconda (optional but recommended)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/GKomal2606/FastAPI-Library-Management.git
cd FastAPI-Library-Management
```

2. **Create virtual environment**
```bash
conda create -n fastapi-auth python=3.11
conda activate fastapi-auth
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate test data** (optional)
```bash
python create_test_data.py
```

5. **Start the application**
```bash
# Terminal 1: FastAPI server
uvicorn app.main:app --reload

# Terminal 2: Celery worker
celery -A app.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Celery beat
celery -A app.celery_app beat --loglevel=info
```

## 🧪 Testing

### Test Credentials
After running `create_test_data.py`:
- **Admin User:**
  - Email: `admin@library.com`
  - Password: `Admin@123`

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📝 Usage

### Import Data
1. Download a template from the import endpoints
2. Fill in your data
3. Upload the file to the corresponding import endpoint
4. Review the import report for any errors

### Export Data
1. Authenticate as admin
2. Call the export endpoint
3. Download the formatted Excel file

## 🔧 Project Structure
```
fastapi-jwt-auth/
├── app/
│   ├── routers/
│   │   ├── books.py          # Book CRUD operations
│   │   ├── libraries.py       # Library operations
│   │   ├── users.py           # User management
│   │   ├── tasks.py           # Celery tasks
│   │   ├── export.py          # Export functionality
│   │   └── import_data.py     # Import functionality
│   ├── main.py                # FastAPI application
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── database.py            # Database connection
│   ├── auth.py                # JWT authentication
│   └── celery_app.py          # Celery configuration
├── create_test_data.py        # Test data generator
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 📊 Database Schema

- **Users** - User accounts with authentication
- **Books** - Book catalog with details
- **Libraries** - Library locations
- **Book-Libraries** - Many-to-many relationship

## 🔐 Security

- JWT token-based authentication
- Password hashing with bcrypt
- Admin-only endpoints for import/export
- Input validation on all endpoints
- SQL injection prevention via ORM

## 📈 Recent Updates

### v2.0.0 (January 2026)
- ✅ Added Excel/CSV import functionality
- ✅ Added Excel export with professional formatting
- ✅ Added template download endpoints
- ✅ Implemented duplicate detection
- ✅ Added comprehensive error handling
- ✅ Created test data generation script

## 📄 License

MIT License

## 👤 Author

**Komal G**
- GitHub: [@GKomal2606](https://github.com/GKomal2606)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## ⭐ Show your support

Give a ⭐️ if this project helped you!