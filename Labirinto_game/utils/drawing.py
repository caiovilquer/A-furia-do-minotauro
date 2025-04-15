import pygame
import os



def desenhar_texto(texto, fonte, cor, superficie, x, y):
    """Desenha texto na superfície especificada."""
    from utils.colors import cor_com_escala_cinza
    text_obj = fonte.render(texto, True, cor_com_escala_cinza(cor[0], cor[1], cor[2]))
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    superficie.blit(text_obj, text_rect)

def desenhar_texto_sombra(text, font, color, surf, x, y, shadow_color=(0,0,0), offset=2):
    # Renderiza o texto principal
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(topleft=(x, y))

    # Renderiza o texto para a sombra (deslocado)
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(topleft=(x + offset, y + offset))

    # Desenha a sombra primeiro, depois o texto “principal”
    surf.blit(shadow_surface, shadow_rect)
    surf.blit(text_surface, text_rect)

def desenhar_texto_textura(text, font, texture):
    """
    text: string
    font: fonte do pygame
    texture: pygame.Surface com a textura a ser usada

    Retorna um pygame.Surface onde as letras do texto foram
    preenchidas com a imagem 'texture'.
    """

    # Renderiza o texto em branco (para ficar fácil usar alpha)
    text_surface = font.render(text, True, (255,255,255))
    text_surface = text_surface.convert_alpha()

    # Criamos uma nova surface do mesmo tamanho do text_surface
    w, h = text_surface.get_size()
    final_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    final_surf = final_surf.convert_alpha()

    texture_scaled = pygame.transform.scale(texture, (w, h))

    final_surf.blit(texture_scaled, (0, 0))

    final_surf.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return final_surf

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
    from constants import COR_BOTAO_TEXTO
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
    

class TransitionEffect:
    """Classe para gerenciar transições entre telas"""
    
    @staticmethod
    def fade_out(tela, velocidade=5):
        """Transição de fade out (tela escurecendo gradualmente)"""
        largura, altura = tela.get_size()
        overlay = pygame.Surface((largura, altura))
        overlay.fill((0, 0, 0))
        
        for alpha in range(0, 255, velocidade):
            overlay.set_alpha(alpha)
            # Capturamos a tela atual
            tela_atual = tela.copy()
            # Aplicamos o overlay com transparência
            tela_atual.blit(overlay, (0, 0))
            # Atualizamos a tela
            tela.blit(tela_atual, (0, 0))
            pygame.display.update()
            pygame.time.delay(10)
            
    @staticmethod
    def fade_in(tela, velocidade=5):
        """Transição de fade in (tela aparecendo gradualmente)"""
        largura, altura = tela.get_size()
        overlay = pygame.Surface((largura, altura))
        overlay.fill((0, 0, 0))
        
        # Preparamos a tela base que aparecerá
        tela_base = tela.copy()
        
        for alpha in range(255, -1, -velocidade):
            overlay.set_alpha(alpha)
            # Começamos com a tela base
            tela.blit(tela_base, (0, 0))
            # Aplicamos o overlay com transparência decrescente
            tela.blit(overlay, (0, 0))
            pygame.display.update()
            pygame.time.delay(10)
    
    @staticmethod
    def slide_left(tela, nova_tela, velocidade=20):
        """Transição deslizando para a esquerda"""
        largura, altura = tela.get_size()
        tela_atual = tela.copy()
        
        for i in range(0, largura+1, velocidade):
            # Desenha a tela atual deslizando para a esquerda
            tela.blit(tela_atual, (-i, 0))
            # Desenha a nova tela chegando pela direita
            tela.blit(nova_tela, (largura-i, 0))
            pygame.display.update()
            pygame.time.delay(5)
    
    @staticmethod
    def slide_right(tela, nova_tela, velocidade=20):
        """Transição deslizando para a direita"""
        largura, altura = tela.get_size()
        tela_atual = tela.copy()
        
        for i in range(0, largura+1, velocidade):
            # Desenha a tela atual deslizando para a direita
            tela.blit(tela_atual, (i, 0))
            # Desenha a nova tela chegando pela esquerda
            tela.blit(nova_tela, (-largura+i, 0))
            pygame.display.update()
            pygame.time.delay(5)
            
def resize(valor, eh_X = False):
    """Redimensiona o valor baseado na proporção da tela."""
    from constants import LARGURA_TELA, ALTURA_TELA
    if eh_X:
        return int(valor * LARGURA_TELA / 1920)
    else:
        return int(valor * ALTURA_TELA / 1080)