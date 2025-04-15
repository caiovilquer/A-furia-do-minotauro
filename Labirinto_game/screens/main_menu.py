import pygame
import sys
from constants import (BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TITULO, FONTE_BOTAO, COR_TITULO)
from utils.drawing import desenhar_texto, desenhar_botao, resize
from utils.colors import cor_com_escala_cinza

def tela_menu_principal(tela, usuario):
    """Tela do menu principal do jogo."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    import constants
    global ESCALA_CINZA, SOM_LIGADO
    ESCALA_CINZA = constants.ESCALA_CINZA
    SOM_LIGADO = constants.SOM_LIGADO

    titulo_x = LARGURA_TELA//2 - resize(350, eh_X=True)
    titulo_y = resize(100)

    while True:
        from utils.audio_manager import audio_manager
        audio_manager.set_bg_volume(0.05) 
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "VOLTAR"

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto(f"Bem-vindo, {usuario}!", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_inicial = resize(300)
        espacamento_botoes = resize(120)

        clicou_jogar, _ = desenhar_botao(
            texto="Iniciar Jogo",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(180, 100, 50),
            cor_hover=cor_com_escala_cinza(220, 150, 100),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_jogar:
            return "JOGAR"

        clicou_desempenho, _ = desenhar_botao(
            texto="Ver Desempenho",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(50, 50, 200),
            cor_hover=cor_com_escala_cinza(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_desempenho:
            return "DESEMPENHO"

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*2,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(0, 200, 0),
            cor_hover=cor_com_escala_cinza(0, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_rejogar:
            return "REJOGAR"

        clicou_escala, _ = desenhar_botao(
            texto="Desativar Escala de Cinza" if ESCALA_CINZA else "Ativar Escala de Cinza",
            x=LARGURA_TELA - resize(520, eh_X=True),
            y=ALTURA_TELA-resize(100),
            largura=resize(500, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(100, 100, 100),
            cor_hover=cor_com_escala_cinza(150, 150, 150),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_escala:
            constants.ESCALA_CINZA = not constants.ESCALA_CINZA
            ESCALA_CINZA = constants.ESCALA_CINZA
        
        clicou_som, _ = desenhar_botao(
            texto="Ativar Som" if not SOM_LIGADO else "Desativar Som",
            x=LARGURA_TELA - resize(520, eh_X=True),
            y=ALTURA_TELA-resize(200),
            largura=resize(500, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(100, 100, 100),
            cor_hover=cor_com_escala_cinza(150, 150, 150),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_som:
            from utils.audio_manager import audio_manager
            constants.SOM_LIGADO = not constants.SOM_LIGADO
            SOM_LIGADO = constants.SOM_LIGADO
            audio_manager.som_ligado = SOM_LIGADO
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*4,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_voltar:
            return "VOLTAR"
        
        clicou_conquistas, _ = desenhar_botao(
        texto="Conquistas",
        x=LARGURA_TELA//2 - resize(200, eh_X=True),
        y=y_inicial + espacamento_botoes*3,  # Ajuste este valor conforme necessário
        largura=resize(400, eh_X=True),
        altura=resize(80),
        cor_normal=cor_com_escala_cinza(200, 100, 200),
        cor_hover=cor_com_escala_cinza(255, 100, 255),
        fonte=fonte_botao,
        tela=tela,
        events=events,
        imagem_fundo=BUTTON_PATH,
        border_radius=resize(15)
    )
        if clicou_conquistas:
            return "CONQUISTAS"
        
        clicou_sair, _ = desenhar_botao(
            texto="Sair",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*5,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(200, 50, 50),
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

        pygame.display.update()