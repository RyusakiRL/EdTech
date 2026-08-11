"""Table creation templates in SQL"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Column

Base = declarative_base()


class User(Base):
    """Template for user creation"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name_user = Column(String, nullable=False, unique=True, index=True)
    password_user = Column(String, nullable=False)
    role_user = Column(String, nullable=False)
    my_number = Column(Integer, nullable=False)
    created_courses_relationship = relationship(
        "Course", back_populates="instructor_relationship"
    )
    enrollments_relationship = relationship(
        "Registration", back_populates="student_relationship"
    )


class Course(Base):
    """Template for courses creation"""

    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    course_title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    id_instructor = Column(Integer, ForeignKey("users.id"), nullable=False)

    instructor_relationship = relationship(
        "User", back_populates="created_courses_relationship"
    )
    enrollment_students_relationship = relationship(
        "Registration", back_populates="course_relationship"
    )
    classes_relationship = relationship(
        "Lesson", back_populates="course_class_relationship"
    )


class Lesson(Base):
    """Table template for file path creation"""

    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    classes_title = Column(String, nullable=False)
    file_path_class = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course_class_relationship = relationship(
        "Course", back_populates="classes_relationship"
    )


class Registration(Base):
    """Table template for enrollment creation"""

    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    progress = Column(Float, default=0.0)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    student_relationship = relationship(
        "User", back_populates="enrollments_relationship"
    )
    course_relationship = relationship(
        "Course", back_populates="enrollment_students_relationship"
    )
