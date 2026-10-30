import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$")


class StudentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Alice Johnson"})
    email: str = Field(..., min_length=5, max_length=120, json_schema_extra={"example": "alice.johnson@example.com"})
    age: int = Field(..., ge=1, le=120, json_schema_extra={"example": 20})
    course: str = Field(..., min_length=1, max_length=100, json_schema_extra={"example": "Computer Science"})
    gpa: float = Field(..., ge=0.0, le=4.0, json_schema_extra={"example": 3.85})

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        clean_email = v.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError(f"'{v}' is not a valid email address.")
        return clean_email

    @field_validator("name", "course")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Field cannot be empty or only whitespace.")
        return clean


class StudentCreate(StudentBase):
    """Schema used to create a new student."""
    pass


class StudentUpdate(BaseModel):
    """Schema used to update existing student attributes. All fields are optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Alice Smith"})
    email: Optional[str] = Field(None, min_length=5, max_length=120, json_schema_extra={"example": "alice.smith@example.com"})
    age: Optional[int] = Field(None, ge=1, le=120, json_schema_extra={"example": 21})
    course: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Data Science"})
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, json_schema_extra={"example": 3.92})

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean_email = v.strip().lower()
        if not EMAIL_REGEX.match(clean_email):
            raise ValueError(f"'{v}' is not a valid email address.")
        return clean_email

    @field_validator("name", "course")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            raise ValueError("Field cannot be empty or only whitespace.")
        return clean


class StudentResponse(StudentBase):
    """Schema returned to API clients."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
