import pygame
import sys
from constants import (BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                      FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO)
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, TransitionEffect
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios

def tela_inicio_jogo(tela):
    """
    Exibe a tela inicial para escolher entre continuar jogo e novo jogo.
    
    Args:
        tela: Superfície do Pygame para renderização
        
    Returns:
        tuple: ('CONTINUAR', None) ou ('NOVO', dark_mode)
    """
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    
    # Carregar usuários para verificar se existem jogos salvos
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

        # Desenhar fundo
        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)
            
        # Desenhar título
        desenhar_texto_sombra("Escolha uma opção", fonte_titulo, COR_TITULO, tela, LARGURA_TELA // 2 - resize(350, eh_X=True), resize(100))
        
        # Botões
        y_inicial = resize(300)
        espacamento_botoes = resize(120)
        
        # Botão Continuar (apenas se houver usuários)
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
                return ('CONTINUAR', None)
            
            # Ajusta posição do botão Novo Jogo se houver o botão Continuar
            y_novo_jogo = y_inicial + espacamento_botoes
        else:
            y_novo_jogo = y_inicial
            
        # Botão Novo Jogo
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
            return perguntar_idade(tela)
            
        # Botão Sair
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
        
        pygame.display.update()


def perguntar_idade(tela):
    """
    Pergunta a idade do usuário e retorna o modo escuro baseado na resposta.
    
    Args:
        tela: Superfície do Pygame para renderização
        
    Returns:
        tuple: ('NOVO', dark_mode)
    """
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_texto = FONTE_TEXTO
    idade = ""
    
    # Cria um retângulo para o campo de entrada
    input_box = pygame.Rect(LARGURA_TELA//2 - resize(100, eh_X=True), 
                           ALTURA_TELA//2 - resize(200), 
                           resize(200, eh_X=True), 
                           resize(60))
                           
    cor_ativo = cor_com_escala_cinza(200, 200, 200)
    cor_inativo = cor_com_escala_cinza(150, 150, 150)
    cor_atual = cor_inativo
    ativo = True
    
    TransitionEffect.fade_out(tela, velocidade=15)
    
    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return tela_inicio_jogo(tela)  # Voltar para a tela inicial
                elif event.key == pygame.K_RETURN and idade:
                    try:
                        idade_num = int(idade)
                        dark_mode = idade_num >= 12
                        return ('NOVO', dark_mode)
                    except ValueError:
                        idade = ""
                elif event.key == pygame.K_BACKSPACE:
                    idade = idade[:-1]
                elif event.unicode.isdigit() and len(idade) < 3:
                    idade += event.unicode
            
            # Verifica se clicou na caixa de texto
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    ativo = True
                    cor_atual = cor_ativo
                else:
                    ativo = False
                    cor_atual = cor_inativo
                    
        # Desenhar fundo
        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)
        
        # Desenhar textos
        desenhar_texto("Qual é a sua idade?", fonte_titulo, COR_TITULO, tela, 
                      LARGURA_TELA//2 - resize(380, eh_X=True), resize(150))
        
        # Campo de entrada
        pygame.draw.rect(tela, cor_atual, input_box, border_radius=resize(10))
        txt_surface = fonte_texto.render(idade, True, (0, 0, 0))
        
        # Centraliza o texto no campo de entrada
        text_x = input_box.x + (input_box.width - txt_surface.get_width()) // 2
        text_y = input_box.y + (input_box.height - txt_surface.get_height()) // 2
        tela.blit(txt_surface, (text_x, text_y))
        
        # Instrução
        desenhar_texto("Digite sua idade e pressione Enter", fonte_texto, COR_TEXTO, tela, 
                     LARGURA_TELA//2 - resize(300, eh_X=True), ALTURA_TELA//2 - resize(100))            
        # Botão Voltar
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=ALTURA_TELA//2 + resize(200),
            largura=resize(400, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=FONTE_BOTAO,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_voltar:
            return tela_inicio_jogo(tela)  # Voltar para a tela inicial
        
        pygame.display.update()
