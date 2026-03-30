"""Valida os dados que serao entregues"""

from pydantic import BaseModel


class UsuarioValidar(BaseModel):
    """Validacao de dados para criacao de usuario no SQL"""

    nome_user = str
    senha = str


class CursosValidar(BaseModel):
    """Validacao de dados para criacao de cursos no SQL"""

    titulo = str
    descricao = str
