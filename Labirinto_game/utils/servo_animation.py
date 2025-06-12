import pygame
import math
import time
from constants import padroes_servo
from utils.drawing import resize

class AnimacaoServos:
    """Classe para renderizar e animar os servos motores com base nos padrões de cada nível."""
    
    def __init__(self, nivel, servo_velocidade="normal"):
        """
        Inicializa a animação dos servos.
        
        Args:
            nivel (int): O nível atual do jogo.
            servo_velocidade (str): "lento", "normal" ou "rapido"
        """
        self.nivel = nivel
        self.padrao = padroes_servo.get(nivel, [])
        self.tempo_inicio = time.time()
        self.indice_atual = 0
        self.tempo_proximo_passo = 0
        self.duracao_total = sum(duracao for _, duracao in self.padrao) / 1000 if self.padrao else 0
        
        # Ângulos atuais dos servos (0-180)
        self.angulo_servo1 = 90
        self.angulo_servo2 = 90  # Espelhado: 180 - servo1
        
        # Ângulos alvo para interpolação suave
        self.angulo_alvo1 = 90
        self.angulo_alvo2 = 90
        
        # Tempo de início da interpolação
        self.tempo_inicio_interpolacao = 0
        
        # Ajuste de velocidade de transição conforme acessibilidade
        if servo_velocidade == "lento":
            self.duracao_interpolacao = 4
        elif servo_velocidade == "rapido":
            self.duracao_interpolacao = 0.9
        else:
            self.duracao_interpolacao = 2
        
        # Cores e dimensões
        self.cor_base = (100, 100, 100)  # Cinza para a base
        self.cor_servo = (30, 30, 30)    # Cinza escuro para o corpo
        self.cor_braco = (200, 200, 200) # Branco para os braços
        self.cor_detalhe = (255, 50, 50) # Vermelho para detalhes
        
        # Dimensões
        self.largura_base = resize(200, eh_X=True)
        self.altura_base = resize(30)
        self.tamanho_servo = resize(80)
        self.comprimento_braco = resize(120)
        self.espessura_braco = resize(15)
        
        # Espaçamento horizontal entre os servos (aumentado para evitar colisão)
        self.espaco_entre_servos = resize(260, eh_X=True)
        
    def atualizar(self):
        """Atualiza o estado da animação dos servos."""
        if not self.padrao or self.nivel == 1:  # Não animar para o nível 1
            return

        tempo_atual = time.time()

        # Lógica para garantir que o servo chegue ao alvo antes de iniciar o hold
        # 1. Só começa a contar o hold quando o ângulo atual está suficientemente próximo do alvo
        # 2. Só avança para o próximo passo após o hold

        # Estado: estamos indo para o alvo ou segurando no alvo?
        if not hasattr(self, "_hold_ate"):
            self._hold_ate = None
            self._em_hold = False

        # Chegou suficientemente perto do alvo?
        chegou1 = abs(self.angulo_servo1 - self.angulo_alvo1) < 0.5
        chegou2 = abs(self.angulo_servo2 - self.angulo_alvo2) < 0.5
        chegou = chegou1 and chegou2

        if not self._em_hold:
            # Interpolação até o alvo
            progresso = min(1.0, (tempo_atual - self.tempo_inicio_interpolacao) / self.duracao_interpolacao)
            progresso = self._ease_in_out(progresso)
            self.angulo_servo1 = self._interpolar(self.angulo_servo1, self.angulo_alvo1, progresso)
            self.angulo_servo2 = self._interpolar(self.angulo_servo2, self.angulo_alvo2, progresso)

            if chegou:
                # Inicia o hold
                if self.indice_atual < len(self.padrao):
                    _, duracao_ms = self.padrao[self.indice_atual]
                    self._hold_ate = tempo_atual + duracao_ms / 1000
                    self._em_hold = True
        else:
            # Durante o hold, mantém o ângulo exatamente no alvo
            self.angulo_servo1 = self.angulo_alvo1
            self.angulo_servo2 = self.angulo_alvo2
            if tempo_atual >= self._hold_ate:
                # Avança para o próximo passo
                self.indice_atual += 1
                if self.indice_atual >= len(self.padrao):
                    self.indice_atual = 0
                angulo, _ = self.padrao[self.indice_atual]
                self.angulo_alvo1 = angulo
                self.angulo_alvo2 = 180 - angulo
                self.tempo_inicio_interpolacao = tempo_atual
                self._em_hold = False
                self._hold_ate = None
    
    def _interpolar(self, inicio, fim, progresso):
        """Interpola linearmente entre dois valores."""
        return inicio + (fim - inicio) * progresso
    
    def _ease_in_out(self, x):
        """Função de suavização para interpolação."""
        return -(math.cos(math.pi * x) - 1) / 2
    
    def desenhar(self, tela):
        """Desenha os servos na tela."""
        if self.nivel == 1:  # Não mostrar para o nível 1
            return
            
        largura_tela = tela.get_width()
        altura_tela = tela.get_height()
        
        # Posição da base (centrada horizontalmente, mais abaixo para não sobrepor texto)
        base_x = (largura_tela - (2 * self.tamanho_servo + self.espaco_entre_servos)) // 2
        base_y = altura_tela // 2 + resize(100)  # Desce o conjunto
        
        # Posições dos centros dos servos (um de frente para o outro)
        servo1_centro_x = base_x + self.tamanho_servo // 2
        servo2_centro_x = base_x + self.tamanho_servo + self.espaco_entre_servos + self.tamanho_servo // 2
        servo_centro_y = base_y
        
        
        # Desenha o primeiro servo (esquerda, braço para fora)
        self._desenhar_servo(tela, servo1_centro_x, servo_centro_y, self.angulo_servo1, True, invertido=False)
        # Desenha o segundo servo (direita, braço para fora)
        self._desenhar_servo(tela, servo2_centro_x, servo_centro_y, self.angulo_servo2, False, invertido=True)
        
        # Texto explicativo (mais abaixo)
        fonte = pygame.font.SysFont("Arial", resize(28, eh_X=True), bold=True)
        texto_linha1 = "Visualização dos Servos"
        texto_linha2 = f"Padrão Nível {self.nivel}"
        
        surf_texto1 = fonte.render(texto_linha1, True, (255, 255, 255))
        surf_texto2 = fonte.render(texto_linha2, True, (255, 255, 255))
        
        tela.blit(surf_texto1, (largura_tela // 2 - surf_texto1.get_width() // 2, 
                                base_y + self.tamanho_servo + resize(80)))
        tela.blit(surf_texto2, (largura_tela // 2 - surf_texto2.get_width() // 2, 
                                base_y + self.tamanho_servo + resize(120)))
    
    def _desenhar_servo(self, tela, centro_x, centro_y, angulo, is_first, invertido=False):
        """Desenha um único servo motor com seu braço na posição angular especificada."""
        # Desenha o corpo do servo (quadrado)
        offset = self.tamanho_servo // 2
        pygame.draw.rect(tela, self.cor_servo, 
                        (centro_x - offset, centro_y - offset, 
                         self.tamanho_servo, self.tamanho_servo),
                        border_radius=resize(8))
        
        # Adiciona detalhes ao corpo do servo
        pygame.draw.rect(tela, self.cor_detalhe, 
                        (centro_x - offset + resize(8), centro_y - offset + resize(8), 
                         self.tamanho_servo - resize(16), self.tamanho_servo - resize(16)),
                        width=resize(2), border_radius=resize(4))
        
        # Para ambos, 90 graus é horizontal (braço para fora do centro)
        # 0 graus = para cima, 90 graus = para fora, 180 graus = para baixo
        # Para o servo da esquerda (invertido=False), 90° = para a esquerda
        # Para o servo da direita (invertido=True), 90° = para a direita
        if invertido:
            # Servo direito: base é 180°, aumenta horário, diminui anti-horário
            angulo_rad = math.radians(180 + (angulo - 90))
        else:
            # Servo esquerdo: 90° = direita (horizontal), aumenta anti-horário, diminui horário (mantém como está)
            angulo_rad = math.radians(0 + (angulo - 90))

        ponto_central = (centro_x, centro_y)
        ponta_braco_x = ponto_central[0] + math.cos(angulo_rad) * self.comprimento_braco
        ponta_braco_y = ponto_central[1] - math.sin(angulo_rad) * self.comprimento_braco
        
        # Desenha o eixo de rotação (círculo no centro do servo)
        pygame.draw.circle(tela, (255, 255, 255), ponto_central, resize(10))
        pygame.draw.circle(tela, (0, 0, 0), ponto_central, resize(4))
        
        # Desenha o braço do servo (linha grossa)
        pygame.draw.line(tela, self.cor_braco, ponto_central, 
                        (ponta_braco_x, ponta_braco_y), self.espessura_braco)
        
        # Adiciona um "marcador" no braço para tornar o movimento mais visível
        marcador_x = ponto_central[0] + math.cos(angulo_rad) * (self.comprimento_braco * 0.7)
        marcador_y = ponto_central[1] - math.sin(angulo_rad) * (self.comprimento_braco * 0.7)
        pygame.draw.circle(tela, self.cor_detalhe, (marcador_x, marcador_y), resize(8))
        
        # Exibe o ângulo atual
        fonte_angulo = pygame.font.SysFont("Arial", resize(18, eh_X=True), bold=True)
        texto_angulo = f"{int(angulo)}°"
        surf_angulo = fonte_angulo.render(texto_angulo, True, (255, 255, 255))
        posicao_texto = (centro_x - surf_angulo.get_width() // 2, 
                          centro_y + self.tamanho_servo // 2 + resize(20))
        tela.blit(surf_angulo, posicao_texto)
        
        # Identifica qual servo é
        nome = "Servo Esquerdo" if is_first else "Servo Direito"
        surf_nome = fonte_angulo.render(nome, True, (200, 200, 200))
        pos_nome = (centro_x - surf_nome.get_width() // 2, 
                    centro_y + self.tamanho_servo // 2 + resize(40))
        tela.blit(surf_nome, pos_nome)
