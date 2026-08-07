"""System Functions"""

import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from models import Course, Registration, User, Lesson
from schemas import CoursesValidation, UserValidation
from security import verify_password, generator_hash_password
from security import create_token_jwt

UPLOADS_FOLDER = Path("uploads")

UPLOADS_FOLDER.mkdir(exist_ok=True)


def create_students(student: UserValidation, db: Session):
    """Allow peoples for create a student to acess the courses"""
    student_existance = (
        db.query(User).filter(User.name_user == student.user_name).first()
    )
    if student_existance:
        raise HTTPException(
            status_code=400, detail="Name already exists: please enter another one."
        )
    password_cript = generator_hash_password(student.password_model)
    new_student = User(
        name_user=student.user_name, password_user=password_cript, role_user="student"
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return {"message": "Welcome to our platform."}


def create_instructor(instructor: UserValidation, login_confirmation: str, db: Session):
    """Create a instructor route, responsability: manage grades, progress and courses"""
    name_validation_admnistrator = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not name_validation_admnistrator:
        raise HTTPException(status_code=404, detail="administrator not found")
    if name_validation_admnistrator.role_user != "administrator":
        raise HTTPException(
            status_code=403,
            detail="Access denied: only admnistrator can create instructors on plataform",
        )

    instructor_existence = (
        db.query(User).filter(User.name_user == instructor.user_name).first()
    )
    if instructor_existence:
        raise HTTPException(status_code=400, detail="Name already exists: insert other")
    encrypted_password = generator_hash_password(instructor.password_model)
    new_instructor = User(
        name_user=instructor.user_name,
        password_user=encrypted_password,
        role_user="instructor",
    )
    db.add(new_instructor)
    db.commit()
    db.refresh(new_instructor)
    return {"message": "Welcome to the new instructor"}


def login(db: Session, username: str, password: str):
    """Login in system and return the token"""
    existence = db.query(User).filter(User.name_user == username).first()
    if not existence:
        raise HTTPException(status_code=404, detail="Invalid credential")
    verified_password = verify_password(password, existence.password_user)
    if not verified_password:
        raise HTTPException(status_code=400, detail="Invalid credential")
    token = create_token_jwt({"sub": existence.name_user})
    return {"access_token": token, "token_type": "bearer"}


def create_course(login_confirmation: str, db: Session, course_data: CoursesValidation):
    """The instructor can create a course, and block others roles to create a course"""
    instructor_name_validation = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not instructor_name_validation:
        raise HTTPException(status_code=404, detail="Instructor not found")
    if not instructor_name_validation.role_user == "instructor":
        raise HTTPException(
            status_code=403,
            detail="Access denied: only instructors can create courses",
        )
    new_course = Course(
        course_title=course_data.title_model,
        description=course_data.description_model,
        id_instructor=instructor_name_validation.id,
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"message": "Course created with sucess"}


def create_registration(login_confirmation: str, course_name: str, db: Session):
    """Enable students to enroll in existing courses."""
    student_existence = (
        db.query(User).filter(User.name_user == login_confirmation).first()
    )
    if not student_existence:
        raise HTTPException(
            status_code=403,
            detail="Student not found",
        )
    if not student_existence.role_user == "student":
        raise HTTPException(
            status_code=403,
            detail="Only students are allowed to registration in a class",
        )

    course_existence = (
        db.query(Course).filter(Course.course_title == course_name).first()
    )
    if not course_existence:
        raise HTTPException(status_code=404, detail="Course not found")
    already_enrolled = (
        db.query(Registration)
        .filter(
            Registration.student_id == student_existence.id,
            Registration.course_id == course_existence.id,
        )
        .first()
    )
    if already_enrolled:
        raise HTTPException(
            status_code=403,
            detail="Student already enrolled in this class",
        )
    new_registration = Registration(
        student_id=student_existence.id, course_id=course_existence.id
    )

    db.add(new_registration)
    db.commit()
    db.refresh(new_registration)
    return {"message": "Registration realized with sucess"}


def list_courses(db: Session):
    """Lists the courses for each teacher"""
    courses_of_each_instructor = (
        db.query(Course).options(joinedload(Course.instructor_relationship)).all()
    )

    return courses_of_each_instructor


def add_class_course(
    db: Session,
    course_id: int,
    class_title: str,
    file: UploadFile,
    username: str,
):
    """Uploads the file and links it to a course in the database."""
    instructor_logged = db.query(User).filter(User.name_user == username).first()

    if not instructor_logged or instructor_logged.role_user != "instructor":
        raise HTTPException(
            status_code=403,
            detail="Denied access: only instructors",
        )
    target_course = db.query(Course).filter(Course.id == course_id).first()
    if not target_course:
        raise HTTPException(
            status_code=403,
            detail="Denied access: course not found",
        )
    if target_course.id_instructor != instructor_logged.id:
        raise HTTPException(
            status_code=403,
            detail="Denied access: You do not own this course.",
        )
    destin_path = UPLOADS_FOLDER / file.filename
    with destin_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_class = Lesson(
        classes_title=class_title,
        file_path_class=str(destin_path),
        course_id=target_course.id,
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return {"message": f"Class '{class_title}' added with sucess in this course!"}


def list_course_classes(db: Session, course_id: int):
    """
    Returns the list of lessons in JSON format linked to a specific course."""
    courses = db.query(Course).filter(Course.id == course_id).first()
    if not courses:
        raise HTTPException(
            status_code=403,
            detail="No one course found",
        )
    classes = db.query(Lesson).filter(Lesson.course_id == course_id).all()
    return classes


def download_file_of_class(db: Session, class_id: int):
    """Returns the file for viewing/downloading."""
    classroom = db.query(Lesson).filter(Lesson.id == class_id).first()
    if not classroom:
        raise HTTPException(
            status_code=403,
            detail="Class not found",
        )
    file_path = Path(classroom.file_path_class)
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="The physical file don't exists/It disappeared from the server.",
        )

    return FileResponse(
        path=file_path, filename=classroom.classes_title + file_path.suffix
    )
