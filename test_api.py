"""Automated test suite verifying in-memory CRUD operations, validations, and edge cases."""
import unittest
from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import ValidationError

import schemas
import main
from main import (
    create_student,
    read_students,
    read_student,
    update_student,
    delete_student,
    get_stats,
    health_check,
)


class TestStudentCRUDInMemory(unittest.TestCase):
    def setUp(self):
        # Reset in-memory database to a known state before each test
        main.students_db = {
            1: {
                "id": 1,
                "name": "Alice Smith",
                "email": "alice@university.edu",
                "age": 20,
                "course": "Computer Science",
                "gpa": 3.80,
                "created_at": datetime.now(timezone.utc),
            },
            2: {
                "id": 2,
                "name": "Bob Jones",
                "email": "bob@university.edu",
                "age": 22,
                "course": "Data Science",
                "gpa": 3.60,
                "created_at": datetime.now(timezone.utc),
            },
        }
        main.id_counter = 2

    def test_health_check(self):
        result = health_check()
        self.assertEqual(result["status"], "ok")

    def test_create_student_success(self):
        new_data = schemas.StudentCreate(
            name="Charlie Brown",
            email="charlie@university.edu",
            age=21,
            course="Physics",
            gpa=3.95,
        )
        created = create_student(student=new_data)
        self.assertEqual(created["id"], 3)
        self.assertEqual(created["name"], "Charlie Brown")
        self.assertEqual(created["email"], "charlie@university.edu")
        self.assertEqual(created["course"], "Physics")
        self.assertEqual(created["gpa"], 3.95)
        self.assertIn(3, main.students_db)

    def test_create_duplicate_email_fails(self):
        duplicate_data = schemas.StudentCreate(
            name="Alice Imposter",
            email="alice@university.edu",  # already exists
            age=21,
            course="Art",
            gpa=3.50,
        )
        with self.assertRaises(HTTPException) as ctx:
            create_student(student=duplicate_data)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("already exists", ctx.exception.detail)

    def test_pydantic_schema_validations(self):
        # Invalid email format
        with self.assertRaises(ValidationError):
            schemas.StudentCreate(
                name="Test",
                email="not-an-email",
                age=20,
                course="CS",
                gpa=3.5,
            )

        # Invalid GPA above 4.0
        with self.assertRaises(ValidationError):
            schemas.StudentCreate(
                name="Test",
                email="test@email.com",
                age=20,
                course="CS",
                gpa=4.5,
            )

        # Invalid negative age
        with self.assertRaises(ValidationError):
            schemas.StudentCreate(
                name="Test",
                email="test@email.com",
                age=-1,
                course="CS",
                gpa=3.0,
            )

    def test_read_students_and_filters(self):
        # Read all
        students = read_students(skip=0, limit=10, course=None, search=None)
        self.assertEqual(len(students), 2)

        # Filter by course
        cs_students = read_students(skip=0, limit=10, course="Computer Science", search=None)
        self.assertEqual(len(cs_students), 1)
        self.assertEqual(cs_students[0]["name"], "Alice Smith")

        # Search by keyword
        search_res = read_students(skip=0, limit=10, course=None, search="Bob")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["name"], "Bob Jones")

    def test_read_single_student_and_not_found(self):
        # Existing student
        student = read_student(student_id=1)
        self.assertEqual(student["name"], "Alice Smith")

        # Non-existing student
        with self.assertRaises(HTTPException) as ctx:
            read_student(student_id=999)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_update_student(self):
        update_data = schemas.StudentUpdate(
            name="Alice S. Johnson",
            gpa=3.99,
        )
        updated = update_student(student_id=1, student_update=update_data)
        self.assertEqual(updated["name"], "Alice S. Johnson")
        self.assertEqual(updated["gpa"], 3.99)
        # Unchanged fields remain preserved
        self.assertEqual(updated["email"], "alice@university.edu")
        self.assertEqual(updated["course"], "Computer Science")

    def test_update_duplicate_email_conflict(self):
        update_data = schemas.StudentUpdate(email="bob@university.edu")
        with self.assertRaises(HTTPException) as ctx:
            update_student(student_id=1, student_update=update_data)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("already exists", ctx.exception.detail)

    def test_delete_student(self):
        result = delete_student(student_id=2)
        self.assertEqual(result["status"], "success")
        self.assertNotIn(2, main.students_db)

        # Deleting non-existent student raises 404
        with self.assertRaises(HTTPException) as ctx:
            delete_student(student_id=2)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_stats_endpoint(self):
        stats = get_stats()
        self.assertEqual(stats["total_students"], 2)
        self.assertEqual(stats["average_gpa"], 3.70)


if __name__ == "__main__":
    unittest.main(verbosity=2)
