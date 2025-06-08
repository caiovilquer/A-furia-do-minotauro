import pygame
import os
import math



def centralizar_texto(fonte, texto, superficie, y, largura=None, x0=0):
    """
    Retorna a posição X para centralizar o texto na superfície.
    - fonte: pygame.font.Font
    - texto: str
    - superficie: pygame.Surface
    - y: posição Y desejada
    - largura: largura do retângulo de centralização (opcional, padrão: largura da superfície)
    - x0: início do retângulo (opcional)
    """
    text_obj = fonte.render(texto, True, (0,0,0))
    rect = text_obj.get_rect()
    if largura is None:
        largura = superficie.get_width()
    x = x0 + (largura - rect.width) // 2
    return x, y

def desenhar_texto(texto, fonte, cor, superficie, x, y, centralizado=False, largura=None):
    """Desenha texto na superfície especificada. Se centralizado=True, centraliza horizontalmente."""
    from utils.colors import cor_com_escala_cinza
    text_obj = fonte.render(texto, True, cor_com_escala_cinza(cor[0], cor[1], cor[2]))
    if centralizado:
        if largura is None:
            largura = superficie.get_width()
        x = (largura - text_obj.get_width()) // 2
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
    from utils.audio_manager import audio_manager
    
    if events is None:
        events = []
    
    pos_mouse = pygame.mouse.get_pos()
    botao_rect = pygame.Rect(x, y, largura, altura)
    mouse_sobre = botao_rect.collidepoint(pos_mouse)
    
    # Verifica se o mouse acabou de entrar no botão para tocar o som de hover
    mouse_estava_sobre = getattr(desenhar_botao, f'mouse_sobre_{x}_{y}', False)
    if mouse_sobre and not mouse_estava_sobre:
        audio_manager.play_sound("hover")
    setattr(desenhar_botao, f'mouse_sobre_{x}_{y}', mouse_sobre)

    # Efeito de elevação ao passar o mouse por cima
    hover_offset = resize(6) if mouse_sobre else 0
    
    # Prepara superfícies para o botão e sua sombra
    botao_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    botao_surf = botao_surf.convert_alpha()
    
    # Dimensões da sombra (ligeiramente maior que o botão)
    shadow_expand = resize(5)  # Quanto a sombra se expande além do botão
    shadow_width = largura + shadow_expand * 2
    shadow_height = altura + shadow_expand  # Maior na parte inferior
    
    # Cria uma superfície para a sombra (maior que o botão)
    shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
    
    # Cor do botão (agora usamos uma cor ligeiramente diferente ao passar o mouse)
    if mouse_sobre:
        # Botão um pouco mais claro quando hover
        cor_fundo = tuple(min(c + 30, 255) for c in cor_normal)
    else:
        cor_fundo = cor_normal

    # Desenha o botão normalmente
    if imagem_fundo and os.path.exists(imagem_fundo):
        img = pygame.image.load(imagem_fundo).convert_alpha()
        img = pygame.transform.scale(img, (largura, altura))
        botao_surf.blit(img, (0, 0))
        
        # Para imagens,um leve brilho ao passar o mouse
    #     if mouse_sobre:
    #         glow = pygame.Surface((largura, altura), pygame.SRCALPHA)
    #         glow.fill((255, 255, 255, 30))  # Brilho sutil
    #         botao_surf.blit(glow, (0, 0))
    # else:
    #     pygame.draw.rect(botao_surf, cor_fundo, (0, 0, largura, altura), border_radius=border_radius)
    
    # Adiciona o texto ao botão com estilo mitológico
    from constants import COR_BOTAO_TEXTO
    import math, time
    
    # Função para renderizar texto com estilo inspirado em entalhes gregos antigos
    def renderizar_texto_mitologico(superficie, texto, fonte, posicao_central):
        # Cores para o efeito de entalhe em pedra antiga
        cor_texto = COR_BOTAO_TEXTO  # Cor principal (branco)
        cor_sombra_escura = (10, 5, 0, 120)  # Sombra profunda quase preta
        cor_sombra_media = (30, 15, 0, 80)  # Sombra marrom média
        cor_borda = (180, 140, 60, 255)  # Dourado antigo
        
        cx, cy = posicao_central
        
        # Profundidade maior quando hover para efeito de "elevação" do texto
        profundidade = 6 if mouse_sobre else 4
        
        # Camada de sombra profunda
        for i in range(profundidade, 0, -1):
            # Sombra gradualmente mais opaca conforme se aproxima do texto
            opacidade = min(255, 120 + (profundidade - i) * 40)
            sombra = fonte.render(texto, True, (cor_sombra_escura[0], cor_sombra_escura[1], 
                                             cor_sombra_escura[2], opacidade))
            rect = sombra.get_rect(center=(cx + i*0.8, cy + i*1.2))
            superficie.blit(sombra, rect)
        
        # Sombra média para transição mais suave
        sombra_media = fonte.render(texto, True, cor_sombra_media)
        rect = sombra_media.get_rect(center=(cx + 1, cy + 1))
        superficie.blit(sombra_media, rect) 
        
        # Borda dourada (aspecto de entalhe em ouro)
        if mouse_sobre:
            # Contorno dourado completo quando hover
            for offset in [(0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1)]:
                borda = fonte.render(texto, True, cor_borda)
                rect = borda.get_rect(center=(cx + offset[0], cy + offset[1]))
                superficie.blit(borda, rect)
        else:
            # Contorno parcial quando não hover (só embaixo e à direita)
            for offset in [(1,0), (1,1), (0,1)]:
                borda = fonte.render(texto, True, cor_borda)
                rect = borda.get_rect(center=(cx + offset[0], cy + offset[1]))
                superficie.blit(borda, rect)
        
        # Texto principal com cor base
        texto_principal = fonte.render(texto, True, cor_texto)
        rect_principal = texto_principal.get_rect(center=(cx, cy))
        superficie.blit(texto_principal, rect_principal)
        
    
    # Renderiza o texto com o estilo personalizado
    renderizar_texto_mitologico(botao_surf, texto, fonte, (largura//2, altura//2+resize(5)))
    
    # Desenha uma sombra 
    if not (imagem_fundo and os.path.exists(imagem_fundo)):
        # Desenha sombra principal (um retângulo com cantos arredondados)
        shadow_alpha = 60 if mouse_sobre else 40  # Sombra mais escura ao passar o mouse
        shadow_color = (0, 0, 0, shadow_alpha)
        
        # Desenha a forma principal da sombra com cantos arredondados
        shadow_rect = pygame.Rect(
            shadow_expand, 
            shadow_expand, 
            largura, 
            altura
        )
        pygame.draw.rect(shadow_surf, shadow_color, shadow_rect, border_radius=border_radius)
        
        # Aplica um efeito de desfoque simples 
        blur_iterations = 3
        for i in range(blur_iterations):
            # Cada iteração dilata ligeiramente a sombra e reduz a opacidade
            blur_alpha = shadow_alpha * (blur_iterations - i) // (blur_iterations * 2)
            blur_color = (0, 0, 0, blur_alpha)
            
            blur_rect = pygame.Rect(
                shadow_expand - i, 
                shadow_expand - i, 
                largura + i * 2, 
                altura + i * 2
            )
            pygame.draw.rect(shadow_surf, blur_color, blur_rect, border_radius=border_radius + i)
        
        # Aplica a sombra na posição ligeiramente deslocada
        shadow_x = x - shadow_expand
        shadow_y = y + hover_offset  # A sombra não se move para cima quando hover
        tela.blit(shadow_surf, (shadow_x, shadow_y))
    
    # Aplica o botão com o efeito de elevação
    tela.blit(botao_surf, (x, y - hover_offset))

    # A área de clique permanece na posição original
    clicou = False
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if botao_rect.collidepoint(e.pos):
                audio_manager.play_sound("click")
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
    text_rect = text_render.get_rect(center=(x + largura//2, y + altura//2 + resize(2)))

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
        
        tela_atual = tela.copy()
        
        for alpha in range(0, 256, velocidade):
            overlay.set_alpha(alpha)
            tela.blit(tela_atual, (0, 0))
            tela.blit(overlay, (0, 0))
            pygame.display.update()
            pygame.time.delay(10)
            
    @staticmethod
    def fade_in(tela, velocidade=5):
        """Transição de fade in (tela aparecendo gradualmente)"""
        largura, altura = tela.get_size()
        overlay = pygame.Surface((largura, altura))
        overlay.fill((0, 0, 0))
        
        tela_base = tela.copy()
        
        for alpha in range(255, -1, -velocidade):
            overlay.set_alpha(alpha)
            tela.blit(tela_base, (0, 0))
            tela.blit(overlay, (0, 0))
            pygame.display.update()
            pygame.time.delay(10)
    
    @staticmethod
    def slide_left(tela, nova_tela, velocidade=20):
        """Transição deslizando para a esquerda"""
        largura, altura = tela.get_size()
        tela_atual = tela.copy()
        
        aceleracao = 1.0
        posicao = 0
        
        while posicao < largura:
            velocidade_atual = velocidade * aceleracao
            posicao += velocidade_atual
            aceleracao += 0.05
            
            posicao = min(posicao, largura)
            
            tela.blit(tela_atual, (-posicao, 0))
            tela.blit(nova_tela, (largura-posicao, 0))
            pygame.display.update()
            pygame.time.delay(5)
    
    @staticmethod
    def slide_right(tela, nova_tela, velocidade=20):
        """Transição deslizando para a direita"""
        largura, altura = tela.get_size()
        tela_atual = tela.copy()
        
        aceleracao = 1.0
        posicao = 0
        
        while posicao < largura:
            velocidade_atual = velocidade * aceleracao
            posicao += velocidade_atual
            aceleracao += 0.05
            
            posicao = min(posicao, largura)
            
            tela.blit(tela_atual, (posicao, 0))
            tela.blit(nova_tela, (-largura+posicao, 0))
            pygame.display.update()
            pygame.time.delay(5)
    
    @staticmethod
    def circle_close(tela, velocidade=10):
        """Transição com círculo se fechando"""
        largura, altura = tela.get_size()
        centro = (largura // 2, altura // 2)
        raio_max = int(math.sqrt(largura**2 + altura**2) / 2)
        
        tela_original = tela.copy()
        
        for raio in range(raio_max, 0, -velocidade):
            mascara = pygame.Surface((largura, altura), pygame.SRCALPHA)
            mascara.fill((0, 0, 0))
            
            pygame.draw.circle(mascara, (0, 0, 0, 0), centro, raio)
            
            tela.blit(tela_original, (0, 0))
            tela.blit(mascara, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)
            
        tela.fill((0, 0, 0))
        pygame.display.update()
        
    @staticmethod
    def circle_open(tela, velocidade=10):
        """Transição com círculo se abrindo"""
        largura, altura = tela.get_size()
        centro = (largura // 2, altura // 2)
        raio_max = int(math.sqrt(largura**2 + altura**2) / 2)
        
        tela_final = tela.copy()
        
        tela.fill((0, 0, 0))
        pygame.display.update()
        
        for raio in range(0, raio_max + velocidade, velocidade):
            mascara = pygame.Surface((largura, altura), pygame.SRCALPHA)
            mascara.fill((0, 0, 0))
            
            pygame.draw.circle(mascara, (0, 0, 0, 0), centro, raio)
            
            tela.fill((0, 0, 0))
            tela.blit(tela_final, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            tela.blit(mascara, (0, 0))
            pygame.display.update()
            pygame.time.delay(5)
            
        tela.blit(tela_final, (0, 0))
        pygame.display.update()
def resize(valor, eh_X=False, largura_tela=None, altura_tela=None, ui_escala=None):
    """
    Redimensiona o valor baseado na proporção da tela.
    (Escala de interface removida)
    """

    if largura_tela is None or altura_tela is None:
        try:
            from constants import LARGURA_TELA, ALTURA_TELA
            if largura_tela is None:
                largura_tela = LARGURA_TELA
            if altura_tela is None:
                altura_tela = ALTURA_TELA
        except Exception:
            largura_tela = largura_tela or 1920
            altura_tela = altura_tela or 1080
    if eh_X:
        return min(int(valor * largura_tela / 1920), int(1.1*valor))
    else:
        return min(int(valor * altura_tela / 1080), int(1.1*valor))



def aplicar_filtro_cinza_superficie(surface, alpha=180):
    """
    Aplica um filtro de escala de cinza sobre a superfície fornecida.
    alpha: transparência do filtro (0-255). Use 255 para filtro total.
    """
    # Cria uma superfície temporária do mesmo tamanho
    gray_surface = pygame.Surface(surface.get_size())
    
    # Copia o conteúdo da superfície original
    gray_surface.blit(surface, (0, 0))
    
    # Usa array3d para obter um array NumPy da superfície
    arr = pygame.surfarray.array3d(gray_surface)
    
    # Calcula a média ponderada para escala de cinza
    gray = 0.299 * arr[:,:,0] + 0.587 * arr[:,:,1] + 0.114 * arr[:,:,2]
    
    # Aplica o valor de cinza a todos os canais
    arr[:,:,0] = gray
    arr[:,:,1] = gray
    arr[:,:,2] = gray
    
    # Atualiza a superfície com o array modificado
    pygame.surfarray.blit_array(gray_surface, arr)
    
    # Define a transparência
    gray_surface.set_alpha(alpha)
    
    # Aplica a superfície em escala de cinza sobre a original
    surface.blit(gray_surface, (0, 0))
