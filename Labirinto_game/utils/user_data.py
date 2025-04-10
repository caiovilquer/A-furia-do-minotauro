import json
import os
from constants import USUARIOS_JSON

def carregar_usuarios():
    """Carrega dados dos usuários do arquivo JSON."""
    if not os.path.exists(USUARIOS_JSON):
        return {}
    with open(USUARIOS_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = {}
    return data

def salvar_usuarios(data):
    """Salva dados dos usuários no arquivo JSON."""
    with open(USUARIOS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)