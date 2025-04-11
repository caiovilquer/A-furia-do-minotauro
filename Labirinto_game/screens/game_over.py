import pygame
import sys
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO
from utils.drawing import desenhar_texto, desenhar_botao
from utils.colors import cor_com_escala_cinza

def tela_falhou(tela, sistema_conquistas):
    """Tela quando o jogador perde todas as vidas."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    titulo_x = LARGURA_TELA//2 - 600
    titulo_y = 400

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Você perdeu todas as vidas!", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - 241,
            y=600,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(50, 200, 50),
            cor_hover=cor_com_escala_cinza(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return True
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - 241,
            y=700,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return False
        
        sistema_conquistas.desenhar_notificacao(tela)

        pygame.display.update()