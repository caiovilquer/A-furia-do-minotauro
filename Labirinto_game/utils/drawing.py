import pygame
import os
from constants import COR_BOTAO_TEXTO
from utils.colors import cor_com_escala_cinza

def desenhar_texto(texto, fonte, cor, superficie, x, y):
    """Desenha texto na superfície especificada."""
    text_obj = fonte.render(texto, True, cor)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    superficie.blit(text_obj, text_rect)

def desenhar_botao(
    texto,
    x,
    y,
    largura,
    altura,
    cor_normal,
    cor_hover,
    fonte,
    tela,
    events=None,
    imagem_fundo=None,
    border_radius=0
):
    """Desenha um botão interativo e retorna se foi clicado."""
    if events is None:
        events = []
    
    pos_mouse = pygame.mouse.get_pos()
    botao_rect = pygame.Rect(x, y, largura, altura)
    mouse_sobre = botao_rect.collidepoint(pos_mouse)

    cor_fundo = cor_hover if mouse_sobre else cor_normal

    botao_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    botao_surf = botao_surf.convert_alpha()

    if imagem_fundo and os.path.exists(imagem_fundo):
        img = pygame.image.load(imagem_fundo).convert_alpha()
        img = pygame.transform.scale(img, (largura, altura))
        botao_surf.blit(img, (0, 0))
        if mouse_sobre:
            highlight_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
            highlight_surf.fill((255, 255, 255, 40))
            botao_surf.blit(highlight_surf, (0, 0))
    else:
        pygame.draw.rect(botao_surf, cor_fundo, (0, 0, largura, altura), border_radius=border_radius)

    texto_render = fonte.render(texto, True, COR_BOTAO_TEXTO)
    texto_rect = texto_render.get_rect(center=(largura//2, altura//2))
    botao_surf.blit(texto_render, texto_rect)
    tela.blit(botao_surf, (x, y))

    clicou = False
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if botao_rect.collidepoint(e.pos):
                clicou = True
                break

    return clicou, botao_rect

def desenhar_barra_progresso(
    tela,
    x,
    y,
    largura,
    altura,
    progresso,
    cor_fundo=(50, 50, 50),
    cor_barra=(0, 200, 0),
    cor_outline=(255, 255, 255),
    border_radius=15
):
    """Desenha uma barra de progresso com porcentagem."""
    if progresso < 0:
        progresso = 0
    elif progresso > 1:
        progresso = 1

    bar_surface = pygame.Surface((largura, altura), pygame.SRCALPHA)
    bar_surface = bar_surface.convert_alpha()

    fundo_rect = pygame.Rect(0, 0, largura, altura)
    pygame.draw.rect(bar_surface, cor_fundo, fundo_rect, border_radius=border_radius)

    fill_width = int(largura * progresso)
    if fill_width > 0:
        fill_rect = pygame.Rect(0, 0, fill_width, altura)
        pygame.draw.rect(bar_surface, cor_barra, fill_rect, border_radius=border_radius)

    pygame.draw.rect(bar_surface, cor_outline, fundo_rect, width=2, border_radius=border_radius)

    from constants import FONTE_BARRA
    percent_txt = f"Progresso: {int(progresso * 100)}%"
    text_render = FONTE_BARRA.render(percent_txt, True, (255,255,255))
    text_rect = text_render.get_rect(center=(x + largura//2, y + altura//2 - 3))

    tela.blit(bar_surface, (x, y))
    tela.blit(text_render, text_rect)