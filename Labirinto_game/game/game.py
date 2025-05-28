import pygame
import sys
import time
import random
from datetime import datetime
from constants import (BUTTON_PATH, FONTE_BOTAO, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TEXTO, COR_TEXTO, PORTA_SELECIONADA)
from utils.drawing import aplicar_filtro_cinza_superficie, desenhar_texto, desenhar_botao, desenhar_barra_progresso, resize, TransitionEffect
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
        self.conexao_serial = conexao_serial  # Objeto de conexão serial
        
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
        
        # Enviar nível atual para o Arduino se necessário
        if self.conexao_serial:
            self.enviar_nivel_arduino()

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
        # Incrementa gradualmente o progresso para simular movimento
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
        
        # Reproduz o efeito sonoro padrão de colisão
        audio_manager.play_sound("collision")
        
        # Escolhe o áudio dublado correto baseado no número de vidas restantes
        if self.vidas == 1:
            audio_manager.play_voiced_dialogue("colisao_1vida")
        elif self.vidas == 2:
            audio_manager.play_voiced_dialogue("colisao_2vidas")
            
        print(f"Colisão! Progresso atual: {self.progresso:.2f}")

    def verifica_conclusao_nivel(self):
        """Verifica se o nível foi concluído."""
        # Se estiver usando comunicação serial, o Arduino já enviará o sinal de conclusão
        # Caso contrário, usamos a simulação
        if self.conexao_serial:
            return self.progresso >= 1.0
        else:
            return (time.time() - self.inicio_tempo) > 10 or self.progresso >= 1.0

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
            'vidas_restantes': self.vidas,
            'vidas_iniciais': 3,
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
        
        # Enviar novo nível para o Arduino se necessário
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
                from utils.audio_manager import audio_manager
                audio_manager.stop_voiced_dialogue();
                return

            # Se acabou as vidas
            if self.vidas <= 0:
                tempo_total = time.time() - self.inicio_tempo
                self.salvar_progresso(tempo_total, falhou=True)
                self.jogo_ativo, pular_dialogo = tela_falhou(tela, self.sistema_conquistas)
                
                # Se decidiu continuar, reseta o nível e mostra o diálogo novamente
                if self.jogo_ativo:
                    self.resetar_nivel()
                    # Reinicia o loop para mostrar o diálogo novamente
                    return self.loop_principal(pular_dialogo=pular_dialogo)

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
            
            import constants
            if constants.ESCALA_CINZA:
                aplicar_filtro_cinza_superficie(tela)
                
            pygame.display.update()