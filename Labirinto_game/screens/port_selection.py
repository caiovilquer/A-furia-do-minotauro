import pygame
import sys
import serial.tools.list_ports
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza

def tela_selecao_porta(tela):
    """Tela para selecionar a porta do Arduino."""
    global PORTA_SELECIONADA
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    lista_portas = [p.device for p in serial.tools.list_ports.comports()]

    titulo_x = LARGURA_TELA//2 - resize(580, eh_X=True)
    titulo_y = resize(80)

    y_inicial_botoes = resize(250)
    espacamento_botoes = resize(90)

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from constants import PORTA_SELECIONADA
                    globals()['PORTA_SELECIONADA'] = None
                    return None

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto_sombra("Selecione a porta do Arduino", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_offset = y_inicial_botoes
        for port in lista_portas:
            clicou, _ = desenhar_botao(
                texto=port,
                x=LARGURA_TELA//2 - resize(160, eh_X=True),
                y=y_offset,
                largura=resize(300, eh_X=True),
                altura=resize(60),
                cor_normal=cor_com_escala_cinza(0, 150, 200),
                cor_hover=cor_com_escala_cinza(0, 200, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(10)
            )
            if clicou:
                from constants import PORTA_SELECIONADA
                globals()['PORTA_SELECIONADA'] = port
                return port
            y_offset += espacamento_botoes

        # Caso não tenha porta ou para simulação
        clicou_semport, _ = desenhar_botao(
            texto="Simulação",
            x=LARGURA_TELA//2 - resize(160, eh_X=True),
            y=y_offset + resize(100),
            largura=resize(300, eh_X=True),
            altura=resize(60),
            cor_normal=cor_com_escala_cinza(180, 100, 50),
            cor_hover=cor_com_escala_cinza(200, 120, 60),
            fonte=fonte_botao,
            tela=tela,
            imagem_fundo=BUTTON_PATH,
            events=events,
            border_radius=resize(10)
        )
        if clicou_semport:
            from constants import PORTA_SELECIONADA
            globals()['PORTA_SELECIONADA'] = None
            return None
            
        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)

        pygame.display.update()