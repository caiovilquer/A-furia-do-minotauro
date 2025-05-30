import pygame
import sys
import os
import time
import random
import math
from datetime import datetime
from constants import (BUTTON_PATH, FONTE_BOTAO, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TEXTO, COR_TEXTO, PORTA_SELECIONADA, SOUND_PATH, dialogo_dentro_img)
from utils.drawing import aplicar_filtro_cinza_superficie, desenhar_texto, desenhar_botao, resize, TransitionEffect
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios
from screens.game_over import tela_falhou
from screens.level_complete import tela_conclusao_nivel
from screens.game_complete import tela_conclusao
from utils.dialog_manager import GerenciadorDialogos
from utils.achievements import SistemaConquistas

class JogoLabirinto:
    """Classe principal do jogo que gerencia o estado e a lógica do jogo."""
    
    def __init__(self, tela, usuario, nivel_inicial=None, sistema_conquistas=None, conexao_serial=None):
        self.tela = tela
        self.usuario = usuario
        self.clock = pygame.time.Clock()
        self.fonte = FONTE_TEXTO
        self.conexao_serial = conexao_serial
        
        # Para o timer visual
        self.timer_raio = resize(50)
        self.timer_centro = (LARGURA_TELA - resize(100, eh_X=True), resize(100))
        self.timer_espessura = resize(8)
        self.timer_cor_fundo = (80, 80, 80)
        self.timer_cor = (0, 200, 200)
        
        # Para efeitos de colisão
        self.flash_ativo = False
        self.flash_inicio = 0
        self.flash_duracao = 0.3  # segundos
        self.flash_cor = (255, 0, 0, 150)  # Vermelho semi-transparente
        
        # Para controles de áudio
        self.icone_som_ligado = None
        self.icone_som_desligado = None
        self.som_ligado = True
        self.carregar_icones_audio()
        
        if sistema_conquistas:
            self.sistema_conquistas = sistema_conquistas
        else:
            self.sistema_conquistas = SistemaConquistas()
        self.sistema_conquistas.carregar_conquistas_usuario(usuario)
        self.colisoes = 0 
        self.usuarios_data = carregar_usuarios()
        
        # Configurações para comunicação serial
        self.buffer_serial = ""
        self.ultima_verificacao = time.time()
        self.intervalo_verificacao = 0.05  # 50ms entre leituras
        
        if nivel_inicial is not None:
            self.nivel_atual = nivel_inicial
        else:
            self.nivel_atual = self.usuarios_data[usuario]["nivel"]

        # Obter melhor tempo do jogador para este nível
        self.melhor_tempo = self.obter_melhor_tempo()
        
        # Configurações para nomes e temas dos níveis
        self.nomes_niveis = {
            1: "O Labirinto Inicial",
            2: "Corredores Sinuosos",
            3: "Caminho das Sombras",
            4: "Jardim do Minotauro",
            5: "Passagem Secreta",
            6: "Caverna dos Ecos",
            7: "Salão dos Heróis",
            8: "Confronto Final"
        }
        
        # Nomes dos arquivos de imagem de fundo para cada nível
        self.background_files = {
            1: "initial_labyrinth.png",
            2: "winding_corridors.png",
            3: "path_of_shadows.png",
            4: "minotaurs_garden.png",
            5: "secret_passage.png",
            6: "echo_cavern.png",
            7: "hall_of_heroes.png",
            8: "final_confrontation.png"
        }
        
        # Dicionário para armazenar as imagens de fundo carregadas
        self.background_images = {}
        
        # Carregar as imagens de fundo
        self.carregar_imagens_fundo()
        
        # Elementos temáticos para cada nível (posição na tela, imagem)
        self.carregar_elementos_tematicos()

        # Criação do gerenciador de diálogos - agora com acesso às imagens de fundo
        self.gerenciador_dialogos = GerenciadorDialogos(
            tela, 
            "Labirinto_game/data/dialogos_fases.json",
            background_images=self.background_images  # Passamos as imagens de fundo carregadas
        )

        # Flag para controlar se o diálogo inicial da fase já foi mostrado
        # Quando o jogo inicia, não mostramos o diálogo ainda
        self.mostrou_dialogo_fase_atual = False

        self.vidas = 3
        # Configurações de exibição dos corações
        self.tamanho_coracao = resize(150)
        self.posicao_y_coracoes = resize(320) 
        self.espacamento_coracoes = resize(25) 
        self.estados_coracoes = [True, True, True]
        self.progresso_animacao_coracoes = [0.0, 0.0, 0.0] 
        self.duracao_animacao_coracoes = 0.5

        self.inicio_tempo = time.time()
        self.jogo_ativo = True
        
        # Para transições mais suaves
        self.transicao_ativa = False
        self.transicao_tipo = None
        self.transicao_progresso = 0

        # Progresso do jogador (de 0.0 a 1.0)
        self.progresso = 0.0
        
        # Para indicadores de conquistas próximas
        self.conquistas_proximas = self.verificar_conquistas_proximas()
        
        # Enviar nível atual para o Arduino se necessário
        if self.conexao_serial:
            self.enviar_nivel_arduino()
            
    def carregar_icones_audio(self):
        """Carrega os ícones de controle de áudio"""
        try:
            self.icone_som_ligado = pygame.image.load(f"{SOUND_PATH}/icons/sound_on.png").convert_alpha()
            self.icone_som_desligado = pygame.image.load(f"{SOUND_PATH}/icons/sound_off.png").convert_alpha()
            
            # Redimensionar ícones
            tamanho = resize(40)
            self.icone_som_ligado = pygame.transform.scale(self.icone_som_ligado, (tamanho, tamanho))
            self.icone_som_desligado = pygame.transform.scale(self.icone_som_desligado, (tamanho, tamanho))
        except Exception as e:
            print(f"Erro ao carregar ícones de áudio: {e}")
            # Criar ícones de fallback
            self.icone_som_ligado = self.criar_icone_som(True)
            self.icone_som_desligado = self.criar_icone_som(False)
    
    def criar_icone_som(self, ligado):
        """Cria um ícone de som básico usando primitivas do pygame"""
        tamanho = resize(40)
        icone = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        
        if ligado:
            # Desenha um alto-falante com ondas sonoras
            pygame.draw.rect(icone, (200, 200, 200), (5, 12, 10, 16))
            pygame.draw.polygon(icone, (200, 200, 200), [(15, 12), (25, 5), (25, 35), (15, 28)])
            for i in range(3):
                offset = (i+1) * 5
                pygame.draw.arc(icone, (200, 200, 200), 
                                (25, 12 - offset, offset * 2, offset * 4),
                                math.pi * 0.25, math.pi * 0.75, 2)
        else:
            # Desenha um alto-falante com X
            pygame.draw.rect(icone, (200, 200, 200), (5, 12, 10, 16))
            pygame.draw.polygon(icone, (200, 200, 200), [(15, 12), (25, 5), (25, 35), (15, 28)])
            pygame.draw.line(icone, (255, 0, 0), (28, 10), (35, 30), 3)
            pygame.draw.line(icone, (255, 0, 0), (35, 10), (28, 30), 3)
            
        return icone
            
    def carregar_elementos_tematicos(self):
        """Carrega os elementos temáticos para cada nível"""
        self.elementos_tematicos = {}
        
        try:
            # Define os caminhos para os elementos de cada nível
            elementos_niveis = {
                1: ["column_greek.png", "greek_vase.png"],
                2: ["statue_small.png", "torch.png"],
                3: ["spider_web.png", "skull.png"],
                4: ["plant_vine.png", "fountain.png"],
                5: ["old_key.png", "ancient_rune.png"],
                6: ["stalactite.png", "crystal_blue.png"],
                7: ["shield_gold.png", "sword_bronze.png"],
                8: ["minotaur_shadow.png", "broken_chain.png"]
            }
            
            # Para cada nível, carrega os elementos e define suas posições
            for nivel, elementos in elementos_niveis.items():
                self.elementos_tematicos[nivel] = []
                
                for i, elem in enumerate(elementos):
                    try:
                        caminho = f"Labirinto_game/assets/images/theme_elements/{elem}"
                        imagem = pygame.image.load(caminho).convert_alpha()
                        
                        # Redimensiona a imagem
                        largura = resize(100, eh_X=True)
                        altura = int(largura * imagem.get_height() / imagem.get_width())
                        imagem = pygame.transform.scale(imagem, (largura, altura))
                        
                        # Define uma posição para o elemento (personalizar conforme necessário)
                        if i == 0:
                            pos = (resize(50, eh_X=True), ALTURA_TELA - altura - resize(50))
                            pass
                        else:
                            pos = (LARGURA_TELA - largura - resize(50, eh_X=True), ALTURA_TELA - altura - resize(50))
                        
                        self.elementos_tematicos[nivel].append((imagem, pos))
                    except Exception as e:
                        print(f"Erro ao carregar elemento temático {elem}: {e}")
        except Exception as e:
            print(f"Erro ao carregar elementos temáticos: {e}")

    def carregar_imagens_fundo(self):
        """Carrega as imagens de fundo para cada nível"""
        try:
            for nivel, arquivo in self.background_files.items():
                caminho = f"Labirinto_game/assets/images/backgrounds/{arquivo}"
                try:
                    imagem = pygame.image.load(caminho).convert()
                    
                    # Redimensiona para caber na tela
                    imagem = pygame.transform.scale(imagem, (LARGURA_TELA, ALTURA_TELA))
                    
                    self.background_images[nivel] = imagem
                    print(f"Imagem de fundo carregada para nível {nivel}: {arquivo}")
                except Exception as e:
                    print(f"Erro ao carregar imagem de fundo para nível {nivel}: {e}")
                    self.background_images[nivel] = None
        except Exception as e:
            print(f"Erro geral ao carregar imagens de fundo: {e}")

    def obter_melhor_tempo(self):
        """Obtém o melhor tempo do jogador para o nível atual"""
        tentativas = self.usuarios_data.get(self.usuario, {}).get("tentativas", [])
        # Filtra tentativas bem-sucedidas do nível atual
        tentativas_nivel = [t for t in tentativas if t.get("nivel") == self.nivel_atual and t.get("vidas", 0) > 0]
        
        if tentativas_nivel:
            # Retorna o melhor tempo
            return min(t.get("tempo", float('inf')) for t in tentativas_nivel)
        return None

    def verificar_conquistas_proximas(self):
        """Verifica quais conquistas estão próximas de serem desbloqueadas"""
        conquistas_proximas = []
        
        # Lista de tentativas do usuário
        tentativas = self.usuarios_data.get(self.usuario, {}).get("tentativas", [])
        

        if not self.sistema_conquistas.conquistas['pegadas_de_bronze']['desbloqueada']:
            total_jogos = len(tentativas)
            if total_jogos >= 25:  # Reduzido para 25 (50% de 50)
                conquistas_proximas.append({
                    'chave': 'pegadas_de_bronze',
                    'nome': self.sistema_conquistas.conquistas['pegadas_de_bronze']['nome'],
                    'progresso': min(1.0, total_jogos / 50),
                    'meta': 50,
                    'atual': total_jogos
                })
        

        if not self.sistema_conquistas.conquistas['domador_do_labirinto']['desbloqueada']:
            niveis_completados = set(t.get('nivel') for t in tentativas if t.get('vidas', 0) > 0)
            if len(niveis_completados) >= 2:  # Reduzido para 2 (40% de 5)
                conquistas_proximas.append({
                    'chave': 'domador_do_labirinto',
                    'nome': self.sistema_conquistas.conquistas['domador_do_labirinto']['nome'],
                    'progresso': min(1.0, len(niveis_completados) / 5),
                    'meta': 5,
                    'atual': len(niveis_completados)
                })
                

        if not self.sistema_conquistas.conquistas['renascido']['desbloqueada']:
            nivel_atual = self.nivel_atual
            tentativas_nivel = [t for t in tentativas if t.get('nivel') == nivel_atual]
            if len(tentativas_nivel) >= 3:  # Reduzido para 3 (43% de 7)
                conquistas_proximas.append({
                    'chave': 'renascido',
                    'nome': self.sistema_conquistas.conquistas['renascido']['nome'],
                    'progresso': min(1.0, len(tentativas_nivel) / 7),
                    'meta': 7,
                    'atual': len(tentativas_nivel)
                })
        

        if not self.sistema_conquistas.conquistas['heroi_de_atenas']['desbloqueada']:
            niveis_completados = set(t.get('nivel') for t in tentativas if t.get('vidas', 0) > 0)
            total_niveis = 8  
            if len(niveis_completados) >= 7:  
                conquistas_proximas.append({
                    'chave': 'heroi_de_atenas',
                    'nome': self.sistema_conquistas.conquistas['heroi_de_atenas']['nome'],
                    'progresso': min(1.0, len(niveis_completados) / total_niveis),
                    'meta': total_niveis,
                    'atual': len(niveis_completados)
                })
        

        if not self.sistema_conquistas.conquistas['velocista_olimpico']['desbloqueada']:

            tentativas_sucesso = [t for t in tentativas if t.get('vidas', 0) > 0]
            if tentativas_sucesso:
                # Encontrar o melhor tempo
                melhor_tempo = min(t.get('tempo', float('inf')) for t in tentativas_sucesso)
                # Se o melhor tempo está abaixo de 15s, está próximo (mas acima de 10s)
                if 10 < melhor_tempo < 15:
                    # O progresso é inversamente proporcional ao tempo
                    # 15s = 0% progresso, 10s = 100% progresso
                    progresso = (15 - melhor_tempo) / 5
                    conquistas_proximas.append({
                        'chave': 'velocista_olimpico',
                        'nome': self.sistema_conquistas.conquistas['velocista_olimpico']['nome'],
                        'progresso': progresso,
                        'meta': "10s",
                        'atual': f"{melhor_tempo:.1f}s"
                    })
        

        if not self.sistema_conquistas.conquistas['coragem_de_teseu']['desbloqueada']:
            # Procurar tentativas onde o jogador completou perdendo apenas 1 vida
            tentativas_quase_perfeitas = [
                t for t in tentativas 
                if t.get('vidas', 0) == 2  
            ]
            if tentativas_quase_perfeitas:
                # Se tem pelo menos uma tentativa quase perfeita
                conquistas_proximas.append({
                    'chave': 'coragem_de_teseu',
                    'nome': self.sistema_conquistas.conquistas['coragem_de_teseu']['nome'],
                    'progresso': 0.7,
                    'meta': "3 vidas",
                    'atual': "2 vidas"
                })
        
        if not self.sistema_conquistas.conquistas['despertar_da_furia']['desbloqueada']:
            # Ver quantas vezes o jogador completou níveis perdendo 1 vida
            tentativas_perdendo_uma = [
                t for t in tentativas 
                if t.get('vidas', 0) == 2  # Completou com 2 vidas (perdeu 1)
            ]
            if tentativas_perdendo_uma:
                conquistas_proximas.append({
                    'chave': 'despertar_da_furia',
                    'nome': self.sistema_conquistas.conquistas['despertar_da_furia']['nome'],
                    'progresso': 0.5,
                    'meta': "Perder 2 vidas",
                    'atual': "Perdeu 1 vida"
                })
        
        # Ordenar conquistas pelo progresso (maiores progressos primeiro)
        conquistas_proximas.sort(key=lambda c: c['progresso'], reverse=True)
        
        return conquistas_proximas[:3]  # Retorna as 3 mais próximas para dar mais variedade

    def enviar_nivel_arduino(self):
        """Envia o nível atual para o Arduino."""
        try:
            # Formato da mensagem: "NIVEL:X\n" onde X é o número do nível
            mensagem = f"NIVEL:{self.nivel_atual}\n".encode()
            self.conexao_serial.write(mensagem)
            self.conexao_serial.flush()
            print(f"Enviado nível {self.nivel_atual} para o Arduino")
        except Exception as e:
            print(f"Erro ao enviar nível para Arduino: {e}")

    def atualizar_labirinto(self):
        """Atualiza o estado do labirinto."""
        if self.conexao_serial:
            self.ler_dados_serial()
        else:
            # Simulação quando não há comunicação com Arduino
            self.simular_progresso()

    def simular_progresso(self):
        """Simular progresso para modo de demonstração."""
        incremento = random.uniform(0.001, 0.005)
        self.progresso = min(1.0, self.progresso + incremento)
        
        # Simula colisões ocasionalmente
        if random.random() < 0.001:
            self.vidas -= 1
            self.colisoes += 1
            self.feedback_colisao()
            
        # Simular conclusão se alcançar progresso completo
        if self.progresso >= 1.0:
            # Termina o nível após 10 segundos ou quando atingir 100%
            if (time.time() - self.inicio_tempo) > 10:
                return True

    def ler_dados_serial(self):
        """Lê dados da porta serial para atualizar estado do jogo."""
        agora = time.time()
        
        # Verifica a cada intervalo para não sobrecarregar a CPU
        if (agora - self.ultima_verificacao) >= self.intervalo_verificacao:
            self.ultima_verificacao = agora
            
            try:
                if self.conexao_serial and self.conexao_serial.in_waiting > 0:
                    dados = self.conexao_serial.readline().decode('utf-8').strip()
                    self.processar_dados_serial(dados)
            except Exception as e:
                print(f"Erro na leitura serial: {e}")

    def processar_dados_serial(self, dados):
        """Processa os dados recebidos do Arduino."""
        print(f"Dados recebidos: {dados}")
        
        # Formato esperado dos dados: COMANDO:VALOR
        # Exemplos: PROGRESSO:0.75, COLISAO:1, CONCLUIDO:1
        try:
            if ':' in dados:
                comando, valor = dados.split(':', 1)
                
                if comando == "PROGRESSO":
                    self.progresso = float(valor)
                    
                elif comando == "COLISAO":
                    if int(valor) == 1:
                        self.vidas -= 1
                        self.colisoes += 1
                        self.feedback_colisao()
                        
                elif comando == "CONCLUIDO":
                    if int(valor) == 1:
                        # Marca o nível como concluído
                        self.progresso = 1.0
                        
        except Exception as e:
            print(f"Erro ao processar dados: {e}")


    def feedback_colisao(self):
        """Fornece feedback visual/sonoro para colisão."""
        from utils.audio_manager import audio_manager
        
        audio_manager.play_sound("collision")
        
        # Escolhe o áudio dublado correto baseado no número de vidas restantes
        # Nota: self.vidas já foi decrementado antes desta chamada
        if self.vidas == 1: # Será 1 após esta colisão se era 2 antes
            audio_manager.play_voiced_dialogue("colisao_1vida")
        elif self.vidas == 2: # Será 2 após esta colisão se era 3 antes
            audio_manager.play_voiced_dialogue("colisao_2vidas")
        
        self.flash_ativo = True
        self.flash_inicio = time.time()

        # Aciona a animação do coração
        # self.vidas é o número de vidas RESTANTES.
        # Corações são indexados 0, 1, 2.
        # Se 3 vidas -> 2 vidas restantes, coração no índice 2 é perdido.
        # Se 2 vidas -> 1 vida restante, coração no índice 1 é perdido.
        # Se 1 vida -> 0 vidas restantes, coração no índice 0 é perdido.
        indice_coracao_perdido = self.vidas 
        if 0 <= indice_coracao_perdido < 3 and self.estados_coracoes[indice_coracao_perdido]:
            # Inicia a animação apenas se não já iniciada
            if self.progresso_animacao_coracoes[indice_coracao_perdido] == 0.0: 
                self.progresso_animacao_coracoes[indice_coracao_perdido] = 0.01 # Inicia animação
            # O estado self.estados_coracoes[indice_coracao_perdido] será definido como False quando a animação completar.

        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        """Verifica se o nível foi concluído."""

        if self.conexao_serial:
            return self.progresso >= 1.0
        else:
            return (time.time() - self.inicio_tempo) > 10 or self.progresso >= 1.0

    def salvar_progresso(self, tempo_gasto, falhou=False):
        """Salva o progresso do jogador."""
        usuario_data = self.usuarios_data[self.usuario]
        

        tentativa_info = {
            "nivel": self.nivel_atual,
            "tempo": tempo_gasto,
            "vidas": self.vidas,
            "colisoes": self.colisoes,
            "timestamp": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        

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
            'vidas_restantes': self.vidas,
            'vidas_iniciais': 3,
            'concluido': not falhou
        }
        
        # Verificar conquistas com os dados atualizados
        conquistas_desbloqueadas = self.sistema_conquistas.verificar_conquistas(self.usuario, dados_jogo)
        
        if not falhou:
            from utils.audio_manager import audio_manager
            audio_manager.play_sound("success")
        elif falhou:
            from utils.audio_manager import audio_manager
            audio_manager.play_sound("failure")

    def resetar_nivel(self):
        """Reseta o estado do jogo para o próximo nível"""
        self.vidas = 3
        self.estados_coracoes = [True, True, True]
        self.progresso_animacao_coracoes = [0.0, 0.0, 0.0]
        self.progresso = 0.0
        # Recarga explícita das conquistas para garantir estado atualizado
        self.sistema_conquistas.limpar_notificacoes()
        self.sistema_conquistas.carregar_conquistas_usuario(self.usuario)
        self.usuarios_data = carregar_usuarios()
        # Reset da flag de diálogo de fase
        self.mostrou_dialogo_fase_atual = False
        
        self.melhor_tempo = self.obter_melhor_tempo()
        
        self.conquistas_proximas = self.verificar_conquistas_proximas()
        
        if self.conexao_serial:
            self.enviar_nivel_arduino()
            
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
            

            self.gerenciador_dialogos.executar(fase_dialogo, efeito_sonoro=None)
            
            self.mostrou_dialogo_fase_atual = True

    def desenhar_timer_visual(self, tempo_atual):
        """Desenha um timer visual animado"""
        # Convertemos o tempo em segundos para um ângulo (círculo completo = 60 segundos)
        segundos = int(tempo_atual) % 60
        angulo_segundos = segundos * 6
        
        # Desenhamos o círculo de fundo
        pygame.draw.circle(self.tela, self.timer_cor_fundo, self.timer_centro, self.timer_raio)
        
        # Desenhamos o arco que representa o tempo
        rect_timer = pygame.Rect(
            self.timer_centro[0] - self.timer_raio, 
            self.timer_centro[1] - self.timer_raio,
            self.timer_raio * 2, 
            self.timer_raio * 2
        )
        # Começando em -90 graus (topo) e movendo no sentido horário
        pygame.draw.arc(self.tela, self.timer_cor, rect_timer, 
                         math.radians(-90), math.radians(angulo_segundos - 90),
                         self.timer_espessura)
        
        # Desenhamos os marcadores de 15, 30, 45 segundos
        for i in range(4):
            angulo = math.radians(i * 90 - 90)  # -90, 0, 90, 180 graus
            x1 = self.timer_centro[0] + (self.timer_raio - self.timer_espessura) * math.cos(angulo)
            y1 = self.timer_centro[1] + (self.timer_raio - self.timer_espessura) * math.sin(angulo)
            x2 = self.timer_centro[0] + (self.timer_raio + self.timer_espessura/2) * math.cos(angulo)
            y2 = self.timer_centro[1] + (self.timer_raio + self.timer_espessura/2) * math.sin(angulo)
            pygame.draw.line(self.tela, (200, 200, 200), (x1, y1), (x2, y2), 2)
        
        # Desenhamos o ponteiro dos segundos
        angulo = math.radians(angulo_segundos - 90)
        x_ponta = self.timer_centro[0] + (self.timer_raio - self.timer_espessura/2) * math.cos(angulo)
        y_ponta = self.timer_centro[1] + (self.timer_raio - self.timer_espessura/2) * math.sin(angulo)
        pygame.draw.line(self.tela, (255, 255, 255), self.timer_centro, (x_ponta, y_ponta), 3)
        
        # Texto do tempo no centro
        minutos = int(tempo_atual) // 60
        segundos = int(tempo_atual) % 60
        tempo_texto = f"{minutos:02d}:{segundos:02d}"
        fonte_tempo = pygame.font.SysFont("Arial", resize(24, eh_X=True), bold=True)
        texto_surface = fonte_tempo.render(tempo_texto, True, (255, 255, 255))
        texto_rect = texto_surface.get_rect(center=self.timer_centro)
        self.tela.blit(texto_surface, texto_rect)

    def desenhar_nome_nivel(self):
        """Desenha o nome/título do nível atual na parte superior da tela"""
        nome_nivel = self.nomes_niveis.get(self.nivel_atual, f"Nível {self.nivel_atual}")
        
        titulo_fonte = pygame.font.SysFont("Arial", resize(42, eh_X=True), bold=True)
        texto_surface = titulo_fonte.render(nome_nivel, True, (255, 255, 255))
        texto_rect = texto_surface.get_rect(center=(LARGURA_TELA // 2, resize(50)))
        
        # Desenha uma faixa semitransparente atrás do texto
        faixa_rect = texto_rect.copy()
        faixa_rect.inflate_ip(resize(40, eh_X=True), resize(20))
        faixa_surface = pygame.Surface((faixa_rect.width, faixa_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(faixa_surface, (0, 0, 0, 150), 
                         pygame.Rect(0, 0, faixa_rect.width, faixa_rect.height),
                         border_radius=resize(15))
        self.tela.blit(faixa_surface, faixa_rect)
        
        # Adiciona borda dourada à faixa
        pygame.draw.rect(self.tela, cor_com_escala_cinza(255, 215, 0), 
                         faixa_rect, width=resize(2), border_radius=resize(15))
        

        self.tela.blit(texto_surface, texto_rect)
        
        # # Adiciona um pequeno ícone ou decoração relacionada ao nível
        # if self.nivel_atual in self.elementos_tematicos and len(self.elementos_tematicos[self.nivel_atual]) > 0:
        #     icone, _ = self.elementos_tematicos[self.nivel_atual][0]  # Usa o primeiro elemento como ícone
        #     icone_pequeno = pygame.transform.scale(icone, (resize(30, eh_X=True), resize(30)))
        #     self.tela.blit(icone_pequeno, (faixa_rect.left + resize(10, eh_X=True), faixa_rect.centery - resize(15)))

    def desenhar_elementos_tematicos(self):
        """Desenha elementos decorativos temáticos do nível atual"""
        if self.nivel_atual in self.elementos_tematicos:
            for elemento, posicao in self.elementos_tematicos[self.nivel_atual]:
                self.tela.blit(elemento, posicao)

    def desenhar_melhor_tempo(self):
        """Desenha informação de melhor tempo/recorde do jogador"""
        if self.melhor_tempo is not None:
            texto = f"Recorde: {self.melhor_tempo:.2f}s"
            fonte_recorde = pygame.font.SysFont("Arial", resize(32, eh_X=True), bold=True)
            texto_surface = fonte_recorde.render(texto, True, (255, 215, 0))  # Cor dourada
            

            x = self.timer_centro[0] - texto_surface.get_width()//2 - resize(25, eh_X=True)
            y = self.timer_centro[1] + self.timer_raio + resize(20)
            
            self.tela.blit(texto_surface, (x, y))

    def desenhar_indicadores_conquistas(self):
        """Desenha indicadores de conquistas próximas de serem desbloqueadas"""
        if not self.conquistas_proximas:
            return
            
        x = resize(20, eh_X=True)
        y = ALTURA_TELA - resize(600)  
        largura = resize(500, eh_X=True)  
        altura_painel = resize(50)  
        espacamento = resize(15)
        
        # Cria painel de fundo para os indicadores
        altura_total = resize(45) + len(self.conquistas_proximas) * (altura_painel + espacamento)
        painel_rect = pygame.Rect(x - resize(10, eh_X=True), y - resize(40), largura + resize(20, eh_X=True), altura_total)
        

        painel_surf = pygame.Surface((painel_rect.width, painel_rect.height), pygame.SRCALPHA)
        
        for i in range(painel_rect.height):
            # Gradiente de cor escura a cor menos escura
            alpha = 180  # Transparência geral do painel
            fator = i / painel_rect.height
            r = int(30 + 10 * fator)
            g = int(30 + 10 * fator)
            b = int(60 + 20 * fator)
            pygame.draw.line(painel_surf, (r, g, b, alpha), 
                            (0, i), (painel_rect.width, i))
        
        pygame.draw.rect(painel_surf, (0, 0, 0, 0), 
                        pygame.Rect(0, 0, painel_rect.width, painel_rect.height), 
                        border_radius=resize(15))
        

        self.tela.blit(painel_surf, painel_rect)
        
        # Borda dourada para o painel
        pygame.draw.rect(self.tela, (255, 215, 0, 150), painel_rect, 
                        width=resize(2), border_radius=resize(15))
        
        # Desenha título estilizado
        fonte_titulo = pygame.font.SysFont("Arial", resize(26, eh_X=True), bold=True)
        titulo_texto = "Conquistas Próximas"
        titulo_surface = fonte_titulo.render(titulo_texto, True, (255, 215, 0))
        titulo_rect = titulo_surface.get_rect(centerx=painel_rect.centerx, top=y - resize(35))
        
        # Adiciona um brilho sutil ao título
        brilho_surf = pygame.Surface((titulo_surface.get_width() + resize(10, eh_X=True), 
                                      titulo_surface.get_height() + resize(10)), pygame.SRCALPHA)
        brilho_rect = brilho_surf.get_rect(center=titulo_rect.center)
        pygame.draw.rect(brilho_surf, (255, 215, 0, 50), 
                         pygame.Rect(0, 0, brilho_surf.get_width(), brilho_surf.get_height()), 
                         border_radius=resize(10))
        self.tela.blit(brilho_surf, brilho_rect)
        self.tela.blit(titulo_surface, titulo_rect)
        

        for i, conquista in enumerate(self.conquistas_proximas):

            y_atual = y + i * (altura_painel + espacamento)
            
            # Rect para o indicador completo (inclui ícone e barra)
            indicador_rect = pygame.Rect(x, y_atual, largura, altura_painel)
            
            # Efeito pulsante baseado no progresso
            pulso = math.sin(time.time() * 3) * 0.2 + 0.8
            intensidade_pulso = int(40 * pulso * conquista['progresso'])
            
            # Fundo do indicador com efeito pulsante
            fundo_cor = (50 + intensidade_pulso, 50 + intensidade_pulso, 70 + intensidade_pulso)
            pygame.draw.rect(self.tela, fundo_cor, indicador_rect, border_radius=resize(10))
            
            # Carrega o ícone da conquista
            icone = None
            tamanho_icone = resize(32)
            chave = conquista['chave']
            
            if chave in self.sistema_conquistas.conquistas:
                caminho_icone = self.sistema_conquistas.conquistas[chave].get('icone')
                if caminho_icone and os.path.exists(caminho_icone):
                    try:
                        # Carrega e redimensiona o ícone
                        icone_original = pygame.image.load(caminho_icone).convert_alpha()
                        icone = pygame.transform.scale(icone_original, (tamanho_icone, tamanho_icone))
                    except Exception as e:
                        print(f"Erro ao carregar ícone de conquista: {e}")
            

            if icone:
                icone_rect = icone.get_rect(midleft=(x + resize(5, eh_X=True), indicador_rect.centery))
                self.tela.blit(icone, icone_rect)
            else:
                # Círculo como fallback se não conseguir carregar o ícone
                pygame.draw.circle(self.tela, (150, 150, 150), 
                                  (x + resize(16, eh_X=True), indicador_rect.centery), 
                                  tamanho_icone // 2)
            
 
            x_barra = x + tamanho_icone + resize(15, eh_X=True)  # Aumentado o espaçamento
            largura_barra = largura - tamanho_icone - resize(25, eh_X=True)  # Ajustado para o novo tamanho
  
            
            pygame.draw.rect(self.tela, (30, 30, 30), 
                            pygame.Rect(x_barra, y_atual + resize(5), largura_barra, altura_painel - resize(10)), 
                            border_radius=resize(7))
            
            # Barra de progresso preenchida com gradiente
            largura_preenchida = int(largura_barra * conquista['progresso'])
            if largura_preenchida > 0:
                barra_surf = pygame.Surface((largura_preenchida, altura_painel - resize(10)), pygame.SRCALPHA)
                
                # Cria um gradiente horizontal
                for px in range(largura_preenchida):
                    # Varia de azul para dourado baseado no progresso
                    fator = px / largura_preenchida
                    r = int(100 + fator * 155)
                    g = int(150 + fator * 65)
                    b = int(255 - fator * 200)
                    pygame.draw.line(barra_surf, (r, g, b), 
                                    (px, 0), (px, altura_painel - resize(10)))
                
                # Aplica a barra com cantos arredondados
                self.tela.blit(barra_surf, (x_barra, y_atual + resize(5)))
            
            # Borda da barra
            pygame.draw.rect(self.tela, (200, 200, 200), 
                            pygame.Rect(x_barra, y_atual + resize(5), largura_barra, altura_painel - resize(10)), 
                            width=resize(1), border_radius=resize(7))
            
            fonte_conquista = pygame.font.SysFont("Arial", resize(16, eh_X=True), bold=True)  
            
            # Limitando o comprimento do texto para garantir que caiba
            nome_conquista = conquista['nome']
            if len(nome_conquista) > 15:  # Se o nome for muito longo
                texto_conquista = f"{nome_conquista[:15]}... ({conquista['atual']}/{conquista['meta']})"
            else:
                texto_conquista = f"{nome_conquista} ({conquista['atual']}/{conquista['meta']})"
            
            # Cor do texto varia com o progresso
            if conquista['progresso'] >= 0.75:  # Próximo de completar
                cor_texto = (255, 255, 150)  # Amarelo claro
            else:
                cor_texto = (255, 255, 255)  # Branco
                
            texto_surface = fonte_conquista.render(texto_conquista, True, cor_texto)
            texto_rect = texto_surface.get_rect(midleft=(x_barra + resize(10, eh_X=True), indicador_rect.centery))
            self.tela.blit(texto_surface, texto_rect)
            
            # Desenha a porcentagem no final da barra
            porcentagem = f"{int(conquista['progresso']*100)}%"
            fonte_percent = pygame.font.SysFont("Arial", resize(16, eh_X=True), bold=True)
            percent_surf = fonte_percent.render(porcentagem, True, (255, 255, 255))
            percent_rect = percent_surf.get_rect(midright=(x_barra + largura_barra - resize(10, eh_X=True), 
                                                         indicador_rect.centery))
            
            # Garante que a porcentagem não sobreponha o título da conquista
            if percent_rect.left < texto_rect.right + resize(10, eh_X=True):
                percent_rect.left = texto_rect.right + resize(10, eh_X=True)
                
            self.tela.blit(percent_surf, percent_rect)
            
            # Adiciona brilho aos indicadores próximos de completar
            if conquista['progresso'] >= 0.9:  # Muito próximo de completar
                tempo = time.time()
                # Efeito de brilho pulsante
                intensidade = (math.sin(tempo * 4) + 1) / 2  # Varia de 0 a 1
                brilho_cor = (255, 255, 100, int(80 * intensidade))
                
                # Borda brilhante
                pygame.draw.rect(self.tela, brilho_cor, indicador_rect, 
                                width=resize(2), border_radius=resize(10))

    def desenhar_forma_coracao(self, superficie, area_retangulo, cor):
        """Desenha uma forma de coração na superfície fornecida dentro da area_retangulo."""
        largura_rect, altura_rect = area_retangulo.width, area_retangulo.height
        
        # Parâmetros para a forma do coração
        # Novo raio para garantir sobreposição e um visual mais "cheio"
        raio_circulo = largura_rect * 0.3  


        centro_x_circulo_esquerdo = raio_circulo
        centro_x_circulo_direito = largura_rect - raio_circulo 
        
        # Coordenada Y para o centro dos círculos
        centro_y_circulo = raio_circulo + (altura_rect * 0.08)

        # Ponta inferior do coração
        ponta_y = altura_rect * 0.90 # Posição Y da ponta inferior
        ponta_x = largura_rect / 2.0
        ponto_ponta = (int(ponta_x), int(ponta_y))

        # Ângulo para os pontos de conexão do polígono nos círculos
        # math.pi / 4 (45 graus) para um bom ponto de tangência
        angulo_conexao = math.pi / 4 

        cos_angulo = math.cos(angulo_conexao)
        sin_angulo = math.sin(angulo_conexao)

        # Ponto de conexão esquerdo (no círculo esquerdo)
        conexao_x_esquerdo = centro_x_circulo_esquerdo - 0.95*raio_circulo * cos_angulo
        conexao_y_esquerdo = centro_y_circulo + raio_circulo * sin_angulo
        ponto_conexao_esquerdo = (int(conexao_x_esquerdo), int(conexao_y_esquerdo))

        # Ponto de conexão direito (no círculo direito)
        conexao_x_direito = centro_x_circulo_direito + 0.95*raio_circulo * cos_angulo
        conexao_y_direito = centro_y_circulo + raio_circulo * sin_angulo
        ponto_conexao_direito = (int(conexao_x_direito), int(conexao_y_direito))
        
        # Pontos do polígono para a base em V do coração
        pontos_poligono = [
            ponto_conexao_esquerdo,
            ponto_ponta,
            ponto_conexao_direito
        ]
        
        # Desenha o polígono (base em V) primeiro
        pygame.draw.polygon(superficie, cor, pontos_poligono)

        # Desenha os dois círculos para a parte superior.
        # Eles irão sobrepor o polígono e criar a forma arredondada superior do coração.
        pygame.draw.circle(superficie, cor, (int(centro_x_circulo_esquerdo), int(centro_y_circulo)), int(raio_circulo))
        pygame.draw.circle(superficie, cor, (int(centro_x_circulo_direito), int(centro_y_circulo)), int(raio_circulo))

    def desenhar_efeito_corte(self, superficie, area_retangulo, progresso):
        """Desenha um efeito de corte diagonal na superficie."""
        if progresso <= 0 or progresso >= 1:
            return

        largura_rect, altura_rect = area_retangulo.width, area_retangulo.height
        cor_linha = (255, 255, 255, 200) # Branco, semi-transparente
        espessura_linha = resize(5) # Aumentada para corações maiores

        # Linha diagonal do canto superior direito ao inferior esquerdo, comprimento baseado no progresso
        x1, y1 = largura_rect, 0  # Começa do canto superior direito da área do coração
        
        # Ponto final alvo para o corte completo (canto inferior esquerdo)
        x_alvo2, y_alvo2 = 0, altura_rect
        
        # Interpola o ponto final atual da linha
        x_atual2 = x1 + (x_alvo2 - x1) * progresso
        y_atual2 = y1 + (y_alvo2 - y1) * progresso
        
        pygame.draw.line(superficie, cor_linha, (x1, y1), (int(x_atual2), int(y_atual2)), espessura_linha)

        # Efeito de brilho para a linha de corte
        for i in range(1, 3):
            alfa_brilho = 150 - i * 40
            cor_brilho = (255, 255, 255, alfa_brilho)
            pygame.draw.line(superficie, cor_brilho, (x1, y1), (int(x_atual2), int(y_atual2)), espessura_linha + i * resize(2)) # Aumentado brilho


    def desenhar_coracoes(self):
        """Desenha os três corações representando as vidas."""
        numero_coracoes = 3
        largura_total_coracoes = numero_coracoes * self.tamanho_coracao + (numero_coracoes - 1) * self.espacamento_coracoes
        x_inicial = (LARGURA_TELA - largura_total_coracoes) / 2
        
        # Ajusta y_retangulo para centralizar verticalmente os corações maiores
        y_retangulo = self.posicao_y_coracoes - self.tamanho_coracao / 2


        for i in range(numero_coracoes):
            x_coracao = x_inicial + i * (self.tamanho_coracao + self.espacamento_coracoes)
            area_retangulo = pygame.Rect(x_coracao, y_retangulo, self.tamanho_coracao, self.tamanho_coracao)
            
            # Cria uma superfície temporária para cada coração para lidar com animação e transparência
            superficie_coracao = pygame.Surface((self.tamanho_coracao, self.tamanho_coracao), pygame.SRCALPHA)
            superficie_coracao.fill((0,0,0,0)) # Fundo transparente

            progresso_animacao = self.progresso_animacao_coracoes[i]

            if self.estados_coracoes[i]: # Coração está ativo ou sendo perdido
                if progresso_animacao > 0: # Animando perda
                    # Interpola cor de vermelho para cinza
                    fator = min(progresso_animacao, 1.0)
                    r = int(255 * (1 - fator) + 100 * fator)
                    g = int(0 * (1 - fator) + 100 * fator)
                    b = int(0 * (1 - fator) + 100 * fator)
                    cor_atual = (r, g, b)
                    
                    self.desenhar_forma_coracao(superficie_coracao, superficie_coracao.get_rect(), cor_atual)
                    self.desenhar_efeito_corte(superficie_coracao, superficie_coracao.get_rect(), progresso_animacao)
                    
                    # Atualiza progresso da animação
                    self.progresso_animacao_coracoes[i] += (1.0 / (self.duracao_animacao_coracoes * FPS))
                    if self.progresso_animacao_coracoes[i] >= 1.0:
                        self.progresso_animacao_coracoes[i] = 1.0 # Limita em 1
                        self.estados_coracoes[i] = False # Marca como perdido
                else: # Coração totalmente ativo
                    cor_atual = (255, 0, 0) # Vermelho
                    self.desenhar_forma_coracao(superficie_coracao, superficie_coracao.get_rect(), cor_atual)
            else: # Coração está perdido (e animação finalizada)
                cor_atual = (100, 100, 100) # Cinza
                self.desenhar_forma_coracao(superficie_coracao, superficie_coracao.get_rect(), cor_atual)

            self.tela.blit(superficie_coracao, area_retangulo.topleft)

    def desenhar_efeito_colisao(self):
        """Desenha o efeito de flash quando ocorre uma colisão"""
        if not self.flash_ativo:
            return
            
        tempo_atual = time.time()
        tempo_passado = tempo_atual - self.flash_inicio
        
        if tempo_passado > self.flash_duracao:
            self.flash_ativo = False
            return
            
        opacidade = int(255 * (1 - tempo_passado / self.flash_duracao))
        cor_flash = (self.flash_cor[0], self.flash_cor[1], self.flash_cor[2], opacidade)
        
        flash_surface = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        flash_surface.fill(cor_flash)
        
        self.tela.blit(flash_surface, (0, 0))

    def desenhar_controle_audio(self):
        """Desenha o botão de controle de áudio (mute/unmute)"""
        import constants
        
        x = resize(20, eh_X=True)
        y = resize(20)
        tamanho = resize(40)
        
        # Rect para detectar clique
        rect_audio = pygame.Rect(x, y, tamanho, tamanho)
        
        if constants.SOM_LIGADO:
            icone = self.icone_som_ligado
        else:
            icone = self.icone_som_desligado
        
        self.tela.blit(icone, rect_audio)
        
        pos_mouse = pygame.mouse.get_pos()
        if rect_audio.collidepoint(pos_mouse):
            pygame.draw.rect(self.tela, (255, 255, 255), rect_audio, width=1, border_radius=resize(5))
            
 
            for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if event.button == 1 and rect_audio.collidepoint(event.pos):  
                    constants.SOM_LIGADO = not constants.SOM_LIGADO
                    from utils.audio_manager import audio_manager
                    audio_manager.som_ligado = constants.SOM_LIGADO
   

                    if constants.SOM_LIGADO:
                        audio_manager.play_sound("hover")
        
        return rect_audio

    def loop_principal(self, pular_dialogo=False):
        """Loop principal do jogo."""
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.NOFRAME)
        info_x = resize(20, eh_X=True)
        info_y = resize(100)

        TransitionEffect.fade_in(tela, velocidade=8)
        

        nome_cena = f"fase_{self.nivel_atual}"
        if not pular_dialogo:

            self.gerenciador_dialogos.executar(nome_cena)
            from utils.user_data import marcar_dialogo_como_visto
            marcar_dialogo_como_visto(self.usuario, nome_cena)
        
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

                        TransitionEffect.fade_out(tela, velocidade=8)
                        return

            self.atualizar_labirinto()

            # Renderiza o fundo apropriado para o nível atual
            background_atual = self.background_images.get(self.nivel_atual)
            
            if background_atual:
                # Usa a imagem de fundo específica do nível atual
                self.tela.blit(background_atual, (0, 0))
            elif dialogo_dentro_img:
                # Fallback para a imagem de diálogo genérica se disponível
                self.tela.blit(dialogo_dentro_img, (0, 0))
            else:
                # Último fallback para cor sólida
                self.tela.fill(AZUL_CLARO)
                

            self.desenhar_elementos_tematicos()
                

            self.desenhar_nome_nivel()


            clicou_voltar, _ = desenhar_botao(
                texto="VOLTAR",
                x=LARGURA_TELA//2-resize(100, eh_X=True),
                y=ALTURA_TELA-resize(100),
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
                from utils.audio_manager import audio_manager
                audio_manager.stop_voiced_dialogue();

                TransitionEffect.fade_out(tela, velocidade=8)
                return


            if self.vidas <= 0:
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)

                TransitionEffect.fade_out(tela, velocidade=10)
                self.jogo_ativo, pular_dialogo = tela_falhou(tela, self.sistema_conquistas)
                
                if self.jogo_ativo:
                    self.resetar_nivel()

                    return self.loop_principal(pular_dialogo=pular_dialogo)

            if self.verifica_conclusao_nivel():
                tempo_total = time.time() - self.inicio_tempo
                    
                if self.nivel_atual >= 8:
                    TransitionEffect.fade_out(tela, velocidade=10)
                    self.gerenciador_dialogos.executar("vitoria", efeito_sonoro="success")
                    self.salvar_progresso(tempo_total)
                    self.sistema_conquistas.salvar_conquistas_usuario(self.usuario)
                    tela_conclusao(tela, self.sistema_conquistas)
                    self.resetar_nivel() # Reseta corações
                    return
                else:
                    self.salvar_progresso(tempo_total)
                    self.sistema_conquistas.salvar_conquistas_usuario(self.usuario)
                    proximo_nivel = self.nivel_atual + 1
                    

                    TransitionEffect.fade_out(tela, velocidade=10)

                    continuar_jogando, repetir_nivel, pular_dialogo = tela_conclusao_nivel(tela, self.nivel_atual, tempo_total, self.sistema_conquistas)
                    
                    if not continuar_jogando:

                        self.jogo_ativo = False
                        return
                    
                    self.nivel_atual = self.nivel_atual if repetir_nivel else proximo_nivel
                    
 
                    self.resetar_nivel() # Reseta corações
                    
   
                    return self.loop_principal(pular_dialogo=pular_dialogo)


            desenhar_texto(f"Usuário: {self.usuario}", self.fonte, COR_TEXTO, self.tela, info_x, info_y)
            desenhar_texto(f"Nível: {self.nivel_atual}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + resize(60))
            self.desenhar_coracoes()
            
            tempo_atual = time.time() - self.inicio_tempo
            self.desenhar_timer_visual(tempo_atual)

            self.desenhar_melhor_tempo()
            
            self.desenhar_indicadores_conquistas()
            
            self.desenhar_controle_audio()
            
            self.desenhar_efeito_colisao()
            
            self.sistema_conquistas.desenhar_notificacao(self.tela)
            
            import constants
            if constants.ESCALA_CINZA:
                aplicar_filtro_cinza_superficie(tela)
                
            pygame.display.update()