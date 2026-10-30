# Student CRUD REST API (100% Database-Free / In-Memory)

A lightweight, clean, and simple REST API project for managing Student records (`student_crud`), built with **FastAPI** using **pure Python in-memory storage**. 

**Zero database required**:
- ❌ No SQLite / MySQL / PostgreSQL
- ❌ No SQLAlchemy / ORM complexity
- ❌ No `.db` files or migrations
- ✅ Pure Python dictionary in-memory store
- ✅ Ultra fast, zero setup, runs instantly

---

## Features

- **Full CRUD Operations**: Create, Read, Update, Delete students
- **Search & Filtering**: Search by name/email/course and filter by course
- **Data Validation**: Strict type checking and format validation using Pydantic v2 (valid email, age between 1-120, GPA 0.0 - 4.0)
- **Built-in Web Dashboard**: Interactive UI at [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: Test all endpoints at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Preloaded Sample Data**: Comes with 5 sample student records ready to use out-of-the-box
- **Automated Tests**: 10 unit tests with 100% passing coverage

---

## Project Structure

```
student_crud/
├── main.py              # FastAPI app & in-memory store (CRUD endpoints)
├── schemas.py           # Pydantic validation schemas (Create, Update, Response)
├── static/
│   └── index.html       # Responsive Web Dashboard UI
├── test_api.py          # 10 automated test suites (All passing)
├── run.py               # One-click startup script
├── requirements.txt     # Only fastapi & uvicorn (no DB drivers)
└── README.md            # Documentation & instructions
```

---

## Quick Start

### 1. Install Dependencies
Only FastAPI and Uvicorn are needed:
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python run.py
```
*(or run: `python -m uvicorn main:app --reload`)*

Visit:
- **Web UI Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Run Automated Tests
```bash
python test_api.py
```

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Web Dashboard (Interactive HTML UI) |
| `GET` | `/docs` | Swagger UI (Interactive API documentation) |
| `GET` | `/api/health` | Health check endpoint |
| `GET` | `/api/stats` | Statistics (total students, average GPA) |
| `POST` | `/api/students` | **Create** a new student record |
| `GET` | `/api/students` | **List** students (supports `search`, `course`, `skip`, `limit`) |
| `GET` | `/api/students/{id}` | **Get** a single student by ID (returns 404 if not found) |
| `PUT` | `/api/students/{id}` | **Update** student details (partial or full) |
| `DELETE` | `/api/students/{id}` | **Delete** student by ID |

---

## Example cURL Commands

### Create a Student:
```bash
curl -X POST "http://127.0.0.1:8000/api/students" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maya Lin",
    "email": "maya.lin@university.edu",
    "age": 21,
    "course": "Computer Science",
    "gpa": 3.88
  }'
```

### Search Students:
```bash
curl -X GET "http://127.0.0.1:8000/api/students?search=Maya"
```

### Update Student GPA:
```bash
curl -X PUT "http://127.0.0.1:8000/api/students/1" \
  -H "Content-Type: application/json" \
  -d '{"gpa": 3.95}'
```

### Delete Student:
```bash
curl -X DELETE "http://127.0.0.1:8000/api/students/1"
```
