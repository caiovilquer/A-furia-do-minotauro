import pygame
import sys
import os
import json
import time
import random
from datetime import datetime


pygame.init()

# === CONFIGURAÇÕES BÁSICAS ===
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_JOGO = "Labirinto Sensorial"
FPS = 30

# CORES E ESTILO DE FONTE PARA ASPECTO PUZZLE
COR_TITULO = (250, 250, 100)  
COR_TEXTO = (255, 200, 0)   
COR_BOTAO_TEXTO = (0, 0, 0)   


FONTE_TITULO = pygame.font.SysFont("comicsansms", 80, bold=True)
FONTE_BOTAO = pygame.font.SysFont("comicsansms", 50)
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

# === BOTÃO ESTILIZADO ===
def desenhar_botao_estilizado(
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

    def atualizar_labirinto(self):
        pass

    def verificar_colisao(self):
        # chance de colisão meramente ilustrativa
        if random.random() < 0.002:
            self.vidas -= 1
            self.feedback_colisao()

    def feedback_colisao(self):
        pass

    def verifica_conclusao_nivel(self):
        # Simulação de conclusão de nível
        if (time.time() - self.inicio_tempo) > 5:
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

            # Botão Voltar
            clicou_voltar, _ = desenhar_botao_estilizado(
                texto="Voltar",
                x=50,
                y=300,
                largura=200,
                altura=70,
                cor_normal=(255, 200, 0),
                cor_hover=(255, 255, 0),
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
                print("Você perdeu todas as vidas! Reiniciando nível...")
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)
                self.vidas = 3
                self.inicio_tempo = time.time()

            # Se concluiu o nível
            if self.verifica_conclusao_nivel():
                tempo_total = time.time() - self.inicio_tempo
                
                if self.nivel_atual >= 8:
                    tela_conclusao(tela);
                    return
                else:
                    self.salvar_progresso(tempo_total)
                    self.nivel_atual, self.jogo_ativo = tela_conclusao_nivel(tela, self.nivel_atual, tempo_total)
                    self.vidas = 3
                    self.inicio_tempo = time.time()
                

            # Mostrar textos (posicionados e espaçados)
            desenhar_texto(f"Usuário: {self.usuario}", self.fonte, COR_TEXTO, self.tela, 30, 30)
            desenhar_texto(f"Nível: {self.nivel_atual}", self.fonte, COR_TEXTO, self.tela, 30, 90)
            desenhar_texto(f"Vidas: {self.vidas}", self.fonte, COR_TEXTO, self.tela, 30, 150)
            desenhar_texto(f"Tempo: {int(time.time() - self.inicio_tempo)} s", self.fonte, COR_TEXTO, self.tela, 30, 210)

            pygame.display.update()

# === TELA DE ESCOLHA DE USUÁRIO ===
def tela_escolha_usuario(tela):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    input_font = FONTE_TEXTO

    usuarios_data = carregar_usuarios()
    lista_usuarios = list(usuarios_data.keys())

    # Ajuste de posicionamento para evitar sobreposição
    titulo_x = LARGURA_TELA//2 - 400
    titulo_y = 100

    y_inicial_botoes = 250  # onde começam a listar os usuários
    espacamento_botoes = 90 # espaçamento entre botões de usuários

    # onde ficará a input_box, abaixo dos botões
    input_box = pygame.Rect(LARGURA_TELA//2 - 200, y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + 50, 400, 60)

    cor_ativo = (200, 200, 200)
    cor_inativo = (150, 150, 150)
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

        # Para cada usuário, criamos DOIS botões: selecionar e deletar
        for usr in lista_usuarios:
            # Botão do usuário
            x_user_btn = LARGURA_TELA//2 - 220
            y_user_btn = y_offset
            w_user_btn = 300
            h_user_btn = 70

            # Botão deletar ao lado
            x_del_btn = x_user_btn + w_user_btn + 20
            w_del_btn = 120
            h_del_btn = 70

            clicou_user, _ = desenhar_botao_estilizado(
                texto=usr,
                x=x_user_btn,
                y=y_user_btn,
                largura=w_user_btn,
                altura=h_user_btn,
                cor_normal=(0, 200, 0),
                cor_hover=(0, 255, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=10
            )
            if clicou_user:
                return usr

            clicou_delete, _ = desenhar_botao_estilizado(
                texto="Del",
                x=x_del_btn,
                y=y_user_btn,
                largura=w_del_btn,
                altura=h_del_btn,
                cor_normal=(200, 0, 0),
                cor_hover=(255, 0, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=10
            )
            if clicou_delete:
                # Apagar este usuário do JSON
                if usr in usuarios_data:
                    del usuarios_data[usr]
                salvar_usuarios(usuarios_data)
                # Apagar da lista local para não gerar erro
                lista_usuarios.remove(usr)
                input_box = pygame.Rect(LARGURA_TELA//2 - 200, y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + 50, 400, 60)
                break 

            y_offset += espacamento_botoes

        # Caixa de texto para novo usuário
        pygame.draw.rect(tela, cor_atual, input_box, 0, border_radius=10)
        txt_surface = input_font.render(usuario_digitado, True, PRETO)
        tela.blit(txt_surface, (input_box.x+10, input_box.y+10))
        desenhar_texto("Novo usuário e ENTER:", input_font, COR_TEXTO, tela, input_box.x, input_box.y - 50)

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

        # Botão Voltar
        clicou_voltar, _ = desenhar_botao_estilizado(
            texto="Voltar",
            x=LARGURA_TELA//2 - 300,
            y=600,
            largura=400,
            altura=70,
            cor_normal=(255, 200, 0),
            cor_hover=(255, 255, 0),
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

        # Botão Rejogar Nível
        clicou_rejogar, _ = desenhar_botao_estilizado(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - 300,
            y=600,
            largura=400,
            altura=70,
            cor_normal=(50, 200, 50),
            cor_hover=(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return nivel, True
        
        # Botão Avançar Nível
        clicou_avancar, _ = desenhar_botao_estilizado(
            texto="Avançar Nível",
            x=LARGURA_TELA//2 - 300,
            y=700,
            largura=400,
            altura=70,
            cor_normal=(50, 50, 200),
            cor_hover=(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_avancar:
            return nivel + 1, True
        
        # Botão Voltar
        clicou_voltar, _ = desenhar_botao_estilizado(
            texto="Voltar",
            x=LARGURA_TELA//2 - 300,
            y=800,
            largura=400,
            altura=70,
            cor_normal=(255, 200, 0),
            cor_hover=(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return nivel, False

        pygame.display.update()

# === TELA DE MENU PARA REJOGAR NÍVEIS ===
def tela_rejogar(tela, usuario):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO

    usuarios_data = carregar_usuarios()
    nivel_atual = usuarios_data[usuario]["nivel"]
    niveis_disponiveis = list(range(1, nivel_atual + 1))

    titulo_x = LARGURA_TELA//2 - 400
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
            clicou, _ = desenhar_botao_estilizado(
                texto=txt_btn,
                x=LARGURA_TELA//2 - 200,
                y=y_offset,
                largura=200,
                altura=70,
                cor_normal=(50, 50, 200),
                cor_hover=(80, 80, 255),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=15
            )
            if clicou:
                return lvl
            y_offset += espacamento

        # Botão Voltar
        clicou_voltar, _ = desenhar_botao_estilizado(
            texto="Voltar",
            x=LARGURA_TELA//2 - 300,
            y=y_offset,
            largura=400,
            altura=70,
            cor_normal=(255, 200, 0),
            cor_hover=(255, 255, 0),
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

    # Níveis presentes nas tentativas
    niveis_jogados = sorted(set(t["nivel"] for t in tentativas))
    if not niveis_jogados:
        niveis_jogados = [1]

    indice_nivel_selecionado = 0

    def mostrar_tentativas_nivel(nivel_escolhido):
        # Exibiremos apenas as 6 últimas para evitar overlap
        all_t = [t for t in tentativas if t["nivel"] == nivel_escolhido]
        return all_t[-6:]  # as últimas 6

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

        # Botões de navegação de nível
        clicou_ant, _ = desenhar_botao_estilizado(
            texto="<",
            x=100,
            y=300,
            largura=80,
            altura=80,
            cor_normal=(150,150,150),
            cor_hover=(200,200,200),
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

        clicou_prox, _ = desenhar_botao_estilizado(
            texto=">",
            x=220,
            y=300,
            largura=80,
            altura=80,
            cor_normal=(150,150,150),
            cor_hover=(200,200,200),
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

        # Botão Voltar
        clicou_voltar, _ = desenhar_botao_estilizado(
            texto="Voltar",
            x=100,
            y=y_pos + 50,
            largura=400,
            altura=70,
            cor_normal=(255, 200, 0),
            cor_hover=(255, 255, 0),
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

        # Espaçamento vertical entre botões
        y_inicial = 300
        espacamento_botoes = 120

        clicou_jogar, _ = desenhar_botao_estilizado(
            texto="Iniciar Jogo",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial,
            largura=400,
            altura=80,
            cor_normal=(50, 200, 50),
            cor_hover=(50, 255, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_jogar:
            return "JOGAR"

        clicou_desempenho, _ = desenhar_botao_estilizado(
            texto="Ver Desempenho",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes,
            largura=400,
            altura=80,
            cor_normal=(50, 50, 200),
            cor_hover=(50, 50, 255),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_desempenho:
            return "DESEMPENHO"

        clicou_rejogar, _ = desenhar_botao_estilizado(
            texto="Rejogar Nível",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*2,
            largura=400,
            altura=80,
            cor_normal=(180, 100, 50),
            cor_hover=(200, 140, 50),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_rejogar:
            return "REJOGAR"

        clicou_voltar, _ = desenhar_botao_estilizado(
            texto="Voltar",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*3,
            largura=400,
            altura=80,
            cor_normal=(255, 200, 0),
            cor_hover=(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=None,
            border_radius=15
        )
        if clicou_voltar:
            return "VOLTAR"

        clicou_sair, _ = desenhar_botao_estilizado(
            texto="Sair",
            x=LARGURA_TELA//2 - 200,
            y=y_inicial + espacamento_botoes*4,
            largura=400,
            altura=80,
            cor_normal=(200, 50, 50),
            cor_hover=(255, 50, 50),
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

# === FUNÇÃO PRINCIPAL ===
def main():
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JOGO)

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
