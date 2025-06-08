import json
import os
from constants import USUARIOS_JSON

def carregar_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return {}
    with open(USUARIOS_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = {}
    return data

def salvar_usuarios(data):
    with open(USUARIOS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def verificar_dialogo_visto(usuario, nome_cena):
    usuarios_data = carregar_usuarios()
    
    if usuario in usuarios_data:
        dialogos_vistos = usuarios_data[usuario].get('dialogos_vistos', [])
        return nome_cena in dialogos_vistos
    
    return False

def marcar_dialogo_como_visto(usuario, nome_cena):
    usuarios_data = carregar_usuarios()
    
    if usuario in usuarios_data:
        if 'dialogos_vistos' not in usuarios_data[usuario]:
            usuarios_data[usuario]['dialogos_vistos'] = []
        
        if nome_cena not in usuarios_data[usuario]['dialogos_vistos']:
            usuarios_data[usuario]['dialogos_vistos'].append(nome_cena)
            salvar_usuarios(usuarios_data)
            return True
    
    return False

def get_acessibilidade(usuario, usuarios_data=None):
    if usuarios_data is None:
        usuarios_data = carregar_usuarios()
    
    # Garante valores padrão para ESCALA_CINZA e outras configurações
    acessibilidade = usuarios_data.get(usuario, {}).get("acessibilidade", {})
    
    # Atualiza as constantes globais com base nas preferências do usuário
    import constants
    if "ESCALA_CINZA" in acessibilidade:
        constants.ESCALA_CINZA = acessibilidade.get("ESCALA_CINZA", False)
    
    return acessibilidade

def set_acessibilidade(usuario, opcoes, usuarios_data=None):
    if usuarios_data is None:
        usuarios_data = carregar_usuarios()
    if usuario not in usuarios_data:
        usuarios_data[usuario] = {}
    
    # Atualiza as constantes globais para refletir as novas configurações
    import constants
    if "ESCALA_CINZA" in opcoes:
        constants.ESCALA_CINZA = opcoes["ESCALA_CINZA"]
    
    usuarios_data[usuario]["acessibilidade"] = opcoes
    salvar_usuarios(usuarios_data)