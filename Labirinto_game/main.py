import pygame
import sys
import json
import time

# Inicialização do Pygame
pygame.init()

# Importações após inicialização
from screens.initial_dialogue_screen import TelaDialogoInicial
from constants import LARGURA_TELA, ALTURA_TELA, TITULO_JOGO
from screens.initial_screen import tela_inicial
from screens.port_selection import tela_selecao_porta
from screens.user_selection import tela_escolha_usuario
from screens.main_menu import tela_menu_principal
from screens.performance import tela_desempenho
from screens.replay_level import tela_rejogar
from game.game import JogoLabirinto
from utils.drawing import TransitionEffect
from screens.achievements_screen import tela_conquistas
from utils.user_data import carregar_usuarios, salvar_usuarios
from screens.game_start_screen import tela_inicio_jogo
from utils.audio_manager import audio_manager
from screens.characters_screen import tela_personagens

def main():
    """Função principal do jogo."""
    pygame.init()
    
    # Configura a tela
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    
    # Carrega o audio manager
    audio_manager.load_sounds()
    audio_manager.play_background()
    
    # Mostrar tela inicial
    tela_inicial(tela)
    
    # Selecionar porta do Arduino
    TransitionEffect.fade_out(tela, velocidade=30)
    conexao_serial = tela_selecao_porta(tela)
    
    print("CONEXÃO SERIAL:", "Simulação" if conexao_serial is None else "Estabelecida")
    
    # Nova tela para escolher entre continuar ou novo jogo
    TransitionEffect.fade_out(tela, velocidade=30)
    
    # Loop para permitir voltar à tela inicial se necessário
    while True:
        escolha = tela_inicio_jogo(tela)
        
        # Se o usuário escolher continuar, mostrar tela de seleção de usuário
        usuario_escolhido = None
        if escolha == 'CONTINUAR':
            TransitionEffect.fade_out(tela, velocidade=30)
            usuario_escolhido = tela_escolha_usuario(tela)
            
            # Se o usuário clicar em "Voltar", retorna à tela de início de jogo
            if usuario_escolhido is None:
                TransitionEffect.fade_out(tela, velocidade=30)
                continue
        
        # Iniciar diálogo e capturar o nome do usuário (apenas para novo jogo)
        if escolha == 'NOVO' or not usuario_escolhido:
            TransitionEffect.fade_out(tela, velocidade=30)
            dialogos = TelaDialogoInicial(tela)
            usuario_escolhido = dialogos.executar()
        
        # Se temos um usuário válido, podemos prosseguir com o jogo
        if usuario_escolhido:
            # Armazena o usuário atual em constantes para uso global
            import constants
            constants.USUARIO_ATUAL = usuario_escolhido
            from utils.user_data import get_acessibilidade, carregar_usuarios
            usuarios_data = carregar_usuarios()
            opcoes = get_acessibilidade(usuario_escolhido, usuarios_data)
            break
        
    # Verificar se o usuário já existe ou criar novo
    usuarios_data = carregar_usuarios()
    if usuario_escolhido and usuario_escolhido not in usuarios_data:
        usuarios_data[usuario_escolhido] = {
            "nivel": 1,
            "tentativas": [],
        }
        salvar_usuarios(usuarios_data)

    from utils.achievements import SistemaConquistas
    sistema_conquistas = SistemaConquistas()
    # Loop principal do menu
    while True:
        TransitionEffect.fade_out(tela, velocidade=30)
        acao = tela_menu_principal(tela, usuario_escolhido)
        if acao == "JOGAR":
            from utils.user_data import carregar_usuarios, get_acessibilidade
            usuarios_data = carregar_usuarios()
            opcoes = get_acessibilidade(usuario_escolhido, usuarios_data)
            volume_musica = float(opcoes.get("VOLUME_MUSICA", 0.5))
            audio_manager.set_bg_volume(0.1 * volume_musica)
            TransitionEffect.slide_left(tela, tela.copy(), 30)
            jogo = JogoLabirinto(tela, usuario_escolhido, sistema_conquistas=sistema_conquistas, conexao_serial=conexao_serial)
            jogo.loop_principal(pular_dialogo=False)
            TransitionEffect.slide_right(tela, tela.copy(), 30)
        elif acao == "DESEMPENHO":
            TransitionEffect.fade_out(tela, velocidade=30)
            tela_desempenho(tela, usuario_escolhido)
        elif acao == "REJOGAR":
            from utils.user_data import carregar_usuarios, get_acessibilidade
            usuarios_data = carregar_usuarios()
            opcoes = get_acessibilidade(usuario_escolhido, usuarios_data)
            volume_musica = float(opcoes.get("VOLUME_MUSICA", 0.5))
            audio_manager.set_bg_volume(0.1 * volume_musica)
            TransitionEffect.fade_out(tela, velocidade=30)
            nivel_escolhido = tela_rejogar(tela, usuario_escolhido)
            if nivel_escolhido is not None:
                TransitionEffect.fade_out(tela, velocidade=30)
                jogo = JogoLabirinto(tela, usuario_escolhido, nivel_inicial=nivel_escolhido, 
                                     sistema_conquistas=sistema_conquistas, conexao_serial=conexao_serial)
                jogo.loop_principal(pular_dialogo=False)
                TransitionEffect.slide_right(tela, tela.copy(), 30)
        elif acao == "VOLTAR":
            print("Voltando para a tela inicial...")
            constants.ESCALA_CINZA = False  # Reseta a escala de cinza
            return main()
        elif acao == "ACESSIBILIDADE":
            TransitionEffect.fade_out(tela, velocidade=30)
            from screens.options_accessibility import tela_opcoes_acessibilidade
            tela_opcoes_acessibilidade(tela, usuario_escolhido)

        elif acao == "CONQUISTAS":
            TransitionEffect.fade_out(tela, velocidade=30)
            tela_conquistas(tela, usuario_escolhido)
        elif acao == "PERSONAGENS":
            TransitionEffect.fade_out(tela, velocidade=30)
            tela_personagens(tela)
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()