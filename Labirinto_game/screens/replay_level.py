import pygame
import sys
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO
from utils.drawing import desenhar_texto, desenhar_botao, resize
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios

def tela_rejogar(tela, usuario):
    """Tela para escolher qual nível rejogar."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    usuarios_data = carregar_usuarios()
    nivel_atual = usuarios_data[usuario]["nivel"]
    niveis_disponiveis = list(range(1, nivel_atual + 1))

    titulo_x = LARGURA_TELA//2 - resize(300, eh_X=True)
    titulo_y = resize(100)
    y_inicial_botoes = resize(250)
    espacamento = resize(90)

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Rejogar Níveis", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_offset = y_inicial_botoes
        for lvl in niveis_disponiveis:
            txt_btn = f"Nível {lvl}"
            clicou, _ = desenhar_botao(
                texto=txt_btn,
                x=LARGURA_TELA//2-resize(130, eh_X=True),
                y=y_offset,
                largura=resize(200, eh_X=True),
                altura=resize(70),
                cor_normal=cor_com_escala_cinza(50, 50, 200),
                cor_hover=cor_com_escala_cinza(80, 80, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(15)
            )
            if clicou:
                return lvl
            y_offset += espacamento

        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - resize(241, eh_X=True),
            y=y_offset,
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=resize(15)
        )
        if clicou_voltar:
            return None

        pygame.display.update()