"""Teste"""

import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Laboratório de Upload")

# Criamos uma referência para uma pasta chamada "uploads"
PASTA_UPLOADS = Path("uploads")

# Pedimos para o Python criar essa pasta se ela ainda não existir
PASTA_UPLOADS.mkdir(exist_ok=True)


@app.post("/enviar-arquivo")
def receber_arquivo(meu_arquivo: UploadFile = File(...)):
    """Teste para a API"""
    # 1. Montamos o caminho final: pasta "uploads" + o nome da sua imagem
    caminho_destino = PASTA_UPLOADS / meu_arquivo.filename

    # 2. Abrimos esse caminho em modo de escrita binária ("wb" = write binary)
    with caminho_destino.open("wb") as buffer:

        # 3. Despejamos os dados do UploadFile dentro desse arquivo novo
        shutil.copyfileobj(meu_arquivo.file, buffer)

    return {
        "mensagem": f"Sucesso! O arquivo {meu_arquivo.filename} foi salvo fisicamente no seu PC."
    }
