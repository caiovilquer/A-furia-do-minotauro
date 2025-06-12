import pygame
import os

# Configurações básicas
display_info = pygame.display.Info()
LARGURA_TELA = display_info.current_w
ALTURA_TELA = display_info.current_h
TITULO_JOGO = "A Fúria do Minotauro"
FPS = 60

# Flags globais
ESCALA_CINZA = False  # Valor padrão, será substituído pelas configurações do usuário quando disponíveis
SOM_LIGADO = True
PORTA_SELECIONADA = None

# Cores e estilo
COR_TITULO = (250, 250, 100)
COR_TEXTO = (255, 200, 0)
COR_BOTAO_TEXTO = (255, 255, 255)

# --- Acessibilidade: valores padrão ---
VOLUME_MUSICA = 0.3
VOLUME_SFX = 1.0
VOLUME_VOZ = 0.8

REDUZIR_FLASHES = False

SERVO_VELOCIDADE = "normal"  # "lento", "normal", "rapido"

NUM_VIDAS = 3  # 1 a 5

DEBOUNCE_COLISAO_MS = 200  # ms

MODO_PRATICA = False

FEEDBACK_CANAL = "multiplo"  # "som", "cor", "led", "multiplo"
FEEDBACK_INTENSIDADE = 100  # 0-100

QUICK_TIME_EVENTS = True

DIALOGO_VELOCIDADE = 30  # ms/caractere, ou 0 para "instante"

from utils.drawing import resize

# Fontes
pygame.font.init()
FONTE_TITULO = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(100, eh_X=True))
FONTE_BOTAO = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(50, eh_X=True))
FONTE_BOTAO_REDUZIDA = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(45, eh_X=True))
FONTE_BARRA = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(30, eh_X=True))
FONTE_TEXTO = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(40, eh_X=True))

# Cores padrão
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARELO = (255, 255, 0)
AZUL_CLARO = (173, 216, 230)

# Caminhos para recursos
IMAGES_PATH = "Labirinto_game/assets/images/"
BACKGROUND_PATH = IMAGES_PATH + "backgrounds/tela_inicial.png"
BUTTON_PATH = IMAGES_PATH + "button1.png"
DIALOGO_PATH = IMAGES_PATH + "backgrounds/fundo_dialogo.png"
DIALOGO_DENTRO_PATH = IMAGES_PATH + "backgrounds/fundo_dialogo_labirinto_dark.png"
SOUND_PATH = "Labirinto_game/assets/sounds"
USUARIOS_JSON = "Labirinto_game/data/usuarios.json"

# Carregamento de imagens
if os.path.exists(BACKGROUND_PATH):
    background_img = pygame.image.load(BACKGROUND_PATH)
    background_img = pygame.transform.scale(background_img, (LARGURA_TELA, ALTURA_TELA))
else:
    background_img = None

if os.path.exists(DIALOGO_PATH):
    dialogo_img = pygame.image.load(DIALOGO_PATH)
    dialogo_img = pygame.transform.scale(dialogo_img, (LARGURA_TELA, ALTURA_TELA))
else:
    dialogo_img = None
    
if os.path.exists(DIALOGO_DENTRO_PATH):
    dialogo_dentro_img = pygame.image.load(DIALOGO_DENTRO_PATH)
    dialogo_dentro_img = pygame.transform.scale(dialogo_dentro_img, (LARGURA_TELA, ALTURA_TELA))
else:
    dialogo_dentro_img = None

# --- QTE Settings ---
QTE_CHANCE = 0.25  
QTE_TIMEOUT = 6        
QTE_SEQ_MIN = 3        
QTE_SEQ_MAX = 5       
QTE_INTERVALO_MIN = 10


# --- Padrões de Servo ---
# Formato: {número do nivel: [(ângulo, duração_ms), ...]}
padroes_servo = {
    1: [(90, 8000)],
    2: [(90, 2000), (110, 1500)],
    3: [(90, 1500), (120, 1200), (60, 1200)],
    4: [(90, 1200), (130, 1000), (50, 1000), (110, 1000)],
    5: [(90, 1000), (140, 800), (40, 800), (120, 700), (60, 700)],
    6: [(90, 800), (140, 600), (50, 600), (130, 500), (70, 500)],
    7: [(90, 800), (145, 500), (40, 500), (120, 400), (60, 400)],
    8: [(90, 600), (150, 400), (30, 400), (125, 350), (55, 350), (140, 300)],
}
