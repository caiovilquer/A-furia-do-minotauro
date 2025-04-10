import pygame
import sys
import os
import json
import time
import random
from datetime import datetime
import serial
import math 
import serial.tools.list_ports

pygame.init()

# === CONFIGURAÇÕES BÁSICAS ===
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_JOGO = "Labirinto Sensorial"
FPS = 60

# FLAGS GLOBAIS
ESCALA_CINZA = False  # Ajuste para True se quiser todos os botões em escala de cinza
SOM_LIGADO = True  # Ajuste para False se quiser desativar os sons
PORTA_SELECIONADA = None  # Para armazenar a escolha da porta serial do Arduino

# FUNÇÃO AUXILIAR PARA CONVERTER COR EM ESCALA DE CINZA
def to_gray(r, g, b):
    gray = int(0.2989*r + 0.5870*g + 0.1140*b)
    return (gray, gray, gray)

# CORES E ESTILO DE FONTE PARA ASPECTO PUZZLE
COR_TITULO = (250, 250, 100)
COR_TEXTO = (255, 200, 0)
COR_BOTAO_TEXTO = (255, 255, 255)

FONTE_TITULO = pygame.font.SysFont("comicsansms", 80, bold=True)
FONTE_BOTAO = pygame.font.SysFont("comicsansms", 40)
FONTE_BARRA = pygame.font.SysFont("comicsansms", 30)
FONTE_TEXTO = pygame.font.SysFont("comicsansms", 40)

# Demais cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARELO = (255, 255, 0)
AZUL_CLARO = (173, 216, 230)

# Arquivo de background
BACKGROUND_PATH = "images/background_labirinto.png"
USUARIOS_JSON = "usuarios.json"

# Carregar imagem de fundo se existir
if os.path.exists(BACKGROUND_PATH):
    background_img = pygame.image.load(BACKGROUND_PATH)
    background_img = pygame.transform.scale(background_img, (LARGURA_TELA, ALTURA_TELA))
else:
    background_img = None

# === FUNÇÃO PARA DESENHAR TEXTO ===
def desenhar_texto(texto, fonte, cor, superficie, x, y):
    text_obj = fonte.render(texto, True, cor)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    superficie.blit(text_obj, text_rect)

# === FUNÇÕES PARA CARREGAR E SALVAR USUÁRIOS ===
def carregar_usuarios():
    if not os.path.exists(USUARIOS_JSON):
        return {}
    with open(USUARIOS_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            data = {}
    return data

def salvar_usuarios(data):
    with open(USUARIOS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# === FUNÇÃO AUXILIAR PARA OBTER COR COM ESCALA_DE_CINZA ===
def cor_com_escala_cinza(r, g, b):
    if not ESCALA_CINZA:
        return (r, g, b)
    else:
        return to_gray(r, g, b)

# === BOTÃO ESTILIZADO ===
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

# === FUNÇÃO PARA DESENHAR UMA BARRA DE PROGRESSO ===
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

    fonte = FONTE_BARRA
    percent_txt = f"Progresso: {int(progresso * 100)}%"
    text_render = fonte.render(percent_txt, True, (255,255,255))
    text_rect = text_render.get_rect(center=(x + largura//2, y + altura//2 - 3))

    tela.blit(bar_surface, (x, y))
    tela.blit(text_render, text_rect)

# === FUNÇÕES DE TELA ===

def tela_falhou(tela):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    titulo_x = LARGURA_TELA//2 - 600
    titulo_y = 400

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Você perdeu todas as vidas!", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - 241,
            y=600,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(50, 200, 50),
            cor_hover=cor_com_escala_cinza(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return True
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - 241,
            y=700,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return False

        pygame.display.update()

def tela_conclusao(tela):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    titulo_x = LARGURA_TELA//2 - 800
    titulo_y = 400

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Parabéns! Você concluiu todos os níveis!", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - 241,
            y=600,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return

        pygame.display.update()

def tela_conclusao_nivel(tela, nivel, tempo):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    titulo_x = LARGURA_TELA//2 - 900
    titulo_y = 400

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto(f"Parabéns! Você concluiu o nível {nivel} em {tempo:.2f}s !", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2-241,
            y=600,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(0, 200, 50),
            cor_hover=cor_com_escala_cinza(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return nivel, True
        
        clicou_avancar, _ = desenhar_botao(
            texto="Avançar Nível",
            x=LARGURA_TELA//2-241,
            y=700,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(50, 50, 200),
            cor_hover=cor_com_escala_cinza(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_avancar:
            return nivel + 1, True
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2- 241,
            y=800,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return nivel, False

        pygame.display.update()

def tela_selecao_porta(tela):
    global PORTA_SELECIONADA
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    lista_portas = [p.device for p in serial.tools.list_ports.comports()]

    titulo_x = LARGURA_TELA//2 - 580
    titulo_y = 80

    y_inicial_botoes = 250
    espacamento_botoes = 90

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Selecione a porta do Arduino", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_offset = y_inicial_botoes
        for port in lista_portas:
            clicou, _ = desenhar_botao(
                texto=port,
                x=LARGURA_TELA//2 - 160,
                y=y_offset,
                largura=300,
                altura=60,
                cor_normal=cor_com_escala_cinza(0, 150, 200),
                cor_hover=cor_com_escala_cinza(0, 200, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                border_radius=10
            )
            if clicou:
                PORTA_SELECIONADA = port
                return port
            y_offset += espacamento_botoes

        # Caso não tenha porta ou para simulação
        clicou_semport, _ = desenhar_botao(
            texto="Simulação",
            x=LARGURA_TELA//2 - 160,
            y=y_offset + 100,
            largura=300,
            altura=60,
            cor_normal=cor_com_escala_cinza(180, 100, 50),
            cor_hover=cor_com_escala_cinza(200, 120, 60),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            border_radius=10
        )
        if clicou_semport:
            PORTA_SELECIONADA = None
            return None

        pygame.display.update()


# === CLASSE DO JOGO ===
class JogoLabirinto:
    def __init__(self, tela, usuario, nivel_inicial=None):
        self.tela = tela
        self.usuario = usuario
        self.clock = pygame.time.Clock()
        self.fonte = FONTE_TEXTO

        self.usuarios_data = carregar_usuarios()
        
        if nivel_inicial is not None:
            self.nivel_atual = nivel_inicial
        else:
            self.nivel_atual = self.usuarios_data[usuario]["nivel"]

        self.vidas = 3
        self.inicio_tempo = time.time()
        self.jogo_ativo = True

        # Progresso do jogador (de 0.0 a 1.0)
        self.progresso = 0.0

        if PORTA_SELECIONADA:
             self.arduino = serial.Serial(PORTA_SELECIONADA, 9600)
        else:
             self.arduino = None

    def atualizar_labirinto(self):
        pass

    def verificar_colisao(self):
        # Exemplo local. Caso real, leríamos da serial.
        if random.random() < 0.002:
            self.progresso = random.random()
            self.vidas -= 1
            self.feedback_colisao()

    def feedback_colisao(self):
        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        # Simulação de conclusão de nível (após 10s)
        if (time.time() - self.inicio_tempo) > 10:
            return True
        return False

    def salvar_progresso(self, tempo_gasto, falhou=False):
        usuario_data = self.usuarios_data[self.usuario]
        tentativa_info = {
            "nivel": self.nivel_atual,
            "tempo": tempo_gasto,
            "vidas": self.vidas,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        if self.nivel_atual >= self.usuarios_data[self.usuario]["nivel"] and not falhou:
            usuario_data["nivel"] = self.nivel_atual + 1
        usuario_data.setdefault("tentativas", []).append(tentativa_info)
        salvar_usuarios(self.usuarios_data)

    def loop_principal(self):
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        fonte_botao = FONTE_BOTAO
        info_x = 200
        info_y = 300
        while self.jogo_ativo:
            events = pygame.event.get()
            self.clock.tick(FPS)

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.atualizar_labirinto()
            self.verificar_colisao()

            # Desenho de fundo
            if background_img:
                self.tela.blit(background_img, (0, 0))
            else:
                self.tela.fill(AZUL_CLARO)

            # BOTÃO VOLTAR
            clicou_voltar, _ = desenhar_botao(
                texto="Voltar",
                x=200,
                y=600,
                largura=200,
                altura=70,
                cor_normal=cor_com_escala_cinza(255, 200, 0),
                cor_hover=cor_com_escala_cinza(255, 255, 0),
                fonte=fonte_botao,
                tela=self.tela,
                events=events,
                imagem_fundo=None,
                border_radius=15
            )
            if clicou_voltar:
                self.jogo_ativo = False
                return

            # Se acabou as vidas
            if self.vidas <= 0:
                self.jogo_ativo = tela_falhou(tela)
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)
                self.vidas = 3
                self.inicio_tempo = time.time()

            # Se concluiu o nível
            if self.verifica_conclusao_nivel():
                tempo_total = time.time() - self.inicio_tempo
                if self.nivel_atual >= 8:
                    tela_conclusao(tela)
                    return
                else:
                    self.salvar_progresso(tempo_total)
                    self.nivel_atual, self.jogo_ativo = tela_conclusao_nivel(tela, self.nivel_atual, tempo_total)
                    self.vidas = 3
                    self.inicio_tempo = time.time()

            # Mostrar textos (posicionados e espaçados)
            desenhar_texto(f"Usuário: {self.usuario}", self.fonte, COR_TEXTO, self.tela, info_x, info_y)
            desenhar_texto(f"Nível: {self.nivel_atual}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + 60)
            desenhar_texto(f"Vidas: {self.vidas}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + 120)
            desenhar_texto(f"Tempo: {int(time.time() - self.inicio_tempo)} s", self.fonte, COR_TEXTO, self.tela, info_x, info_y + 180)

            cor_barra_fundo = cor_com_escala_cinza(50, 50, 50)
            cor_barra_frente = cor_com_escala_cinza(0, 200, 0)
            desenhar_barra_progresso(
                self.tela,
                x=info_x,
                y=info_y + 241,
                largura=400,
                altura=40,
                progresso=self.progresso,
                cor_fundo=cor_barra_fundo,
                cor_barra=cor_barra_frente,
                cor_outline=cor_com_escala_cinza(255, 255, 255),
                border_radius=10
            )

            pygame.display.update()

# === TELA DE ESCOLHA DE USUÁRIO ===
def tela_escolha_usuario(tela):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    input_font = FONTE_TEXTO

    usuarios_data = carregar_usuarios()
    lista_usuarios = list(usuarios_data.keys())

    titulo_x = LARGURA_TELA//2 - 400
    titulo_y = 100

    y_inicial_botoes = 250  # onde começam a listar os usuários
    espacamento_botoes = 90 # espaçamento entre botões de usuários

    input_box = pygame.Rect(LARGURA_TELA//2 - 200, y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + 50, 400, 60)

    cor_ativo = cor_com_escala_cinza(200, 200, 200)
    cor_inativo = cor_com_escala_cinza(150, 150, 150)
    cor_atual = cor_inativo
    usuario_digitado = ""
    ativo_input = False

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    ativo_input = True
                    cor_atual = cor_ativo
                else:
                    ativo_input = False
                    cor_atual = cor_inativo
            elif event.type == pygame.KEYDOWN:
                if ativo_input:
                    if event.key == pygame.K_RETURN:
                        if usuario_digitado.strip() != "":
                            if usuario_digitado.strip() not in usuarios_data:
                                usuarios_data[usuario_digitado.strip()] = {
                                    "nivel": 1,
                                    "tentativas": []
                                }
                                salvar_usuarios(usuarios_data)

                            return usuario_digitado.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        usuario_digitado = usuario_digitado[:-1]
                    else:
                        usuario_digitado += event.unicode

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Selecione ou Crie um Usuário", fonte_titulo, COR_TITULO, tela, titulo_x-150, titulo_y)

        # Lista de usuários
        y_offset = y_inicial_botoes
        for usr in lista_usuarios:
            x_user_btn = LARGURA_TELA//2 - 220
            y_user_btn = y_offset
            w_user_btn = 300
            h_user_btn = 70

            x_del_btn = x_user_btn + w_user_btn + 20
            w_del_btn = 120
            h_del_btn = 70

            clicou_user, _ = desenhar_botao(
                texto=usr,
                x=x_user_btn,
                y=y_user_btn,
                largura=w_user_btn,
                altura=h_user_btn,
                cor_normal=cor_com_escala_cinza(0, 200, 0),
                cor_hover=cor_com_escala_cinza(0, 255, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=10
            )
            if clicou_user:
                return usr

            clicou_delete, _ = desenhar_botao(
                texto="Del",
                x=x_del_btn,
                y=y_user_btn,
                largura=w_del_btn,
                altura=h_del_btn,
                cor_normal=cor_com_escala_cinza(200, 0, 0),
                cor_hover=cor_com_escala_cinza(255, 0, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=10
            )
            if clicou_delete:
                if usr in usuarios_data:
                    del usuarios_data[usr]
                salvar_usuarios(usuarios_data)
                lista_usuarios.remove(usr)
                input_box = pygame.Rect(LARGURA_TELA//2 - 200, y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + 50, 400, 60)
                break

            y_offset += espacamento_botoes

        pygame.draw.rect(tela, cor_atual, input_box, 0, border_radius=10)
        txt_surface = input_font.render(usuario_digitado, True, PRETO)
        tela.blit(txt_surface, (input_box.x+10, input_box.y+10))
        desenhar_texto("Novo usuário e ENTER:", input_font, COR_TEXTO, tela, input_box.x, input_box.y - 50)

        pygame.display.update()

# === TELA DE MENU PARA REJOGAR NÍVEIS ===
def tela_rejogar(tela, usuario):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    usuarios_data = carregar_usuarios()
    nivel_atual = usuarios_data[usuario]["nivel"]
    niveis_disponiveis = list(range(1, nivel_atual + 1))

    titulo_x = LARGURA_TELA//2 - 300
    titulo_y = 100
    y_inicial_botoes = 250
    espacamento = 90

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Rejogar Níveis", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_offset = y_inicial_botoes
        for lvl in niveis_disponiveis:
            txt_btn = f"Nível {lvl}"
            clicou, _ = desenhar_botao(
                texto=txt_btn,
                x=LARGURA_TELA//2-130,
                y=y_offset,
                largura=200,
                altura=70,
                cor_normal=cor_com_escala_cinza(50, 50, 200),
                cor_hover=cor_com_escala_cinza(80, 80, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=15
            )
            if clicou:
                return lvl
            y_offset += espacamento

        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - 241,
            y=y_offset,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return None

        pygame.display.update()

# === TELA DE DESEMPENHO ===
def tela_desempenho(tela, usuario):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_texto = FONTE_TEXTO
    fonte_botao = FONTE_BOTAO

    usuarios_data = carregar_usuarios()
    nivel = usuarios_data[usuario].get("nivel", 1)
    tentativas = usuarios_data[usuario].get("tentativas", [])

    niveis_jogados = sorted(set(t["nivel"] for t in tentativas))
    if not niveis_jogados:
        niveis_jogados = [1]

    indice_nivel_selecionado = 0

    def mostrar_tentativas_nivel(nivel_escolhido):
        all_t = [t for t in tentativas if t["nivel"] == nivel_escolhido]
        return all_t[-6:]

    titulo_x = 100
    titulo_y = 50

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

        desenhar_texto(f"Desempenho de {usuario}", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        desenhar_texto(f"Nível atual: {nivel}", fonte_texto, COR_TEXTO, tela, 100, 180)
        
        clicou_ant, _ = desenhar_botao(
            texto="<",
            x=100,
            y=300,
            largura=80,
            altura=80,
            cor_normal=cor_com_escala_cinza(150,150,150),
            cor_hover=cor_com_escala_cinza(200,200,200),
            fonte=pygame.font.SysFont("arial", 50),
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=40
        )
        if clicou_ant:
            indice_nivel_selecionado -= 1
            if indice_nivel_selecionado < 0:
                indice_nivel_selecionado = 0

        clicou_prox, _ = desenhar_botao(
            texto=">",
            x=220,
            y=300,
            largura=80,
            altura=80,
            cor_normal=cor_com_escala_cinza(150,150,150),
            cor_hover=cor_com_escala_cinza(200,200,200),
            fonte=pygame.font.SysFont("arial", 50),
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=40
        )
        if clicou_prox:
            indice_nivel_selecionado += 1
            if indice_nivel_selecionado >= len(niveis_jogados):
                indice_nivel_selecionado = len(niveis_jogados) - 1

        nivel_escolhido = niveis_jogados[indice_nivel_selecionado]
        desenhar_texto(f"Nível escolhido: {nivel_escolhido}", fonte_texto, COR_TEXTO, tela, 320, 320)

        desenhar_texto("Tentativas desse nível (últimas 6):", fonte_texto, COR_TEXTO, tela, 100, 400)
        tentativas_nivel = mostrar_tentativas_nivel(nivel_escolhido)
        if tentativas_nivel:
            melhor_tentativa = min(tentativas_nivel, key=lambda x: x["tempo"] if x["vidas"] > 0 else float('inf'))
            desenhar_texto(f"Melhor tempo: {melhor_tentativa['tempo']:.2f} s", fonte_texto, COR_TEXTO, tela, 100, 480)
        else:
            desenhar_texto("Nenhuma tentativa registrada.", fonte_texto, COR_TEXTO, tela, 100, 480)
        y_pos = 560
        for idx, tent in enumerate(tentativas_nivel):
            texto_tent = (
                f"Tempo: {tent['tempo']:.2f}s, Vidas: {tent['vidas']}, "
                f"Data: {tent['timestamp']}"
            )
            if tent['vidas'] == 0:
                texto_tent += " (Não concluído)"
            else:
                texto_tent += " (Concluído)"
            desenhar_texto(f"{idx+1} - {texto_tent}", fonte_texto, COR_TEXTO, tela, 100, y_pos)
            y_pos += 50

        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=100,
            y=y_pos + 50,
            largura=400,
            altura=70,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return

        pygame.display.update()

# === TELA DE MENU PRINCIPAL ===
def tela_menu_principal(tela, usuario):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    global ESCALA_CINZA, COR_TITULO, COR_TEXTO, SOM_LIGADO

    titulo_x = LARGURA_TELA//2 - 350
    titulo_y = 100

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto(f"Bem-vindo, {usuario}!", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)

        y_inicial = 300
        espacamento_botoes = 120

        clicou_jogar, _ = desenhar_botao(
            texto="Iniciar Jogo",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial,
            largura=400,
            altura=80,
            cor_normal=cor_com_escala_cinza(180, 100, 50),
            cor_hover=cor_com_escala_cinza(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_jogar:
            return "JOGAR"

        clicou_desempenho, _ = desenhar_botao(
            texto="Ver Desempenho",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes,
            largura=400,
            altura=80,
            cor_normal=cor_com_escala_cinza(50, 50, 200),
            cor_hover=cor_com_escala_cinza(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_desempenho:
            return "DESEMPENHO"

        clicou_rejogar, _ = desenhar_botao(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*2,
            largura=400,
            altura=80,
            cor_normal=cor_com_escala_cinza(0, 200, 0),
            cor_hover=cor_com_escala_cinza(0, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return "REJOGAR"

        clicou_escala, _ = desenhar_botao(
            texto="Desativar Escala de Cinza" if ESCALA_CINZA else "Ativar Escala de Cinza",
            x=LARGURA_TELA - 500,
            y= ALTURA_TELA-100,
            largura=500,
            altura=80,
            cor_normal=cor_com_escala_cinza(100, 100, 100),
            cor_hover=cor_com_escala_cinza(150, 150, 150),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_escala:
            ESCALA_CINZA = not ESCALA_CINZA
            COR_TITULO = cor_com_escala_cinza(250, 250, 100)
            COR_TEXTO = cor_com_escala_cinza(255, 200, 0)
        
        clicou_som, _ = desenhar_botao(
            texto="Ativar Som" if not SOM_LIGADO else "Desativar Som",
            x=LARGURA_TELA - 500,
            y= ALTURA_TELA-200,
            largura=500,
            altura=80,
            cor_normal=cor_com_escala_cinza(100, 100, 100),
            cor_hover=cor_com_escala_cinza(150, 150, 150),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_som:
            SOM_LIGADO = not SOM_LIGADO
            # se quisesse ligar/desligar musica
            # if SOM_LIGADO:
            #     pygame.mixer.music.unpause()
            # else:
            #     pygame.mixer.music.pause()
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*4,
            largura=400,
            altura=80,
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return "VOLTAR"

        clicou_sair, _ = desenhar_botao(
            texto="Sair",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*5,
            largura=400,
            altura=80,
            cor_normal=cor_com_escala_cinza(200, 50, 50),
            cor_hover=cor_com_escala_cinza(255, 50, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_sair:
            pygame.quit()
            sys.exit()

        pygame.display.update()

def tela_inicial(tela):

    clock = pygame.time.Clock()
    rodando = True

    # Texto e fonte
    mensagem = "Pressione qualquer botão para iniciar!"
    fonte = pygame.font.SysFont("comicsansms", 80, bold=True)

    # Posição base (fixa) e parâmetros de movimento
    base_x = LARGURA_TELA // 2
    base_y = ALTURA_TELA // 2 - 80
    amplitude = 40.0   # até onde o texto “sobe e desce”
    frequencia = 0.5   # quantas “oscilações” por segundo

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

    
# === FUNÇÃO PRINCIPAL ===
def main():
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)
    
    tela_inicial(tela)
    
    porta_escolhida = tela_selecao_porta(tela)
    print("PORTA ESCOLHIDA:", porta_escolhida)


    usuario_escolhido = tela_escolha_usuario(tela)


    while True:
        acao = tela_menu_principal(tela, usuario_escolhido)
        if acao == "JOGAR":
            jogo = JogoLabirinto(tela, usuario_escolhido)
            jogo.loop_principal()
        elif acao == "DESEMPENHO":
            tela_desempenho(tela, usuario_escolhido)
        elif acao == "REJOGAR":
            nivel_escolhido = tela_rejogar(tela, usuario_escolhido)
            if nivel_escolhido is not None:
                jogo = JogoLabirinto(tela, usuario_escolhido, nivel_inicial=nivel_escolhido)
                jogo.loop_principal()
        elif acao == "VOLTAR":
            usuario_escolhido = tela_escolha_usuario(tela)
        else:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
