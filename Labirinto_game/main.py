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

def main():
    """Função principal que inicia o jogo."""
    # Configuração da tela
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    
    # Tela inicial
    tela_inicial(tela)
    
    # Selecionar porta do Arduino
    porta_escolhida = tela_selecao_porta(tela)
    print("PORTA ESCOLHIDA:", porta_escolhida)

    # Selecionar ou criar usuário
    usuario_escolhido = tela_escolha_usuario(tela)

    # Loop principal do menu
    while True:
        acao = tela_menu_principal(tela, usuario_escolhido)
        if acao == "JOGAR":
            jogo = JogoLabirinto(tela, usuario_escolhido)
            jogo.loop_principal()
        elif acao == "DESEMPENHO":
            tela_desempenho(tela, usuario_escolhido)
        elif acao == "REJOGAR":
            nivel_escolhido = tela_rejogar(tela, usuario_escolhido)
            if nivel_escolhido is not None:
                jogo = JogoLabirinto(tela, usuario_escolhido, nivel_inicial=nivel_escolhido)
                jogo.loop_principal()
        elif acao == "VOLTAR":
            usuario_escolhido = tela_escolha_usuario(tela)
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()