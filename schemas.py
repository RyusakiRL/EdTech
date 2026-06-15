"""Valida os dados que serao entregues"""

from pydantic import BaseModel


class UsuarioValidar(BaseModel):
    """Validacao de dados para criacao de usuario no SQL"""

    nome_user: str
    senha: str


class CursosValidar(BaseModel):
    """Validacao de dados para criacao de cursos no SQL"""

    titulo: str
    descricao: str


class InstrutorResponse(BaseModel):
    nome_user: str


class ModelResponseCursos(BaseModel):
    """Modelo de resposta para a lista de dados dos cursos existentes"""

    titulo: str
    descricao: str
    instrutor: InstrutorResponse
