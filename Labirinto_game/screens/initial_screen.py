import pygame
import sys
import math
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img

def tela_inicial(tela):
    """Tela inicial do jogo com texto animado."""
    clock = pygame.time.Clock()
    rodando = True

    # Texto e fonte
    mensagem = "Pressione qualquer botão para iniciar!"
    fonte = pygame.font.SysFont("comicsansms", 80, bold=True)

    # Posição base (fixa) e parâmetros de movimento
    base_x = LARGURA_TELA // 2
    base_y = ALTURA_TELA // 2 - 80
    amplitude = 40.0   # até onde o texto "sobe e desce"
    frequencia = 0.5   # quantas "oscilações" por segundo

    tempo_acumulado = 0.0

    while rodando:
        dt = clock.tick(FPS)  # tempo em ms desde o último frame
        tempo_acumulado += dt / 1000.0  # converte para segundos

        # Trata eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # Ao apertar qualquer tecla ou clicar, sai desta tela
                rodando = False

        # Desenha fundo
        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        # Cálculo do offset em Y usando sin
        offset_y = amplitude * math.sin(2 * math.pi * frequencia * tempo_acumulado)
        # Posição final do texto
        pos_x = base_x
        pos_y = base_y + offset_y

        # Renderiza e desenha
        text_surface = fonte.render(mensagem, True, AZUL_CLARO)
        text_rect = text_surface.get_rect(center=(pos_x, pos_y))
        tela.blit(text_surface, text_rect)

        pygame.display.update()