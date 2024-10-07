from pydantic import BaseModel
from datetime import date

class InstituteCreate(BaseModel):
    institute_name: str

class CourseCreate(BaseModel):
    institute_id: int
    course_name: str

class StudentCreate(BaseModel):
    institute_id: int
    course_id: int
    student_name: str
    joining_date: date
