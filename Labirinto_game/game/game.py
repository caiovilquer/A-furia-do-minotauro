import pygame
import sys
import time
import random
from datetime import datetime
import serial
from constants import (BUTTON_PATH, FONTE_BOTAO, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TEXTO, COR_TEXTO, PORTA_SELECIONADA)
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_barra_progresso, resize, TransitionEffect
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios
from screens.game_over import tela_falhou
from screens.level_complete import tela_conclusao_nivel
from screens.game_complete import tela_conclusao
from utils.dialog_manager import GerenciadorDialogos
from utils.achievements import SistemaConquistas

class JogoLabirinto:
    """Classe principal do jogo que gerencia o estado e a lógica do jogo."""
    
    def __init__(self, tela, usuario, nivel_inicial=None, sistema_conquistas=None):
        self.tela = tela
        self.usuario = usuario
        self.clock = pygame.time.Clock()
        self.fonte = FONTE_TEXTO
        if sistema_conquistas:
            self.sistema_conquistas = sistema_conquistas
        else:
            self.sistema_conquistas = SistemaConquistas()
        self.sistema_conquistas.carregar_conquistas_usuario(usuario)
        self.colisoes = 0 
        self.usuarios_data = carregar_usuarios()
        
        if nivel_inicial is not None:
            self.nivel_atual = nivel_inicial
        else:
            self.nivel_atual = self.usuarios_data[usuario]["nivel"]

        # Criação do gerenciador de diálogos
        self.gerenciador_dialogos = GerenciadorDialogos(
            tela, 
            "Labirinto_game/data/dialogos_fases.json"
        )

        # Flag para controlar se o diálogo inicial da fase já foi mostrado
        # Quando o jogo inicia, não mostramos o diálogo ainda
        self.mostrou_dialogo_fase_atual = False


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
        if random.random() < 0.00:
            self.progresso = random.random()
            self.vidas -= 1
            self.colisoes += 1
            self.feedback_colisao()

    def feedback_colisao(self):
        """Fornece feedback visual/sonoro para colisão."""
        from utils.audio_manager import audio_manager
        audio_manager.play_sound("collision")
        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        """Verifica se o nível foi concluído."""
        # Simulação de conclusão de nível (após 10s)
        if (time.time() - self.inicio_tempo) > 3:
            return True
        return False

    def salvar_progresso(self, tempo_gasto, falhou=False):
        """Salva o progresso do jogador."""
        usuario_data = self.usuarios_data[self.usuario]
        
        # Preparar informações da tentativa
        tentativa_info = {
            "nivel": self.nivel_atual,
            "tempo": tempo_gasto,
            "vidas": self.vidas,
            "colisoes": self.colisoes,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        
        # Adicionar a nova tentativa à lista
        usuario_data.setdefault("tentativas", []).append(tentativa_info)
        
        # Atualizar o nível máximo desbloqueado
        if self.nivel_atual >= self.usuarios_data[self.usuario]["nivel"] and not falhou and self.nivel_atual < 8:
            usuario_data["nivel"] = self.nivel_atual + 1
              
        salvar_usuarios(self.usuarios_data)
        
        # Preparar dados para verificação de conquistas (APÓS atualizar tentativas)
        dados_jogo = {
            'nivel_atual': self.nivel_atual,
            'tempo_gasto': tempo_gasto,
            'colisoes': self.colisoes,
            'tentativas': usuario_data.get('tentativas', []),
            'vidas': self.vidas,
            'concluido': not falhou
        }
        
        # Verificar conquistas com os dados atualizados
        conquistas_desbloqueadas = self.sistema_conquistas.verificar_conquistas(self.usuario, dados_jogo)
        
        # Tocar som de sucesso se o nível foi concluído com sucesso
        if not falhou:
            from utils.audio_manager import audio_manager
            audio_manager.play_sound("success")
        elif falhou:
            from utils.audio_manager import audio_manager
            audio_manager.play_sound("failure")

    def resetar_nivel(self):
        """Reseta o estado do jogo para o próximo nível"""
        self.vidas = 3
        self.progresso = 0.0
        self.colisoes = 0
        self.inicio_tempo = time.time()
        # Recarga explícita das conquistas para garantir estado atualizado
        self.sistema_conquistas.limpar_notificacoes()
        self.sistema_conquistas.carregar_conquistas_usuario(self.usuario)
        self.usuarios_data = carregar_usuarios()
        # Reset da flag de diálogo de fase
        self.mostrou_dialogo_fase_atual = False
        print(f"Estado do jogo resetado.")

    def mostrar_dialogo_fase(self):
        """Mostra o diálogo correspondente à fase atual."""
        if not self.mostrou_dialogo_fase_atual:
            if self.nivel_atual == 2:
                from utils.audio_manager import audio_manager
                audio_manager.play_sound("earthquake")
            TransitionEffect.fade_out(self.tela, velocidade=10)
            
            # Nome da fase para buscar no arquivo de diálogos
            fase_dialogo = f"fase_{self.nivel_atual}"
            
            # Executar o diálogo
            self.gerenciador_dialogos.executar(fase_dialogo, efeito_sonoro=None)
            
            # Marca que o diálogo já foi mostrado para esta sessão de jogo
            self.mostrou_dialogo_fase_atual = True

    def loop_principal(self, pular_dialogo=False):
        """Loop principal do jogo."""
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.NOFRAME)
        info_x = resize(200, eh_X=True)
        info_y = resize(300)
        
        # Antes de iniciar o loop principal, mostramos o diálogo da fase
        nome_cena = f"fase_{self.nivel_atual}"
        if not pular_dialogo:
            # Exiba o diálogo e marque como visto
            self.gerenciador_dialogos.executar(nome_cena)
            from utils.user_data import marcar_dialogo_como_visto
            marcar_dialogo_como_visto(self.usuario, nome_cena)
        else:
            # Pula o diálogo pois estamos repetindo o nível
            pass
        
        # Reinicia o timer após o diálogo (importante!)
        self.inicio_tempo = time.time()
        
        while self.jogo_ativo:
            events = pygame.event.get()
            self.clock.tick(FPS)

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.jogo_ativo = False
                        return

            self.atualizar_labirinto()
            self.verificar_colisao()

            # Desenho de fundo
            if background_img:
                self.tela.blit(background_img, (0, 0))
            else:
                self.tela.fill(AZUL_CLARO)

            # BOTÃO VOLTAR
            clicou_voltar, _ = desenhar_botao(
                texto="VOLTAR",
                x=resize(200, eh_X=True),
                y=resize(600),
                largura=resize(200, eh_X=True),
                altura=resize(70),
                cor_normal=cor_com_escala_cinza(255, 200, 0),
                cor_hover=cor_com_escala_cinza(255, 255, 0),
                fonte=FONTE_BOTAO,
                tela=self.tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(15)
            )
            if clicou_voltar:
                self.jogo_ativo = False
                return

            # Se acabou as vidas
            if self.vidas <= 0:
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)
                self.jogo_ativo = tela_falhou(tela, self.sistema_conquistas)
                
                # Se decidiu continuar, reseta o nível e mostra o diálogo novamente
                if self.jogo_ativo:
                    self.resetar_nivel()
                    # Reinicia o loop para mostrar o diálogo novamente
                    return self.loop_principal()

            # Se concluiu o nível
            if self.verifica_conclusao_nivel():
                tempo_total = time.time() - self.inicio_tempo
                    
                if self.nivel_atual >= 8:
                    # Mostrar diálogo de conclusão (vitória)
                    self.gerenciador_dialogos.executar("vitoria", efeito_sonoro="success")
                    self.salvar_progresso(tempo_total)
                    # Garantir que as conquistas sejam salvas explicitamente
                    self.sistema_conquistas.salvar_conquistas_usuario(self.usuario)
                    # Mostrar tela de conclusão do jogo
                    tela_conclusao(tela, self.sistema_conquistas)
                    self.resetar_nivel()
                    return
                else:
                    self.salvar_progresso(tempo_total)
                    # Garantir que as conquistas sejam salvas explicitamente
                    self.sistema_conquistas.salvar_conquistas_usuario(self.usuario)
                    # Avança para o próximo nível
                    proximo_nivel = self.nivel_atual + 1
                    
                    # Mostra tela de conclusão do nível atual
                    continuar_jogando, repetir_nivel, pular_dialogo = tela_conclusao_nivel(tela, self.nivel_atual, tempo_total, self.sistema_conquistas)
                    
                    if not continuar_jogando:
                        # Jogador optou por sair
                        self.jogo_ativo = False
                        return
                    
                    # Define o próximo nível (continuar ou repetir)
                    self.nivel_atual = self.nivel_atual if repetir_nivel else proximo_nivel
                    
                    # Reseta o estado do jogo para o próximo nível
                    self.resetar_nivel()
                    
                    # Reinicia o loop para mostrar o diálogo do próximo nível
                    return self.loop_principal(pular_dialogo=pular_dialogo)

            # Mostrar textos (posicionados e espaçados)
            desenhar_texto(f"Usuário: {self.usuario}", self.fonte, COR_TEXTO, self.tela, info_x, info_y)
            desenhar_texto(f"Nível: {self.nivel_atual}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + resize(60))
            desenhar_texto(f"Vidas: {self.vidas}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + resize(120))
            desenhar_texto(f"Tempo: {int(time.time() - self.inicio_tempo)} s", self.fonte, COR_TEXTO, self.tela, info_x, info_y + resize(180))

            cor_barra_fundo = cor_com_escala_cinza(50, 50, 50)
            cor_barra_frente = cor_com_escala_cinza(0, 200, 0)
            desenhar_barra_progresso(
                self.tela,
                x=info_x,
                y=info_y + resize(241),
                largura=resize(400, eh_X=True),
                altura=resize(40),
                progresso=self.progresso,
                cor_fundo=cor_barra_fundo,
                cor_barra=cor_barra_frente,
                cor_outline=cor_com_escala_cinza(255, 255, 255),
                border_radius=resize(10)
            )
            pygame.display.update()