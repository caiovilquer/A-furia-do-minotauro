import pygame
import sys
import math
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from utils.drawing import resize, desenhar_texto_textura, centralizar_texto, aplicar_filtro_cinza_superficie

def tela_inicial(tela):
    """Tela inicial do jogo com texto animado."""
    clock = pygame.time.Clock()
    rodando = True

    # Texto e fonte
    mensagem = "A FÚRIA DO MINOTAURO"
    mensagem2 = "Aperte qualquer tecla para continuar"
    fonte = pygame.font.Font("Labirinto_game/assets/fonts/Odyssey2.otf", resize(140, eh_X=True))
    fonte2 = pygame.font.Font("Labirinto_game/assets/fonts/Odyssey.otf", resize(50, eh_X=True))

    # Configuração de animação
    base_x = LARGURA_TELA // 2
    base_y = ALTURA_TELA // 2 - resize(20)
    amplitude = resize(20)
    frequencia = 0.4

    tempo_acumulado = 0.0
    texture_image = pygame.image.load("Labirinto_game/assets/images/marmore2.jpg").convert_alpha()
    
    while rodando:
        dt = clock.tick(FPS)
        tempo_acumulado += dt / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    rodando = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                rodando = False

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        # Animação de movimento vertical
        offset_y = amplitude * math.sin(2 * math.pi * frequencia * tempo_acumulado)
        pos_y = base_y + offset_y

        # Renderizar textos
        text_surface = desenhar_texto_textura(mensagem, fonte, texture_image)
        text_surface2 = desenhar_texto_textura(mensagem2, fonte2, texture_image)
        
        text_rect = text_surface.get_rect(center=(LARGURA_TELA // 2, pos_y))
        text_rect2 = text_surface2.get_rect(center=(LARGURA_TELA // 2, pos_y + resize(100)))
        
        tela.blit(text_surface, text_rect)
        tela.blit(text_surface2, text_rect2)

        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)
            
        pygame.display.update()