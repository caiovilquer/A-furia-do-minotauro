import pygame
import sys
from constants import (BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                      FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO)
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, TransitionEffect, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios

def tela_inicio_jogo(tela):
    """
    Exibe a tela inicial para escolher entre continuar jogo e novo jogo.
    
    Args:
        tela: Superfície do Pygame para renderização
        
    Returns:
        str: 'CONTINUAR' ou 'NOVO'
    """
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    
    usuarios = carregar_usuarios()
    tem_usuarios = len(usuarios) > 0
    
    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)
            
        desenhar_texto_sombra(
            "Escolha uma opção",
            fonte_titulo,
            COR_TITULO,
            tela,
            (LARGURA_TELA - fonte_titulo.size("Escolha uma opção")[0]) // 2,
            resize(100)
        )
        
        y_inicial = resize(300)
        espacamento_botoes = resize(120)
        
        if tem_usuarios:
            clicou_continuar, _ = desenhar_botao(
                texto="Continuar Jogo",
                x=LARGURA_TELA//2 - resize(200, eh_X=True),
                y=y_inicial,
                largura=resize(400, eh_X=True),
                altura=resize(80),
                cor_normal=cor_com_escala_cinza(0, 200, 100),
                cor_hover=cor_com_escala_cinza(0, 255, 100),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(15)
            )
            if clicou_continuar:
                return 'CONTINUAR'
            
            y_novo_jogo = y_inicial + espacamento_botoes
        else:
            y_novo_jogo = y_inicial
            
        clicou_novo, _ = desenhar_botao(
            texto="NOVO JOGO",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_novo_jogo,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(50, 50, 180),
            cor_hover=cor_com_escala_cinza(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_novo:
            return 'NOVO'
            
        clicou_sair, _ = desenhar_botao(
            texto="Sair",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_novo_jogo + espacamento_botoes,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(180, 50, 50),
            cor_hover=cor_com_escala_cinza(255, 50, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_sair:
            pygame.quit()
            sys.exit()
        
        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)
            
        pygame.display.update()
