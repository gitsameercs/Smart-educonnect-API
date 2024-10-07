from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import text
from sqlalchemy.orm import aliased

def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()


def create_institute(db: Session, institute: schemas.InstituteCreate):
    db_institute = models.Institute(institute_name=institute.institute_name)
    db.add(db_institute)
    db.commit()
    db.refresh(db_institute)
    return db_institute

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# Add other CRUD operations for fetching and updating records

def get_student_enrollment_report(db: Session):
    report_query = text("""
        SELECT * FROM report_student_enrollment();
    """)
    result = db.execute(report_query)
    return result.fetchall()

def search_records(db: Session, search_term: str):
    # Define aliases for the tables
    InstituteAlias = aliased(models.Institute)
    CourseAlias = aliased(models.Course)
    StudentAlias = aliased(models.Student)

    # Perform the search across all relevant tables
    results = db.query(InstituteAlias.institute_name, CourseAlias.course_name, StudentAlias.student_name, StudentAlias.joining_date).\
        join(CourseAlias, CourseAlias.institute_id == InstituteAlias.institute_id).\
        join(StudentAlias, StudentAlias.course_id == CourseAlias.course_id).\
        filter(
            InstituteAlias.institute_name.ilike(f"%{search_term}%") |
            CourseAlias.course_name.ilike(f"%{search_term}%") |
            StudentAlias.student_name.ilike(f"%{search_term}%")
        ).all()

    return results


