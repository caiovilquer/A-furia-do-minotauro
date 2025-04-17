import pygame
import sys
import json
import os
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, TransitionEffect
from utils.colors import cor_com_escala_cinza

def carregar_dados_personagens():
    """Carrega as informações dos personagens do arquivo JSON."""
    try:
        with open("Labirinto_game/data/personagens.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar arquivo de personagens: {e}")
        return {}

def carregar_imagem_personagem(nome_imagem):
    """Carrega a imagem de um personagem."""
    try:
        caminho = f"Labirinto_game/assets/images/characters/{nome_imagem}"
        if os.path.exists(caminho):
            imagem = pygame.image.load(caminho).convert_alpha()
            # Redimensionar para um tamanho adequado
            altura = resize(600)
            largura = altura * imagem.get_width() / imagem.get_height()
            return pygame.transform.scale(imagem, (int(largura), altura))
        else:
            print(f"Imagem não encontrada: {caminho}")
            return None
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        return None

def quebrar_texto_em_linhas(texto, fonte, largura_max):
    """Quebra um texto em múltiplas linhas para caber em uma largura máxima."""
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ''
    
    for palavra in palavras:
        teste_linha = linha_atual + ' ' + palavra if linha_atual else palavra
        largura_texto = fonte.size(teste_linha)[0]
        
        if largura_texto <= largura_max:
            linha_atual = teste_linha
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    
    if linha_atual:
        linhas.append(linha_atual)
    
    return linhas

def tela_personagens(tela):
    """Tela que mostra informações sobre os personagens do jogo."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_texto = pygame.font.Font(None, resize(36))
    fonte_botao = FONTE_BOTAO
    
    # Carrega os dados dos personagens
    dados_personagens = carregar_dados_personagens()
    
    # Lista de chaves dos personagens para navegar
    chaves_personagens = list(dados_personagens.keys())
    if not chaves_personagens:
        print("Nenhum personagem encontrado no arquivo JSON.")
        return
    
    # Índice do personagem atual
    indice_atual = 0
    
    # Largura máxima para o texto descritivo
    largura_max_texto = resize(800, eh_X=True)
    
    # Efeito de entrada
    TransitionEffect.fade_in(tela, velocidade=5)
    
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
        
        # Obtém o personagem atual
        chave_atual = chaves_personagens[indice_atual]
        personagem = dados_personagens[chave_atual]
        
        # Título da tela com o nome do personagem
        titulo_x = resize(100, eh_X=True)
        titulo_y = resize(50)
        desenhar_texto_sombra(personagem["nome"], fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        
        # Carrega e exibe a imagem do personagem
        imagem = carregar_imagem_personagem(personagem["imagem"])
        if imagem:
            posicao_x = LARGURA_TELA - imagem.get_width() - resize(100, eh_X=True)
            posicao_y = resize(150)
            tela.blit(imagem, (posicao_x, posicao_y))
        
        # Exibe a descrição do personagem
        linhas = quebrar_texto_em_linhas(personagem["descricao"], fonte_texto, largura_max_texto)
        descricao_y = titulo_y + resize(100)
        painel_descricao = pygame.Rect(
            titulo_x - resize(20, eh_X=True),
            descricao_y - resize(20),
            largura_max_texto + resize(40, eh_X=True),
            len(linhas) * resize(40) + resize(40)
        )
        # Desenha um painel semi-transparente para o texto
        painel_surface = pygame.Surface((painel_descricao.width, painel_descricao.height), pygame.SRCALPHA)
        pygame.draw.rect(
            painel_surface, 
            (30, 30, 50, 180), 
            pygame.Rect(0, 0, painel_descricao.width, painel_descricao.height),
            border_radius=resize(15)
        )
        tela.blit(painel_surface, (painel_descricao.x, painel_descricao.y))
        
        # Desenha o texto da descrição
        for i, linha in enumerate(linhas):
            desenhar_texto(linha, fonte_texto, COR_TEXTO, tela, titulo_x, descricao_y + i * resize(40))
        
        # Indicador de página
        texto_pagina = f"Personagem {indice_atual + 1} de {len(chaves_personagens)}"
        desenhar_texto(texto_pagina, fonte_texto, COR_TEXTO, tela, 
                      (LARGURA_TELA - fonte_texto.size(texto_pagina)[0]) // 2, 
                      ALTURA_TELA - resize(200))
        
        # Botões de navegação (anterior e próximo)
        clicou_anterior, _ = desenhar_botao(
            texto="Anterior",
            x=resize(100, eh_X=True),
            y=ALTURA_TELA - resize(150),
            largura=resize(250, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(50, 100, 200),
            cor_hover=cor_com_escala_cinza(80, 150, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_anterior:
            indice_atual = (indice_atual - 1) % len(chaves_personagens)
        
        clicou_proximo, _ = desenhar_botao(
            texto="Próximo",
            x=resize(400, eh_X=True),
            y=ALTURA_TELA - resize(150),
            largura=resize(250, eh_X=True),
            altura=resize(80),
            cor_normal=cor_com_escala_cinza(50, 100, 200),
            cor_hover=cor_com_escala_cinza(80, 150, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_proximo:
            indice_atual = (indice_atual + 1) % len(chaves_personagens)
        
        # Botão voltar
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA - resize(300, eh_X=True),
            y=ALTURA_TELA - resize(150),
            largura=resize(250, eh_X=True),
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
            return
        
        pygame.display.update()
