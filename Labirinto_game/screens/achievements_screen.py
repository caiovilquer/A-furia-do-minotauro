import pygame
import sys
import os
from constants import LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO
from utils.drawing import desenhar_texto, desenhar_botao, resize
from utils.colors import cor_com_escala_cinza
from utils.achievements import SistemaConquistas

def carregar_e_redimensionar_icone(caminho, tamanho=(resize(80, eh_X=True), resize(80))):
    """Carrega uma imagem de ícone e redimensiona para o tamanho especificado."""
    try:
        if os.path.exists(caminho):
            icone = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(icone, tamanho)
        else:
            print(f"Caminho do ícone não encontrado: {caminho}")
            return None
    except Exception as e:
        print(f"Erro ao carregar ícone {caminho}: {e}")
        return None

def tela_conquistas(tela, usuario):
    """Tela para visualizar conquistas desbloqueadas."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_texto = FONTE_TEXTO
    fonte_botao = FONTE_BOTAO
    
    # Inicializa o sistema de conquistas
    sistema_conquistas = SistemaConquistas()
    conquistas = sistema_conquistas.carregar_conquistas_usuario(usuario)
    
    # Pré-carrega os ícones
    icones = {}
    for chave, conquista in conquistas.items():
        icone_path = conquista.get('icone', None)
        if icone_path:
            icones[chave] = carregar_e_redimensionar_icone(icone_path)
    
    titulo_x = resize(100, eh_X=True)
    titulo_y = resize(50)
    
    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        
        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)
        
        # Título da tela
        desenhar_texto(f"Conquistas de {usuario}", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        
        # Lista de conquistas
        y_offset = resize(180)
        espacamento = resize(100)
        
        for chave, conquista in conquistas.items():
            # Status da conquista
            status = "Desbloqueada" if conquista['desbloqueada'] else "Bloqueada"
            cor_status = cor_com_escala_cinza(0, 200, 0) if conquista['desbloqueada'] else cor_com_escala_cinza(200, 0, 0)
            
            # Prepara o retângulo para o ícone
            icone_rect = pygame.Rect(titulo_x, y_offset, resize(80, eh_X=True), resize(80))
            
            # Tenta desenhar o ícone
            if chave in icones and icones[chave]:
                # Ajuste o ícone para aparecer cinza se estiver bloqueado
                if not conquista['desbloqueada']:
                    # Cria uma cópia em escala de cinza do ícone
                    icone_cinza = icones[chave].copy()
                    # Cria uma superfície para aplicar o efeito de escala de cinza
                    cinza_surface = pygame.Surface((resize(80, eh_X=True), resize(80)), pygame.SRCALPHA)
                    cinza_surface.fill((100, 100, 100, 150))
                    # Aplica o efeito
                    icone_cinza.blit(cinza_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    tela.blit(icone_cinza, icone_rect)
                else:
                    # Ícone normal para conquistas desbloqueadas
                    tela.blit(icones[chave], icone_rect)
                
                # Desenha uma borda ao redor do ícone
                pygame.draw.rect(tela, cor_com_escala_cinza(200, 200, 200), icone_rect, width=resize(2), border_radius=resize(10))
            else:
                # Fallback para o retângulo original caso o ícone não seja encontrado
                pygame.draw.rect(tela, cor_com_escala_cinza(150, 150, 150), icone_rect, border_radius=resize(10))
                pygame.draw.rect(tela, cor_com_escala_cinza(200, 200, 200), icone_rect, width=resize(2), border_radius=resize(10))
            
            # Desenha informações da conquista
            desenhar_texto(conquista['nome'], fonte_texto, COR_TEXTO, tela, titulo_x + resize(100, eh_X=True), y_offset)
            desenhar_texto(conquista['descricao'], pygame.font.SysFont("comicsansms", resize(30)), 
                          cor_com_escala_cinza(200, 200, 200), tela, titulo_x + resize(100, eh_X=True), y_offset + resize(40))
            desenhar_texto(status, pygame.font.SysFont("comicsansms", resize(25)), 
                          cor_status, tela, LARGURA_TELA - resize(300, eh_X=True), y_offset + resize(20))
            
            y_offset += espacamento
                
        # Botão Voltar
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=resize(100, eh_X=True),
            y=ALTURA_TELA - resize(150),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=resize(15)
        )
        if clicou_voltar:
            return
        
        pygame.display.update()