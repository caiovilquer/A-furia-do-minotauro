import pygame
import sys
import serial.tools.list_ports
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO
from utils.drawing import desenhar_texto, desenhar_botao
from utils.colors import cor_com_escala_cinza

def tela_selecao_porta(tela):
    """Tela para selecionar a porta do Arduino."""
    global PORTA_SELECIONADA
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    lista_portas = [p.device for p in serial.tools.list_ports.comports()]

    titulo_x = LARGURA_TELA//2 - 580
    titulo_y = 80

    y_inicial_botoes = 250
    espacamento_botoes = 90

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

        desenhar_texto("Selecione a porta do Arduino", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_offset = y_inicial_botoes
        for port in lista_portas:
            clicou, _ = desenhar_botao(
                texto=port,
                x=LARGURA_TELA//2 - 160,
                y=y_offset,
                largura=300,
                altura=60,
                cor_normal=cor_com_escala_cinza(0, 150, 200),
                cor_hover=cor_com_escala_cinza(0, 200, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                border_radius=10
            )
            if clicou:
                from constants import PORTA_SELECIONADA
                globals()['PORTA_SELECIONADA'] = port
                return port
            y_offset += espacamento_botoes

        # Caso não tenha porta ou para simulação
        clicou_semport, _ = desenhar_botao(
            texto="Simulação",
            x=LARGURA_TELA//2 - 160,
            y=y_offset + 100,
            largura=300,
            altura=60,
            cor_normal=cor_com_escala_cinza(180, 100, 50),
            cor_hover=cor_com_escala_cinza(200, 120, 60),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            border_radius=10
        )
        if clicou_semport:
            from constants import PORTA_SELECIONADA
            globals()['PORTA_SELECIONADA'] = None
            return None

        pygame.display.update()