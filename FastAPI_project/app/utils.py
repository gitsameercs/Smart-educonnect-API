import shutil
from fastapi import UploadFile
from pydf import generate_pdf

def save_student_photo(file: UploadFile, student_id: int):
    path = f"photos/{student_id}.jpg"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path

def generate_id_card(student):
    html = f"""
    <html>
        <body>
            <h1>{student.student_name}</h1>
            <p>Institute: {student.institute_name}</p>
            <p>Course: {student.course_name}</p>
            <p>Joining Date: {student.joining_date}</p>
        </body>
    </html>
    """
    pdf = generate_pdf(html)
    return pdf

