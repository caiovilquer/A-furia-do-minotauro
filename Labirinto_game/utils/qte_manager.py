import random
import time
from utils.audio_manager import audio_manager

class QTEManager:
    """Gerenciador de Quick Time Events (QTEs) para o jogo."""
    
    def __init__(self, timeout=6, seq_min=3, seq_max=5):
        self.timeout = timeout  # Tempo limite em segundos
        self.seq_min = seq_min  # Número mínimo de passos na sequência
        self.seq_max = seq_max  # Número máximo de passos na sequência
        self.sequencia = []  # Sequência atual de QTE (L ou R)
        self.passo_atual = 0  # Posição atual na sequência
        self.tempo_inicio = 0  # Quando o QTE foi iniciado
        self.ativo = False  # Se há um QTE em andamento
        self.sucesso = False  # Se o QTE foi completado com sucesso
        self.erro = False  # Se houve um erro no QTE
        self.timeout_ocorrido = False  # Se o tempo limite foi excedido
        self.concluido = False  # Se o QTE foi concluído (sucesso ou erro)
    
    def iniciar(self, sequencia=None):
        """Inicia um novo QTE com uma sequência específica ou aleatória."""
        self.tempo_inicio = time.time()
        self.passo_atual = 0
        self.ativo = True
        self.sucesso = False
        self.erro = False
        self.timeout_ocorrido = False
        self.concluido = False
        
        if sequencia is None:
            # Gera uma sequência aleatória
            tamanho = random.randint(self.seq_min, self.seq_max)
            self.sequencia = [random.choice(["E", "D"]) for _ in range(tamanho)]
        else:
            self.sequencia = sequencia
        
        print(f"QTE iniciado! Sequência: {self.sequencia}")
        
        # Tocar som de início
        audio_manager.play_sound("qte_start")
        
        return self.sequencia
    
    def processar_input(self, entrada):
        """Processa uma entrada de botão (L ou R).
        
        Returns:
            True: se o QTE foi completado com sucesso
            False: se houve erro
            None: se o QTE continua
        """
        if not self.ativo or self.concluido:
            return False
            
        print(f"Processando input QTE: {entrada}, esperado: {self.sequencia[self.passo_atual]}")
            
        if entrada == self.sequencia[self.passo_atual]:
            # Entrada correta
            audio_manager.play_sound("qte_hit")
            self.passo_atual += 1
            
            # Verifica se completou a sequência
            if self.passo_atual >= len(self.sequencia):
                self.sucesso = True
                self.concluido = True
                audio_manager.play_sound("qte_success")
                print("QTE completado com sucesso!")
                return True
        else:
            # Entrada incorreta
            self.erro = True
            self.concluido = True
            audio_manager.play_sound("qte_fail")
            print("QTE falhou: entrada incorreta!")
            return False
            
        return None  # Continua o QTE
    
    def atualizar(self, dt):
        """Atualiza o estado do QTE com base no tempo decorrido."""
        if not self.ativo or self.concluido:
            return
            
        tempo_atual = time.time()
        tempo_decorrido = tempo_atual - self.tempo_inicio
        
        if tempo_decorrido >= self.timeout:
            # Timeout
            self.timeout_ocorrido = True
            self.concluido = True
            print("QTE falhou: tempo esgotado!")
            audio_manager.play_sound("qte_fail")
    
    def tempo_restante(self):
        """Retorna o tempo restante em segundos."""
        if not self.ativo:
            return 0
            
        tempo_atual = time.time()
        tempo_decorrido = tempo_atual - self.tempo_inicio
        tempo_restante = max(0, self.timeout - tempo_decorrido)
        
        return tempo_restante
    
    def progresso_tempo(self):
        """Retorna o progresso do tempo como uma porcentagem (0-1)."""
        if not self.ativo:
            return 0
            
        return self.tempo_restante() / self.timeout
        
    def resetar(self):
        """Reseta o QTE para o estado inicial."""
        print("Resetando QTE manager")
        self.sequencia = []
        self.passo_atual = 0
        self.tempo_inicio = 0
        self.ativo = False
        self.sucesso = False
        self.erro = False
        self.timeout_ocorrido = False
        self.concluido = False
