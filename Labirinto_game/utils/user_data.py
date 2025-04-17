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

def marcar_dialogo_como_visto(usuario, nome_cena):
    """Marca um diálogo como já visto pelo usuário."""
    usuarios_data = carregar_usuarios()
    
    if usuario in usuarios_data:
        if 'dialogos_vistos' not in usuarios_data[usuario]:
            usuarios_data[usuario]['dialogos_vistos'] = []
        
        if nome_cena not in usuarios_data[usuario]['dialogos_vistos']:
            usuarios_data[usuario]['dialogos_vistos'].append(nome_cena)
            salvar_usuarios(usuarios_data)
            
def verificar_dialogo_visto(usuario, nome_cena):
    """Verifica se um diálogo já foi visto pelo usuário."""
    usuarios_data = carregar_usuarios()
    
    if usuario in usuarios_data:
        dialogos_vistos = usuarios_data[usuario].get('dialogos_vistos', [])
        return nome_cena in dialogos_vistos
    
    return False