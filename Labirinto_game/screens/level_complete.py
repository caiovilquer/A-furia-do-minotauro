import pygame
import sys
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza

def tela_conclusao_nivel(tela, nivel, tempo, sistema_conquistas=None):
    """
    Tela quando o jogador conclui um nível.
    
    Returns:
        tuple: (continuar_jogando, repetir_nivel, pular_dialogo)
            continuar_jogando (bool): True se deve continuar jogando, False para sair
            repetir_nivel (bool): True para repetir o nível, False para avançar
            pular_dialogo (bool): True para pular diálogo ao repetir o nível
    """
    from utils.audio_manager import audio_manager
    
    # Reproduz um áudio dublado de vitória quando a tela é exibida
    audio_manager.play_voiced_dialogue("ganhou")
    
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    titulo_x = LARGURA_TELA//2 - resize(900, eh_X=True)
    titulo_y = resize(400)

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False, False, False  # Não continuar, não repetir, não pular diálogo

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto_sombra(f"Parabéns! Você concluiu o nível {nivel} em {tempo:.2f}s !", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2-resize(200, eh_X=True),
            y=resize(600),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(0, 200, 50),
            cor_hover=cor_com_escala_cinza(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_rejogar:
            audio_manager.stop_voiced_dialogue();
            return True, True, True  # Continuar jogando, repetir nível, pular diálogo

        clicou_avancar, _ = desenhar_botao(
            texto="Avançar Nível",
            x=LARGURA_TELA//2-resize(200, eh_X=True),
            y=resize(700),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(50, 50, 200),
            cor_hover=cor_com_escala_cinza(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_avancar:
            audio_manager.stop_voiced_dialogue();
            return True, False, False  # Continuar jogando, avançar para próximo nível, não pular diálogo
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2-resize(200, eh_X=True),
            y=resize(800),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_voltar:
            audio_manager.stop_voiced_dialogue();
            return False, False, False  # Não continuar, não repetir, não pular diálogo
        
        # Garantir que as notificações de conquistas sejam exibidas
        if sistema_conquistas and sistema_conquistas.notificacao_ativa:
            sistema_conquistas.desenhar_notificacao(tela)
            
        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)
            
        pygame.display.update()