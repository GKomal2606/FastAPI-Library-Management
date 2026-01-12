\# FastAPI Library Management System with Celery



A comprehensive library management system built with FastAPI and Celery for asynchronous task processing.



\## Features

\- JWT Authentication

\- Book management (CRUD operations)

\- User management

\- Borrow/return functionality

\- Asynchronous task processing with Celery



\## Tech Stack

\- FastAPI

\- Celery

\- Redis/RabbitMQ

\- SQLAlchemy

\- PostgreSQL/MySQL/SQLite



\## Installation



1\. Clone the repository

```bash

git clone https://github.com/YOUR\_USERNAME/fastapi-library-management.git

cd fastapi-library-management

```



2\. Create virtual environment

```bash

conda create -n fastapi-auth python=3.10

conda activate fastapi-auth

```



3\. Install dependencies

```bash

pip install -r requirements.txt

```



\## Usage



1\. Start the FastAPI server

```bash

uvicorn main:app --reload

```



2\. Start Celery worker

```bash

celery -A tasks worker --loglevel=info

```



\## API Documentation

Access the interactive API docs at: `http://localhost:8000/docs`



\## License

MIT

