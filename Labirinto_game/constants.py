import pygame
import os

# === CONFIGURAÇÕES BÁSICAS ===
LARGURA_TELA = 1920
ALTURA_TELA = 1080
TITULO_JOGO = "Labirinto Sensorial"
FPS = 60

# FLAGS GLOBAIS
ESCALA_CINZA = False  # Ajuste para True se quiser todos os botões em escala de cinza
SOM_LIGADO = True  # Ajuste para False se quiser desativar os sons
PORTA_SELECIONADA = None  # Para armazenar a escolha da porta serial do Arduino

# CORES E ESTILO DE FONTE PARA ASPECTO PUZZLE
COR_TITULO = (250, 250, 100)
COR_TEXTO = (255, 200, 0)
COR_BOTAO_TEXTO = (255, 255, 255)

# Fontes
pygame.font.init()
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
IMAGES_PATH = "Labirinto_game/assets/images/"
BACKGROUND_PATH = IMAGES_PATH + "background_labirinto4.png"
SOUND_PATH = "Labirinto_game/assets/sounds"
USUARIOS_JSON = "Labirinto_game/data/usuarios.json"

# Carregar imagem de fundo se existir
if os.path.exists(BACKGROUND_PATH):
    background_img = pygame.image.load(BACKGROUND_PATH)
    background_img = pygame.transform.scale(background_img, (LARGURA_TELA, ALTURA_TELA))
else:
    background_img = None