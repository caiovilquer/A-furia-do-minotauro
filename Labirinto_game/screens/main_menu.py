import pygame
import sys
from constants import (BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TITULO, FONTE_BOTAO, COR_TITULO, FONTE_BOTAO_REDUZIDA)
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios

def tela_menu_principal(tela, usuario):
    """Tela do menu principal do jogo."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    import constants
    
    usuarios_data = carregar_usuarios()
    usuario_data = usuarios_data[usuario]

    titulo_x = LARGURA_TELA//2 - resize(350, eh_X=True)
    titulo_y = resize(100)

    while True:
        from utils.audio_manager import audio_manager
        from utils.user_data import get_acessibilidade
        try:
            opcoes = get_acessibilidade(usuario, usuarios_data)
            volume_musica = float(opcoes.get("VOLUME_MUSICA", 0.5))
        except Exception:
            volume_musica = 0.5
        audio_manager.set_bg_volume(volume_musica)
        
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

        # Centraliza o título
        desenhar_texto_sombra(
            f"Bem-vindo, {usuario}!",
            fonte_titulo,
            COR_TITULO,
            tela,
            (LARGURA_TELA - fonte_titulo.size(f"Bem-vindo, {usuario}!")[0]) // 2,
            titulo_y
        )

        y_inicial = resize(250)
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
        
        clicou_personagens, _ = desenhar_botao(
            texto="Personagens",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*4,
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(100, 180, 180),
            cor_hover=cor_com_escala_cinza(120, 220, 220),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_personagens:
            return "PERSONAGENS"
            
        clicou_acess, _ = desenhar_botao(
            texto="Acessibilidade",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*5,  # Ajustado para manter espaçamento
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(100, 100, 255),
            cor_hover=cor_com_escala_cinza(150, 150, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_acess:
            return "ACESSIBILIDADE"
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*6,  # Ajustado para manter espaçamento
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
        
        clicou_sair, _ = desenhar_botao(
            texto="Sair",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=y_inicial + espacamento_botoes*7,  # Ajustado para manter espaçamento
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
        
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)

        pygame.display.update()