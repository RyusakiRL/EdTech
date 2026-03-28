"""Moldes de criacao da tabela SQL"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Integer, String, ForeignKey, Float, Column

Base = declarative_base()


class Usuario(Base):
    """Molde de criacao de usuario"""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nome_adm = Column(String, nullable=False, unique=True, index=True)
    senha = Column(String, nullable=False)
    cargo = Column(String, nullable=False)

    cursos_criados = relationship("Curso", back_populates="instrutor")
    matriculas = relationship("Matricula", back_populates="aluno")


class Curso(Base):
    """Molde para criacao dos cursos"""

    __tablename__ = "cursos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    id_instrutor = Column(Integer, ForeignKey("users.id"), nullable=False)

    instrutor = relationship("Usuario", back_populates="cursos_criados")
    alunos_matriculados = relationship("Matricula", back_populates="matriculas")


class Matricula(Base):
    """Tabela que cria os cursos que um usuario esta matriculado"""

    __tablename__ = "matriculas"
    id = Column(Integer, primary_key=True, index=True)
    progresso = Column(Float, default=0.0)
    id_aluno = Column(Integer, ForeignKey("users.id"))
    id_curso = Column(Integer, ForeignKey("cursos.id"))

    aluno = relationship("Usuario", back_populates="matriculas")
    curso = relationship("Curso", back_populates="alunos_matriculados")
