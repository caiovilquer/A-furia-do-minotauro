import pygame
import sys
import os
import time
import random
import math
from datetime import datetime
from constants import (
    BUTTON_PATH, FONTE_BOTAO, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
    FONTE_TEXTO, COR_TEXTO, PORTA_SELECIONADA, SOUND_PATH, dialogo_dentro_img,
    NUM_VIDAS, MODO_PRATICA, SERVO_VELOCIDADE, DEBOUNCE_COLISAO_MS, FEEDBACK_CANAL,
    FEEDBACK_INTENSIDADE, REDUZIR_FLASHES, QUICK_TIME_EVENTS, ESCALA_CINZA, SOM_LIGADO, DIALOGO_VELOCIDADE,
    QTE_CHANCE, QTE_TIMEOUT, QTE_SEQ_MIN, QTE_SEQ_MAX, QTE_INTERVALO_MIN
)
from utils.drawing import aplicar_filtro_cinza_superficie, desenhar_texto, desenhar_botao, resize, TransitionEffect
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios, get_acessibilidade
from screens.game_over import tela_falhou
from screens.level_complete import tela_conclusao_nivel
from screens.game_complete import tela_conclusao
from utils.dialog_manager import GerenciadorDialogos
from utils.achievements import SistemaConquistas
from utils.qte_manager import QTEManager

class JogoLabirinto:
    """Classe principal do jogo que gerencia o estado e a lógica do jogo."""
    
    def __init__(self, tela, usuario, nivel_inicial=None, sistema_conquistas=None, conexao_serial=None):
        self.tela = tela
        self.usuario = usuario
        self.clock = pygame.time.Clock()
        self.fonte = FONTE_TEXTO
        self.conexao_serial = conexao_serial
        
        # Carregar opções de acessibilidade do usuário
        self.usuarios_data = carregar_usuarios()
        self.opcoes = get_acessibilidade(usuario, self.usuarios_data)
        self.aplicar_opcoes_acessibilidade()
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
        self.som_ligado = self.opcoes.get("SOM_LIGADO", True)
        self.carregar_icones_audio()
        
        if sistema_conquistas:
            self.sistema_conquistas = sistema_conquistas
        else:
            self.sistema_conquistas = SistemaConquistas()
        self.sistema_conquistas.carregar_conquistas_usuario(usuario)
        self.colisoes = 0 

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

        # Vidas e corações - usar número dinâmico baseado nas opções do usuário
        self.vidas = self.num_vidas
        self.tamanho_coracao = resize(150)
        self.posicao_y_coracoes = resize(320) 
        self.espacamento_coracoes = resize(25) 
        # Criar array de estados com tamanho igual ao número de vidas
        self.estados_coracoes = [True] * self.num_vidas
        # Array de progresso de animação para cada coração
        self.progresso_animacao_coracoes = [0.0] * self.num_vidas 
        self.duracao_animacao_coracoes = 0.5

        #self.inicio_tempo = time.time()
        self.inicio_tempo = 0 
        self.jogo_ativo = True

        self.esperando_inicio = True if self.conexao_serial else False # Flag para aguardar o sinal do sensor de início
        self.nivel_concluido_hardware = False # Flag para sinal de conclusão do Arduino
        
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
            
        # Para sistema de QTE
        self.qte_manager = QTEManager(QTE_TIMEOUT, QTE_SEQ_MIN, QTE_SEQ_MAX)
        # Inicializa o último QTE para evitar que apareça imediatamente no início do jogo
        self.ultimo_qte = time.time()  # Alterado: Não subtrai o intervalo mínimo
        self.qte_ativado = False
        self.qte_stats = {"qte_sucesso": 0, "qte_falhas": 0}
        self.servo_congelado = False
        self.tempo_servo_congelado = 0
        self.proximo_check_qte = time.time() + QTE_INTERVALO_MIN  # Tempo para o próximo sorteio de QTE
        
        self.qte_input_queue = [] # Fila para os inputs do QTE vindos do Arduino
        # Popup de Power-up QTE
        self.popup_powerup_ativo = False
        self.popup_powerup_titulo = ""
        self.popup_powerup_descricao = ""
        self.popup_powerup_icone_atual = None
        self.popup_powerup_inicio_tempo = 0
        self.popup_powerup_duracao = 3.0  # Segundos
        self.popup_powerup_fade_duracao = 0.5 # Segundos para fade in/out
        self.carregar_icones_powerup()
        
    def aplicar_opcoes_acessibilidade(self):
        # Número de vidas
        self.num_vidas = self.opcoes.get("NUM_VIDAS", NUM_VIDAS)
        # Modo prática
        self.modo_pratica = self.opcoes.get("MODO_PRATICA", MODO_PRATICA)
        # Debounce colisão
        self.debounce_colisao_ms = self.opcoes.get("DEBOUNCE_COLISAO_MS", DEBOUNCE_COLISAO_MS)
        # Feedback
        self.feedback_canal = self.opcoes.get("FEEDBACK_CANAL", FEEDBACK_CANAL)
        self.feedback_intensidade = self.opcoes.get("FEEDBACK_INTENSIDADE", FEEDBACK_INTENSIDADE)
        # Servo velocidade
        self.servo_velocidade = self.opcoes.get("SERVO_VELOCIDADE", SERVO_VELOCIDADE)
        # Quick time events
        self.quick_time_events = self.opcoes.get("QUICK_TIME_EVENTS", QUICK_TIME_EVENTS)
        # Reduzir flashes
        self.reduzir_flashes = self.opcoes.get("REDUZIR_FLASHES", REDUZIR_FLASHES)
        # Escala de cinza
        self.escala_cinza = self.opcoes.get("ESCALA_CINZA", ESCALA_CINZA)
        # Som ligado
        self.som_ligado = self.opcoes.get("SOM_LIGADO", SOM_LIGADO)
        # Velocidade do diálogo
        self.dialogo_velocidade = self.opcoes.get("DIALOGO_VELOCIDADE", DIALOGO_VELOCIDADE)

        # Aplicar configurações globais
        import constants
        constants.ESCALA_CINZA = self.escala_cinza
        constants.SOM_LIGADO = self.som_ligado


        # Aplicar som ligado/desligado no audio_manager
        from utils.audio_manager import audio_manager
        audio_manager.som_ligado = self.som_ligado
        audio_manager.set_music_volume(max(self.opcoes.get("VOLUME_MUSICA", 0.1)*0.1, 0.02))
        audio_manager.set_sfx_volume(self.opcoes.get("VOLUME_SFX", 0.7))
        audio_manager.set_voice_volume(self.opcoes.get("VOLUME_VOZ", 0.8))

        # Ajustar duração do flash
        self.flash_duracao = 0 if self.reduzir_flashes else 0.3

        # Enviar velocidade do servo para Arduino se necessário
        if self.conexao_serial:
            try:
                # Envia todas as configurações de uma vez
                self.conexao_serial.write(f"SERVO:{self.servo_velocidade}\n".encode())
                self.conexao_serial.write(f"DEBOUNCE:{self.debounce_colisao_ms}\n".encode())
                self.conexao_serial.write(f"FEEDBACK:{self.feedback_canal}\n".encode())
            except Exception as e:
                print(f"Erro ao enviar configurações para o Arduino: {e}")

    def carregar_icones_powerup(self):
        """Carrega os ícones para os power-ups."""
        icon_size = resize(64)
        try:
            self.icone_powerup_vida = pygame.image.load("Labirinto_game/assets/images/icons/powerup_vida.png").convert_alpha()
            self.icone_powerup_vida = pygame.transform.scale(self.icone_powerup_vida, (icon_size, icon_size))
        except Exception as e:
            print(f"Erro ao carregar icone_powerup_vida: {e}")
            self.icone_powerup_vida = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(self.icone_powerup_vida, (255,0,0), (icon_size//2, icon_size//2), icon_size//2 - 2)
            desenhar_texto("+", pygame.font.SysFont("Arial", resize(40), bold=True), (255,255,255), self.icone_powerup_vida, icon_size//2, icon_size//2, center=True)


        try:
            self.icone_powerup_congelar = pygame.image.load("Labirinto_game/assets/images/icons/powerup_freeze.png").convert_alpha()
            self.icone_powerup_congelar = pygame.transform.scale(self.icone_powerup_congelar, (icon_size, icon_size))
        except Exception as e:
            print(f"Erro ao carregar icone_powerup_congelar: {e}")
            self.icone_powerup_congelar = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.rect(self.icone_powerup_congelar, (0,200,255), (0,0,icon_size,icon_size), border_radius=5)
            desenhar_texto("❄", pygame.font.SysFont("Arial", resize(40), bold=True), (255,255,255), self.icone_powerup_congelar, icon_size//2, icon_size//2, center=True)

        try:
            self.icone_powerup_tempo = pygame.image.load("Labirinto_game/assets/images/icons/powerup_time.png").convert_alpha()
            self.icone_powerup_tempo = pygame.transform.scale(self.icone_powerup_tempo, (icon_size, icon_size))
        except Exception as e:
            print(f"Erro ao carregar icone_powerup_tempo: {e}")
            self.icone_powerup_tempo = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
            pygame.draw.circle(self.icone_powerup_tempo, (255,215,0), (icon_size//2, icon_size//2), icon_size//2 - 2)
            desenhar_texto("⏱", pygame.font.SysFont("Arial", resize(35), bold=True), (0,0,0), self.icone_powerup_tempo, icon_size//2, icon_size//2, center=True)


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
        
        # Verificar progresso para "Mestre dos Botões"
        if not self.sistema_conquistas.conquistas['mestre_dos_botoes']['desbloqueada']:
            qtes_acertados = self.usuarios_data.get(self.usuario, {}).get("qtes_acertados", 0)
            meta_qte = 10  # Meta para desbloquear a conquista
            
            if qtes_acertados > 0:  # Se já tem pelo menos 1 QTE acertado
                conquistas_proximas.append({
                    'chave': 'mestre_dos_botoes',
                    'nome': self.sistema_conquistas.conquistas.get('mestre_dos_botoes', {}).get('nome', 'Mestre dos Botões'),
                    'progresso': min(1.0, qtes_acertados / meta_qte),
                    'meta': meta_qte,
                    'atual': qtes_acertados
                })

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
            if len(niveis_completados) >= 3:
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
        # Verificar e atualizar estado do servo congelado
        if self.servo_congelado and time.time() > self.tempo_servo_congelado:
            self.servo_congelado = False
            if self.conexao_serial:
                try:
                    self.conexao_serial.write(b"FREEZE:0\n") # Envia o comando para descongelar
                    print("Comando para descongelar servos enviado.")
                except Exception as e:
                    print(f"Erro ao desativar congelamento: {e}")
        
        # Atualizar QTE
        self.qte_manager.atualizar(1/FPS)
        
        # Se o QTE foi concluído (sucesso ou falha), resetar
        if self.qte_manager.concluido:
            # Se foi bem-sucedido, aplicar power-up
            if self.qte_manager.sucesso:
                self.qte_concluido_sucesso()
            self.qte_manager.resetar()
        
        # Verificar se deve iniciar um novo QTE - apenas uma vez por intervalo
        tempo_atual = time.time()
        
        # Realiza o sorteio apenas quando chegar o momento do próximo check
        if (self.quick_time_events and           # Se QTEs estão ativados nas configurações
            not self.qte_manager.ativo and       # Se não há QTE em andamento
            tempo_atual >= self.proximo_check_qte and
            not self.esperando_inicio):  # Se chegou o momento do próximo check
            
            # Faz um único sorteio por intervalo
            chance_atual = random.random() 
            print(f"Check de QTE: {chance_atual:.4f} (limite: {QTE_CHANCE})")
            
            if chance_atual < QTE_CHANCE:
                self.qte_input_queue.clear()
                sequencia_qte = self.qte_manager.iniciar()
                self.ultimo_qte = tempo_atual

                if self.conexao_serial and sequencia_qte:
                    try:
                        # Envia o comando para mostrar apenas a PRIMEIRA luz da sequência
                        primeiro_passo = sequencia_qte[0]
                        comando_qte = f"QTE_SHOW:{primeiro_passo}\n"
                        self.conexao_serial.write(comando_qte.encode('utf-8'))
                    except Exception as e:
                        print(f"Erro ao iniciar sequência de QTE: {e}")
            
            # Independente do resultado, agenda o próximo check para daqui a QTE_INTERVALO_MIN segundos
            self.proximo_check_qte = tempo_atual + QTE_INTERVALO_MIN
        
        if self.conexao_serial:
            self.ler_dados_serial()
        else:
            # Simulação quando não há comunicação com Arduino
            self.simular_progresso()
            
            # Simular botões para QTE em modo de simulação
            if self.qte_manager.ativo and not self.qte_manager.concluido and random.random() < 0.05:
                # 50% de chance de acertar o input correto
                if random.random() < 0.5:
                    input_correto = self.qte_manager.sequencia[self.qte_manager.passo_atual]
                    resultado = self.qte_manager.processar_input(input_correto)
                    if resultado is True:
                        self.qte_concluido_sucesso()
                else:
                    input_errado = "B" if self.qte_manager.sequencia[self.qte_manager.passo_atual] == "C" else "C"
                    self.qte_manager.processar_input(input_errado)
                    self.qte_stats["qte_falhas"] += 1

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
        print(f"Dados recebidos do Arduino: {dados}")
        try:
            # Sinal de que o jogador está no sensor de início
            if dados == "PLAYER_AT_START":
                if self.esperando_inicio:
                    tempo_atual = time.time()
                    self.inicio_tempo = tempo_atual  # Inicia o cronômetro do jogo
                    self.ultimo_qte = tempo_atual  # Inicia o contador de QTE
                    self.proximo_check_qte = tempo_atual + QTE_INTERVALO_MIN  # Agenda primeiro QTE
                    self.esperando_inicio = False
                    print("Cronômetro e timer de QTE iniciados pelo hardware!")

            # Sinal de colisão
            elif dados == "COLLISION":
                if not self.esperando_inicio: # Ignora colisões antes do início
                    self.vidas -= 1
                    self.colisoes += 1
                    self.feedback_colisao() # Chama a função de feedback existente

            # Sinal de que o jogador chegou ao sensor de fim
            elif dados == "LEVEL_COMPLETE":
                self.nivel_concluido_hardware = True

            if dados == "BTN_C":
                self.qte_input_queue.append('C')
            elif dados == "BTN_B":
                self.qte_input_queue.append('B')

        except Exception as e:
            print(f"Erro ao processar dados do Arduino: {e}")
    
    def qte_concluido_sucesso(self):
        """Aplica power-up aleatório quando um QTE é concluído com sucesso"""
        from utils.audio_manager import audio_manager
        
        # Incrementar contagem de QTEs bem-sucedidos
        self.qte_stats["qte_sucesso"] += 1
        print(f"QTE concluído com sucesso! Total: {self.qte_stats['qte_sucesso']}")
        
        if self.vidas < self.num_vidas:
            power_up = random.choice(["vida_extra", "congelar_servos", "reduzir_tempo"])
        else:
            power_up = random.choice(["congelar_servos", "reduzir_tempo"])
        
        self.popup_powerup_titulo = "RECOMPENSA!"
        self.popup_powerup_ativo = True
        self.popup_powerup_inicio_tempo = time.time()

        if power_up == "vida_extra" and self.vidas < self.num_vidas:
            self.vidas += 1
            print(f"Power-up: Vida extra! Vidas: {self.vidas}")
            # Atualiza estados dos corações
            indice_coracao_recuperado = self.vidas - 1
            if 0 <= indice_coracao_recuperado < self.num_vidas:
                self.estados_coracoes[indice_coracao_recuperado] = True
                self.progresso_animacao_coracoes[indice_coracao_recuperado] = 0.0
            audio_manager.play_sound("powerup")
            audio_manager.play_voiced_dialogue("vida_extra")
            self.popup_powerup_descricao = "Vida Extra!"
            self.popup_powerup_icone_atual = self.icone_powerup_vida
            
        elif power_up == "congelar_servos":
            # Congelar servos por 5 segundos
            self.servo_congelado = True
            self.tempo_servo_congelado = time.time() + 5.0  # 5 segundos
            print(f"Power-up: Servos congelados por 5 segundos!")
            if self.conexao_serial:
                try:
                    self.conexao_serial.write(b"FREEZE:1\n")
                except Exception as e:
                    print(f"Erro ao enviar comando de congelamento: {e}")
            audio_manager.play_sound("powerup")
            audio_manager.play_voiced_dialogue("servos_congelados")
            self.popup_powerup_descricao = "Servos Congelados!"
            self.popup_powerup_icone_atual = self.icone_powerup_congelar
            
        elif power_up == "reduzir_tempo":
            # Reduzir 10 segundos do tempo
            self.inicio_tempo += 10.0  # Adicionar 10 segundos ao início (reduz o tempo decorrido)
            tempo_atual = time.time() - self.inicio_tempo
            print(f"Power-up: Tempo reduzido em 10 segundos! Novo tempo: {tempo_atual:.1f}s")
            audio_manager.play_sound("powerup")
            audio_manager.play_voiced_dialogue("tempo_reduzido")
            self.popup_powerup_descricao = "Tempo Reduzido!"
            self.popup_powerup_icone_atual = self.icone_powerup_tempo
            
    def feedback_colisao(self):
        """Fornece feedback visual/sonoro para colisão."""
        from utils.audio_manager import audio_manager
        
        audio_manager.play_sound("collision")
        
        # Escolhe o áudio dublado correto baseado no número de vidas restantes
        if self.vidas == 1: # Será 1 após esta colisão se era 2 antes
            audio_manager.play_voiced_dialogue("colisao_1vida")
        elif self.vidas == 2: # Será 2 após esta colisão se era 3 antes
            audio_manager.play_voiced_dialogue("colisao_2vidas")
        
        self.flash_ativo = True
        self.flash_inicio = time.time()

        indice_coracao_perdido = self.vidas 
        if 0 <= indice_coracao_perdido < self.num_vidas and self.estados_coracoes[indice_coracao_perdido]:
            # Inicia a animação apenas se não já iniciada
            if self.progresso_animacao_coracoes[indice_coracao_perdido] == 0.0: 
                self.progresso_animacao_coracoes[indice_coracao_perdido] = 0.01
        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        """Verifica se o nível foi concluído, agora baseado no sinal do hardware."""
        if self.conexao_serial:
            return self.nivel_concluido_hardware
        else:
            return (time.time() - self.inicio_tempo) > 10 if self.inicio_tempo > 0 else False
    
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
            'vidas_iniciais': self.num_vidas,  # Usar o número de vidas configurado
            'concluido': not falhou,
            'qte_sucesso': self.qte_stats.get("qte_sucesso", 0),
            'qtes_acertados': usuario_data.get('qtes_acertados', 0)  # Adiciona contagem total de QTEs acertados
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
        self.vidas = self.num_vidas
        # Usar número dinâmico de corações
        self.estados_coracoes = [True] * self.num_vidas
        self.progresso_animacao_coracoes = [0.0] * self.num_vidas
        # Recarga explícita das conquistas para garantir estado atualizado
        self.sistema_conquistas.limpar_notificacoes()
        self.sistema_conquistas.carregar_conquistas_usuario(self.usuario)
        self.usuarios_data = carregar_usuarios()
        self.opcoes = get_acessibilidade(self.usuario, self.usuarios_data)
        self.aplicar_opcoes_acessibilidade()
        self.vidas = self.num_vidas
        self.estados_coracoes = [True] * self.num_vidas + [False] * (5 - self.num_vidas)
        self.estados_coracoes = self.estados_coracoes[:5]
        self.progresso_animacao_coracoes = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.progresso = 0.0
        self.mostrou_dialogo_fase_atual = False
        
        # Reset QTE timer when starting a new level
        # self.ultimo_qte = time.time()
        # self.proximo_check_qte = time.time() + QTE_INTERVALO_MIN  # Agenda o primeiro check
        self.qte_manager.resetar()
        self.popup_powerup_ativo = False # Garante que o popup não persista entre níveis
        
        # Obter melhor tempo do jogador para este nível
        self.melhor_tempo = self.obter_melhor_tempo()
        
        self.conquistas_proximas = self.verificar_conquistas_proximas()

        self.esperando_inicio = True if self.conexao_serial else False # Flag para aguardar o sinal do sensor de início
        self.nivel_concluido_hardware = False # Flag para sinal de conclusão do Arduino
        
        if self.conexao_serial:
            self.enviar_nivel_arduino()
            
        print(f"Estado do jogo resetado.")

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

    def desenhar_popup_powerup(self):
        if not self.popup_powerup_ativo:
            return

        tempo_decorrido = time.time() - self.popup_powerup_inicio_tempo
        
        if tempo_decorrido > self.popup_powerup_duracao:
            self.popup_powerup_ativo = False
            return

        # Cálculo de Alpha para fade-in e fade-out
        alpha = 255
        if tempo_decorrido < self.popup_powerup_fade_duracao: # Fade-in
            alpha = int(255 * (tempo_decorrido / self.popup_powerup_fade_duracao))
        elif tempo_decorrido > self.popup_powerup_duracao - self.popup_powerup_fade_duracao: # Fade-out
            alpha = int(255 * ((self.popup_powerup_duracao - tempo_decorrido) / self.popup_powerup_fade_duracao))
        alpha = max(0, min(255, alpha)) # Garante que alpha esteja entre 0 e 255

        if alpha == 0: # Se invisível, não desenha
            return

        # Dimensões e Posição do Popup
        popup_largura = resize(450, eh_X=True)
        popup_altura = resize(130)
        popup_x = (LARGURA_TELA - popup_largura) // 2
        popup_y = ALTURA_TELA // 2 - popup_altura - resize(50) # Um pouco acima do centro

        # Superfície do Popup com transparência
        popup_surface = pygame.Surface((popup_largura, popup_altura), pygame.SRCALPHA)
        
        # Fundo estilizado (ex: gradiente ou cor sólida com borda)
        cor_fundo_base = (30, 30, 70) # Azul escuro
        pygame.draw.rect(popup_surface, (*cor_fundo_base, int(alpha * 0.9)), (0,0, popup_largura, popup_altura), border_radius=resize(20))
        
        # Borda Dourada
        cor_borda = (255, 215, 0)
        pygame.draw.rect(popup_surface, (*cor_borda, alpha), (0,0, popup_largura, popup_altura), width=resize(3), border_radius=resize(20))

        # Desenhar Ícone
        if self.popup_powerup_icone_atual:
            icone_rect = self.popup_powerup_icone_atual.get_rect(centery=popup_altura//2, left=resize(20, eh_X=True))
            # Aplicar alpha ao ícone também
            temp_icon_surf = self.popup_powerup_icone_atual.copy()
            temp_icon_surf.set_alpha(alpha)
            popup_surface.blit(temp_icon_surf, icone_rect)
            texto_x_inicio = icone_rect.right + resize(20, eh_X=True)
        else:
            texto_x_inicio = resize(20, eh_X=True)

        # Título "RECOMPENSA!"
        fonte_titulo_popup = pygame.font.SysFont("Arial", resize(30, eh_X=True), bold=True)
        texto_titulo_surf = fonte_titulo_popup.render(self.popup_powerup_titulo, True, (*cor_borda, alpha))
        titulo_rect = texto_titulo_surf.get_rect(top=resize(15), centerx=popup_largura/2 + texto_x_inicio/3) # Ajustar centro
        if self.popup_powerup_icone_atual: # Centraliza melhor se houver ícone
             titulo_rect.left = texto_x_inicio
        else: # Centraliza no painel se não houver ícone
            titulo_rect.centerx = popup_largura / 2

        popup_surface.blit(texto_titulo_surf, titulo_rect)

        # Descrição do Power-up
        fonte_desc_popup = pygame.font.SysFont("Arial", resize(24, eh_X=True))
        texto_desc_surf = fonte_desc_popup.render(self.popup_powerup_descricao, True, (255, 255, 255, alpha))
        desc_rect = texto_desc_surf.get_rect(top=titulo_rect.bottom + resize(10))
        if self.popup_powerup_icone_atual:
            desc_rect.left = texto_x_inicio
        else:
            desc_rect.centerx = popup_largura / 2
        
        popup_surface.blit(texto_desc_surf, desc_rect)

        # Efeito de brilho sutil (opcional)
        if tempo_decorrido < self.popup_powerup_fade_duracao or tempo_decorrido > self.popup_powerup_duracao - self.popup_powerup_fade_duracao:
            brilho_alpha = int(alpha * 0.3 * (math.sin(tempo_decorrido * 10) * 0.5 + 0.5)) # Pulsante
            pygame.draw.rect(popup_surface, (255, 255, 200, brilho_alpha), (0,0, popup_largura, popup_altura), width=resize(5), border_radius=resize(20))


        self.tela.blit(popup_surface, (popup_x, popup_y))


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
        """Desenha os corações representando as vidas."""
        # Usar o número de vidas configurado pelo usuário
        numero_coracoes = self.num_vidas
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

    def desenhar_qte(self):
        """Desenha a interface do QTE atual"""
        if not self.qte_manager.ativo:
            return
            
        from utils.drawing import desenhar_barra_qte
        
        # Calcula posição central na tela
        centro_x = LARGURA_TELA // 2
        centro_y = ALTURA_TELA // 2 - resize(150)
        
        # Desenha um painel de fundo semitransparente
        painel_largura = resize(400, eh_X=True)
        painel_altura = resize(200)
        painel_x = centro_x - painel_largura // 2
        painel_y = centro_y - painel_altura // 2
        
        painel = pygame.Surface((painel_largura, painel_altura), pygame.SRCALPHA)
        painel.fill((0, 0, 0, 150))  # Fundo escuro semitransparente
        self.tela.blit(painel, (painel_x, painel_y))
        
        # Desenha borda dourada
        pygame.draw.rect(self.tela, (255, 215, 0), 
                        pygame.Rect(painel_x, painel_y, painel_largura, painel_altura),
                        width=resize(2), border_radius=resize(10))
        
        # Título do QTE
        fonte_titulo = pygame.font.SysFont("Arial", resize(32, eh_X=True), bold=True)
        texto_titulo = "Evento de Tempo Rápido!"
        surf_titulo = fonte_titulo.render(texto_titulo, True, (255, 215, 0))
        rect_titulo = surf_titulo.get_rect(center=(centro_x, painel_y + resize(30)))
        self.tela.blit(surf_titulo, rect_titulo)
        
        # Desenha a sequência de botões
        btn_y = painel_y + resize(80)
        btn_tamanho = resize(50)
        espacamento = resize(20, eh_X=True)
        
        # Calcula a posição inicial dos botões para centralizá-los
        total_largura = len(self.qte_manager.sequencia) * btn_tamanho + (len(self.qte_manager.sequencia) - 1) * espacamento
        btn_x_inicial = centro_x - total_largura // 2
        
        for i, comando in enumerate(self.qte_manager.sequencia):
            btn_x = btn_x_inicial + i * (btn_tamanho + espacamento)
            btn_rect = pygame.Rect(btn_x, btn_y, btn_tamanho, btn_tamanho)
            
            # Determina a cor do botão
            if i < self.qte_manager.passo_atual:  # Botões já pressionados corretamente
                cor_btn = (0, 200, 0)  # Verde
            elif i == self.qte_manager.passo_atual:  # Botão atual
                # Efeito pulsante para o botão atual
                pulso = (math.sin(time.time() * 5) + 1) / 2  # Varia de 0 a 1
                if comando == "C":
                    cor_btn = (0, 0 , 255)
                elif comando == "B":
                    cor_btn = (255, 0, 0)
                # Desenha efeito de pulso (círculo ao redor)
                pulso_tamanho = int(btn_tamanho * (1 + 0.2 * pulso))
                pulso_x = btn_x + btn_tamanho // 2 - pulso_tamanho // 2
                pulso_y = btn_y + btn_tamanho // 2 - pulso_tamanho // 2
                pygame.draw.circle(self.tela, (255, 215, 0, 100), 
                                 (btn_x + btn_tamanho // 2, btn_y + btn_tamanho // 2),
                                 pulso_tamanho // 2, width=resize(2))
            else:  # Botões futuros
                if comando == "C":
                    cor_btn = (0, 0, 100)
                elif comando == "B":
                    cor_btn = (100, 0, 0)

            
            # Desenha o botão
            pygame.draw.rect(self.tela, cor_btn, btn_rect, border_radius=resize(10))
            pygame.draw.rect(self.tela, (255, 255, 255), btn_rect, width=resize(2), border_radius=resize(10))
            
            # Desenha o texto do botão (L ou R)
            fonte_btn = pygame.font.SysFont("Arial", resize(24, eh_X=True), bold=True)
            texto_btn = fonte_btn.render(comando, True, (255, 255, 255))
            rect_texto = texto_btn.get_rect(center=btn_rect.center)
            self.tela.blit(texto_btn, rect_texto)
        
        # Desenha a barra de tempo
        barra_largura = resize(350, eh_X=True)
        barra_altura = resize(20)
        barra_x = centro_x - barra_largura // 2
        barra_y = painel_y + painel_altura - resize(40)
        
        # A cor da barra varia conforme o tempo restante
        tempo_pct = self.qte_manager.progresso_tempo()
        if tempo_pct > 0.66:
            cor_barra = (0, 200, 0)  # Verde
        elif tempo_pct > 0.33:
            cor_barra = (255, 215, 0)  # Amarelo
        else:
            cor_barra = (200, 0, 0)  # Vermelho
            
        desenhar_barra_qte(self.tela, barra_x, barra_y, barra_largura, barra_altura, tempo_pct, cor_barra)
        
    def loop_principal(self, pular_dialogo=False):
        """Loop principal do jogo."""
        tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA), pygame.NOFRAME)
        info_x = resize(20, eh_X=True)
        info_y = resize(100)
        
        nome_cena = f"fase_{self.nivel_atual}"
        if not pular_dialogo:

            self.gerenciador_dialogos.executar(nome_cena)
            from utils.user_data import marcar_dialogo_como_visto
            marcar_dialogo_como_visto(self.usuario, nome_cena)
        
     # Reinicia o timer após o diálogo (importante!) e também o timer do QTE
        # self.inicio_tempo = time.time()
        # self.ultimo_qte = time.time()  
        # self.proximo_check_qte = time.time() + QTE_INTERVALO_MIN  # Agenda primeiro check   
        
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
                    # Simular botões QTE com teclado (para testes)
                    elif event.key == pygame.K_LEFT and self.qte_manager.ativo and not self.qte_manager.concluido:
                        resultado = self.qte_manager.processar_input("C")
                    elif event.key == pygame.K_RIGHT and self.qte_manager.ativo and not self.qte_manager.concluido:
                        resultado = self.qte_manager.processar_input("B")

            if self.conexao_serial and self.qte_manager.ativo and self.qte_input_queue:
                # Pega o último botão pressionado que veio do Arduino
                input_do_jogador = self.qte_input_queue.pop(0) 
                
                # Valida o input
                resultado = self.qte_manager.processar_input(input_do_jogador)

                if resultado is None: # Acertou, mas a sequência não terminou
                    # Pisca o LED de acerto e mostra a próxima luz
                    self.conexao_serial.write(b"QTE_ACK\n")
                    time.sleep(0.08) # Pequena pausa para a piscada
                    proximo_passo = self.qte_manager.sequencia[self.qte_manager.passo_atual]
                    self.conexao_serial.write(f"QTE_SHOW:{proximo_passo}\n".encode('utf-8'))

                elif resultado is True: # Acertou o último passo
                    self.conexao_serial.write(b"QTE_END\n")
                    # Incrementa o contador de QTEs acertados no usuário
                    self.usuarios_data.setdefault(self.usuario, {}).setdefault("qtes_acertados", 0)
                    self.usuarios_data[self.usuario]["qtes_acertados"] += 1
                    salvar_usuarios(self.usuarios_data)
                    print(f"QTE acertado! Total: {self.usuarios_data[self.usuario]['qtes_acertados']}")
                    # A função qte_concluido_sucesso() será chamada pelo qte_manager
                    
                elif resultado is False: # Errou
                    self.conexao_serial.write(b"QTE_END\n")

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
                self.conexao_serial.write(b"TERMINAR\n")
                print("Jogo encerrado pelo usuário.")
                TransitionEffect.fade_out(tela, velocidade=8)
                return


            if self.vidas <= 0:
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)
                self.conexao_serial.write(b"LEVEL_FAILED\n")
                self.conexao_serial.write(b"TERMINAR\n")
                TransitionEffect.fade_out(tela, velocidade=10)
                self.jogo_ativo, pular_dialogo = tela_falhou(tela, self.sistema_conquistas)
                
                if self.jogo_ativo:
                    self.resetar_nivel()

                    return self.loop_principal(pular_dialogo=pular_dialogo)

            if self.verifica_conclusao_nivel():
                tempo_total = time.time() - self.inicio_tempo
                self.conexao_serial.write(b"TERMINAR\n")    
                if self.nivel_atual >= 8:
                    TransitionEffect.fade_out(tela, velocidade=10)
                    self.gerenciador_dialogos.executar("vitoria")
                    self.salvar_progresso(tempo_total)
                    self.sistema_conquistas.salvar_conquistas_usuario(self.usuario)
                    tela_conclusao(tela, self.sistema_conquistas)
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


            if self.esperando_inicio:
                fonte_aviso = pygame.font.SysFont("Arial", resize(50, eh_X=True), bold=True)
                desenhar_texto("Posicione o anel no início para começar!", fonte_aviso, 
                                     (255, 255, 100), self.tela, 
                                     LARGURA_TELA//2, ALTURA_TELA//2 - resize(300), centralizado=True)
            else:
                # O jogo está rolando, desenha a interface normal
                desenhar_texto(f"Usuário: {self.usuario}", self.fonte, COR_TEXTO, self.tela, info_x, info_y)
                desenhar_texto(f"Nível: {self.nivel_atual}", self.fonte, COR_TEXTO, self.tela, info_x, info_y + resize(60))
                self.desenhar_coracoes()

                # O cronômetro só é desenhado se já tiver iniciado
                if self.inicio_tempo > 0:
                    tempo_atual = time.time() - self.inicio_tempo
                    self.desenhar_timer_visual(tempo_atual)
                else:
                    self.desenhar_timer_visual(0) # Mostra timer em 0

            self.desenhar_qte()
            self.desenhar_popup_powerup() # Desenha o popup de power-up

            self.desenhar_melhor_tempo()
            
            self.desenhar_indicadores_conquistas()
            
            self.desenhar_controle_audio()
            
            self.desenhar_efeito_colisao()
            
            self.sistema_conquistas.desenhar_notificacao(self.tela)
            
            import constants
            if constants.ESCALA_CINZA:
                aplicar_filtro_cinza_superficie(self.tela)
                
            pygame.display.update()