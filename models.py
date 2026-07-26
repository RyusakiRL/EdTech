"""Moldes de criacao da tabela SQL"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Column

Base = declarative_base()


class Usuario(Base):
    """Molde de criacao de usuario"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name_user = Column(String, nullable=False, unique=True, index=True)
    password_user = Column(String, nullable=False)
    role_user = Column(String, nullable=False)

    created_courses_relationship = relationship("Curso", back_populates="instrutor")
    enrollments_relationship = relationship("Matricula", back_populates="aluno")


class Curso(Base):
    """Molde para criacao dos cursos"""

    __tablename__ = "cursos"
    id = Column(Integer, primary_key=True, index=True)
    course_title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    id_instrutor = Column(Integer, ForeignKey("users.id"), nullable=False)

    instructor_relationship = relationship("Usuario", back_populates="cursos_criados")
    enrollment_students_relationship = relationship("Matricula", back_populates="curso")
    classes_relationship = relationship("Aula", back_populates="curso")


class Aula(Base):
    """Tabela para a criacao do caminho dos arquivos"""

    __tablename__ = "aulas"
    id = Column(Integer, primary_key=True, index=True)
    classes_title = Column(String, nullable=False)
    file_path_class = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("cursos.id"))

    course_relationship = relationship("Curso", back_populates="aulas")


class Matricula(Base):
    """Tabela que cria os cursos que um usuario esta matriculado"""

    __tablename__ = "matriculas"
    id = Column(Integer, primary_key=True, index=True)
    progress = Column(Float, default=0.0)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("cursos.id"))

    student_relationship = relationship("Usuario", back_populates="matriculas")
    course_relationship = relationship("Curso", back_populates="alunos_matriculados")
