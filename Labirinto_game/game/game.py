import pygame
import sys
import time
import random
from datetime import datetime
import serial
from constants import (LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TEXTO, COR_TEXTO, PORTA_SELECIONADA)
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_barra_progresso
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios
from screens.game_over import tela_falhou
from screens.level_complete import tela_conclusao_nivel
from screens.game_complete import tela_conclusao

class JogoLabirinto:
    """Classe principal do jogo que gerencia o estado e a lógica do jogo."""
    
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
        """Atualiza o estado do labirinto."""
        pass

    def verificar_colisao(self):
        """Verifica se houve colisão."""
        # Exemplo local. Caso real, leríamos da serial.
        if random.random() < 0.002:
            self.progresso = random.random()
            self.vidas -= 1
            self.feedback_colisao()

    def feedback_colisao(self):
        """Fornece feedback visual/sonoro para colisão."""
        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        """Verifica se o nível foi concluído."""
        # Simulação de conclusão de nível (após 10s)
        if (time.time() - self.inicio_tempo) > 10:
            return True
        return False

    def salvar_progresso(self, tempo_gasto, falhou=False):
        """Salva o progresso do jogador."""
        usuario_data = self.usuarios_data[self.usuario]
        tentativa_info = {
            "nivel": self.nivel_atual,
            "tempo": tempo_gasto,
            "vidas": self.vidas,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        if self.nivel_atual >= self.usuarios_data[self.usuario]["nivel"] and not falhou and self.nivel_atual < 8:
            usuario_data["nivel"] = self.nivel_atual + 1
        usuario_data.setdefault("tentativas", []).append(tentativa_info)
        salvar_usuarios(self.usuarios_data)

    def loop_principal(self):
        """Loop principal do jogo."""
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        fonte_botao = pygame.font.SysFont("comicsansms", 40)  # Usando valor direto para evitar importação circular
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
                    self.salvar_progresso(tempo_total)
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