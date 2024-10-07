from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Institute(Base):
    __tablename__ = 'institutes'

    institute_id = Column(Integer, primary_key=True, index=True)
    institute_name = Column(String(100), nullable=False)

    # Define the relationship with Course
    courses = relationship("Course", back_populates="institute", cascade="all, delete-orphan")

class Course(Base):
    __tablename__ = 'courses'

    course_id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.institute_id'), nullable=False)
    course_name = Column(String(100), nullable=False)

    # Define the back_populates for the Institute relationship
    institute = relationship("Institute", back_populates="courses")

    # Define the relationship with Student
    students = relationship("Student", back_populates="course", cascade="all, delete-orphan")

class Student(Base):
    __tablename__ = 'students'

    student_id = Column(Integer, primary_key=True, index=True)
    institute_id = Column(Integer, ForeignKey('institutes.institute_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.course_id'), nullable=False)
    student_name = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
   #image_path = Column(String, nullable=True)

    # Define the relationship with Course
    course = relationship("Course", back_populates="students")

    # Define the relationship with Institute
    institute = relationship("Institute")
