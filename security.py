"""Módulo responsável pela segurança, criptografia e geração de tokens JWT."""

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

SECRET_KEY = (
    "uma_senha_completamente_aleatoria_ultra_mega_gigantenorme_asdjfeqwhfwbsfvbsvbsc"
)
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTOS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def gerar_hash_senha(senha: str) -> str:
    """
    Recebe a senha em texto puro (ex: '123456')
    e retorna o Hash ilegível para salvarmos no banco.
    """
    return pwd_context.hash(senha)


def verificar_senha(senha_texto_puro: str, senha_hasheada: str) -> bool:
    """
    Compara a senha que o usuário digitou no login com o Hash que está salvo no banco.
    Retorna True se a senha estiver correta, ou False se estiver errada.
    """
    return pwd_context.verify(senha_texto_puro, senha_hasheada)


def criar_token_jwt(dados: dict):
    """Gera o crachá digital (Token JWT) para o usuário."""
    dados_para_codificar = dados.copy()

    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=ACESS_TOKEN_EXPIRE_MINUTOS
    )
    dados_para_codificar.update({"exp": expiracao})

    token_codificado = jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)

    return token_codificado


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verificar_token(token: str = Depends(oauth2_scheme)):
    """Lê o crachá JWT e descobre quem é o dono."""

    excecao_nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Crachá inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        nome_user: str = payload.get("sub")

        if nome_user is None:
            raise excecao_nao_autorizado

        return nome_user

    except JWTError as erro_original:

        raise excecao_nao_autorizado from erro_original
