from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Path
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine, get_db
import os
from pathlib import Path
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse
from PIL import Image
from . import crud  
from io import BytesIO
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import io



# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add a root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

# Existing CRUD endpoints
@app.post("/institute/", response_model=schemas.InstituteCreate)
def create_institute(institute: schemas.InstituteCreate, db: Session = Depends(get_db)):
    return crud.create_institute(db=db, institute=institute)

@app.post("/course/", response_model=schemas.CourseCreate)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db=db, course=course)

@app.post("/student/", response_model=schemas.StudentCreate)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db=db, student=student)

@app.get("/institute/{institute_id}", response_model=schemas.InstituteCreate)
def get_institute_by_id(institute_id: int, db: Session = Depends(get_db)):
    institute = db.query(models.Institute).filter(models.Institute.institute_id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    return institute

@app.get("/course/{course_id}", response_model=schemas.CourseCreate)
def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.get("/student/{student_id}", response_model=schemas.StudentCreate)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/institute/{institute_id}", response_model=schemas.InstituteCreate)
def update_institute(institute_id: int, updated_institute: schemas.InstituteCreate, db: Session = Depends(get_db)):
    institute = db.query(models.Institute).filter(models.Institute.institute_id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    
    institute.institute_name = updated_institute.institute_name
    
    db.commit()
    db.refresh(institute)
    return institute

@app.put("/course/{course_id}", response_model=schemas.CourseCreate)
def update_course(course_id: int, updated_course: schemas.CourseCreate, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course.course_name = updated_course.course_name
    course.institute_id = updated_course.institute_id
    
    db.commit()
    db.refresh(course)
    return course

@app.put("/student/{student_id}", response_model=schemas.StudentCreate)
def update_student(student_id: int, updated_student: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.student_name = updated_student.student_name
    student.institute_id = updated_student.institute_id
    student.course_id = updated_student.course_id
    student.joining_date = updated_student.joining_date
    
    db.commit()
    db.refresh(student)
    return student

@app.delete("/institute/{institute_id}", response_model=schemas.InstituteCreate)
def delete_institute(institute_id: int, db: Session = Depends(get_db)):
    institute = db.query(models.Institute).filter(models.Institute.institute_id == institute_id).first()
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")

    db.delete(institute)
    db.commit()
    return institute

@app.delete("/course/{course_id}", response_model=schemas.CourseCreate)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()
    return course

@app.delete("/student/{student_id}", response_model=schemas.StudentCreate)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return student

@app.get("/student_enrollment_report/")
def get_student_enrollment_report(db: Session = Depends(get_db)):
    report = crud.get_student_enrollment_report(db)
    
    formatted_report = [
        {
            "year": row[0],
            "month": row[1],
            "institute_name": row[2],
            "course_name": row[3],
            "student_count": row[4]
        }
        for row in report
    ]
    
    return formatted_report

# Set the directory where student photos will be saved
PHOTO_DIRECTORY = "images/"

if not os.path.exists(PHOTO_DIRECTORY):
    os.makedirs(PHOTO_DIRECTORY)

@app.post("/students/{student_id}/upload_image/")
async def upload_image(student_id: int, file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_location = upload_dir / f"{student_id}_{file.filename}"

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return {"info": f"Image uploaded to {file_location}"}

@app.get("/students/{student_id}/download_id_card/")
async def download_id_card(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create an image with student details
    image = Image.new('RGB', (600, 400), color = (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Define text and font
    try:
        font = ImageFont.load_default()
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font

    text = (
        f"Student ID: {student.student_id}\n"
        f"Name: {student.student_name}\n"
        f"Course: {student.course.course_name}\n"
        f"Institute: {student.institute.institute_name}\n"
        f"Joining Date: {student.joining_date.strftime('%Y-%m-%d')}"
    )

    draw.text((10, 10), text, font=font, fill=(0, 0, 0))

    # Save the image to a BytesIO object
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    return StreamingResponse(image_bytes, media_type="image/png", headers={"Content-Disposition": f"attachment; filename=student_{student_id}_id_card.png"})


@app.get("/search/")
def search(search_term: str, db: Session = Depends(get_db)):
    results = crud.search_records(db, search_term)

    # Format the results
    formatted_results = [
        {
            "institute_name": result[0],
            "course_name": result[1],
            "student_name": result[2],
            "joining_date": result[3].strftime("%d %b %Y")  # Format date as "16 Sep 2024"
        }
        for result in results
    ]

    return formatted_results
