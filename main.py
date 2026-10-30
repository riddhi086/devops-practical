from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import schemas

app = FastAPI(
    title="Student CRUD API (In-Memory)",
    description="A simple, fast REST API for managing student records using Python in-memory storage (no database required).",
    version="2.0.0",
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# ============================================================================
# IN-MEMORY DATA STORE (No external database or SQLite file required)
# ============================================================================
students_db: dict[int, dict] = {
    1: {
        "id": 1,
        "name": "Aarav Patel",
        "email": "aarav.patel@example.com",
        "age": 20,
        "course": "Computer Science",
        "gpa": 3.85,
        "created_at": datetime.now(timezone.utc),
    },
    2: {
        "id": 2,
        "name": "Sophia Miller",
        "email": "sophia.m@example.com",
        "age": 22,
        "course": "Data Science",
        "gpa": 3.92,
        "created_at": datetime.now(timezone.utc),
    },
    3: {
        "id": 3,
        "name": "Marcus Chen",
        "email": "marcus.chen@example.com",
        "age": 21,
        "course": "Mechanical Engineering",
        "gpa": 3.40,
        "created_at": datetime.now(timezone.utc),
    },
    4: {
        "id": 4,
        "name": "Ananya Sharma",
        "email": "ananya.s@example.com",
        "age": 19,
        "course": "Information Technology",
        "gpa": 3.70,
        "created_at": datetime.now(timezone.utc),
    },
    5: {
        "id": 5,
        "name": "Lucas Rossi",
        "email": "lucas.rossi@example.com",
        "age": 23,
        "course": "Business Analytics",
        "gpa": 3.15,
        "created_at": datetime.now(timezone.utc),
    },
}

id_counter = 5


# ============================================================================
# ROUTES
# ============================================================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_ui():
    """Serves the interactive web dashboard."""
    index_path = BASE_DIR / "static" / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="""
        <h2>Student CRUD API (In-Memory) is running!</h2>
        <p>Visit <a href="/docs">/docs</a> for the interactive Swagger API documentation.</p>
        """
    )


@app.get("/api/health", tags=["Health"])
def health_check():
    """Check API health status."""
    return {"status": "ok", "message": "Student CRUD API (In-Memory) is operational"}


@app.post(
    "/api/students",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
    summary="Create a new student",
)
def create_student(student: schemas.StudentCreate):
    """
    Create a new student record in memory.

    - **name**: Full name (1-100 characters)
    - **email**: Unique and valid email address
    - **age**: Student's age (1-120)
    - **course**: Degree / program name
    - **gpa**: Cumulative GPA (0.00 to 4.00)
    """
    global id_counter

    # Check for duplicate email
    for existing in students_db.values():
        if existing["email"].lower() == student.email.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with email '{student.email}' already exists.",
            )

    id_counter += 1
    new_student = {
        "id": id_counter,
        "name": student.name,
        "email": student.email,
        "age": student.age,
        "course": student.course,
        "gpa": student.gpa,
        "created_at": datetime.now(timezone.utc),
    }
    students_db[id_counter] = new_student
    return new_student


@app.get(
    "/api/students",
    response_model=List[schemas.StudentResponse],
    tags=["Students"],
    summary="List all students",
)
def read_students(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    search: Optional[str] = Query(None, description="Search across name, email, or course"),
):
    """Retrieve list of students with optional text search, course filter, and pagination."""
    results = list(students_db.values())

    if course:
        target_course = course.lower()
        results = [s for s in results if target_course in s["course"].lower()]

    if search:
        target_search = search.lower()
        results = [
            s
            for s in results
            if target_search in s["name"].lower()
            or target_search in s["email"].lower()
            or target_search in s["course"].lower()
        ]

    # Sort by ID ascending
    results.sort(key=lambda x: x["id"])
    return results[skip : skip + limit]


@app.get(
    "/api/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Get student by ID",
)
def read_student(student_id: int):
    """Retrieve details for a single student by ID."""
    if student_id not in students_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    return students_db[student_id]


@app.put(
    "/api/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Update a student",
)
def update_student(student_id: int, student_update: schemas.StudentUpdate):
    """
    Update one or more fields of an existing student.
    Only provided fields are modified.
    """
    if student_id not in students_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )

    existing = students_db[student_id]

    # If updating email, verify uniqueness
    if student_update.email and student_update.email.lower() != existing["email"].lower():
        for s_id, s_data in students_db.items():
            if s_id != student_id and s_data["email"].lower() == student_update.email.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A student with email '{student_update.email}' already exists.",
                )

    update_fields = student_update.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        existing[field] = value

    return existing


@app.delete(
    "/api/students/{student_id}",
    status_code=status.HTTP_200_OK,
    tags=["Students"],
    summary="Delete a student",
)
def delete_student(student_id: int):
    """Delete a student record permanently by ID."""
    if student_id not in students_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found.",
        )
    student_name = students_db[student_id]["name"]
    del students_db[student_id]
    return {
        "status": "success",
        "message": f"Student with ID {student_id} ('{student_name}') has been deleted.",
    }


@app.get("/api/stats", tags=["Statistics"], summary="Get summary statistics")
def get_stats():
    """Return high-level statistics like total students count and average GPA."""
    total = len(students_db)
    if total == 0:
        return {"total_students": 0, "average_gpa": 0.0}

    avg_gpa = sum(s["gpa"] for s in students_db.values()) / total
    return {
        "total_students": total,
        "average_gpa": round(avg_gpa, 2),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
