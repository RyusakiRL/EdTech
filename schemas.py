"""Valida os dados que serao entregues"""

from pydantic import BaseModel


class Usuario(BaseModel):
    """Validacao de dados para criacao de usuario no SQL"""

    nome_user = str
    senha = str


class Cursos(BaseModel):
    """Validacao de dados para criacao de cursos no SQL"""

    titulo = str
    descricao = str
