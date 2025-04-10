import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Importações após inicialização
from constants import LARGURA_TELA, ALTURA_TELA, TITULO_JOGO
from screens.initial_screen import tela_inicial
from screens.port_selection import tela_selecao_porta
from screens.user_selection import tela_escolha_usuario
from screens.main_menu import tela_menu_principal
from screens.performance import tela_desempenho
from screens.replay_level import tela_rejogar
from game.game import JogoLabirinto
from utils.drawing import TransitionEffect

def main():
    """Função principal que inicia o jogo."""
    # Configuração da tela
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    
    # Tela inicial
    TransitionEffect.fade_out(tela, velocidade=30)
    tela_inicial(tela)
    
    # Selecionar porta do Arduino
    TransitionEffect.fade_out(tela, velocidade=30)
    porta_escolhida = tela_selecao_porta(tela)
    
    print("PORTA ESCOLHIDA:", porta_escolhida)

    # Selecionar ou criar usuário
    TransitionEffect.fade_out(tela, velocidade=30)
    usuario_escolhido = tela_escolha_usuario(tela)

    # Loop principal do menu
    while True:
        TransitionEffect.fade_out(tela, velocidade=30)
        acao = tela_menu_principal(tela, usuario_escolhido)
        if acao == "JOGAR":
            TransitionEffect.fade_out(tela, velocidade=30)
            jogo = JogoLabirinto(tela, usuario_escolhido)
            jogo.loop_principal()
        elif acao == "DESEMPENHO":
            TransitionEffect.fade_out(tela, velocidade=30)
            tela_desempenho(tela, usuario_escolhido)
        elif acao == "REJOGAR":
            TransitionEffect.fade_out(tela, velocidade=30)
            nivel_escolhido = tela_rejogar(tela, usuario_escolhido)
            if nivel_escolhido is not None:
                TransitionEffect.fade_out(tela, velocidade=30)
                jogo = JogoLabirinto(tela, usuario_escolhido, nivel_inicial=nivel_escolhido)
                jogo.loop_principal()
        elif acao == "VOLTAR":
            TransitionEffect.fade_out(tela, velocidade=30)
            usuario_escolhido = tela_escolha_usuario(tela)
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()