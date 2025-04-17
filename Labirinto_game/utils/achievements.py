import pygame
import time
import math
import os
from utils.user_data import carregar_usuarios, salvar_usuarios
from utils.drawing import resize

class SistemaConquistas:
    """Sistema de gerenciamento de conquistas do jogo"""
    
    def __init__(self):
        self.conquistas = {
            'fio_de_ariadne': {
                'nome': 'Fio de Ariadne', 
                'descricao': 'Complete seu primeiro nível com sucesso',
                'icone': 'Labirinto_game/assets/images/achievements/Fio_de_Ariadne.png',
                'desbloqueada': False
            },
            'coragem_de_teseu': {
                'nome': 'Coragem de Teseu', 
                'descricao': 'Complete um nível sem perder nenhuma vida',
                'icone': 'Labirinto_game/assets/images/achievements/Coragem_de_Teseu.png',
                'desbloqueada': False
            },
            'despertar_da_furia': {
                'nome': 'Despertar da Fúria', 
                'descricao': 'Complete um nível após perder 2 vidas',
                'icone': 'Labirinto_game/assets/images/achievements/Despertar_da_Furia.png',
                'desbloqueada': False
            },
            'domador_do_labirinto': {
                'nome': 'Domador do Labirinto', 
                'descricao': 'Complete 5 fases diferentes',
                'icone': 'Labirinto_game/assets/images/achievements/Domador_do_Labirinto.png',
                'desbloqueada': False
            },
            'renascido': {
                'nome': 'Renascido', 
                'descricao': 'Tente a mesma fase 7 vezes consecutivas',
                'icone': 'Labirinto_game/assets/images/achievements/Renascido.png',
                'desbloqueada': False
            },
            'heroi_de_atenas': {
                'nome': 'Herói de Atenas', 
                'descricao': 'Complete todas as fases do jogo',
                'icone': 'Labirinto_game/assets/images/achievements/Heroi_de_Atenas.png',
                'desbloqueada': False
            },
            'velocista_olimpico': {
                'nome': 'Velocista Olímpico', 
                'descricao': 'Completar um nível em menos de 10 segundos',
                'icone': 'Labirinto_game/assets/images/achievements/Velocista_Olimpico.png',  
                'desbloqueada': False
            },
            'mestre_dos_servos': {
                'nome': 'Mestre dos Servos', 
                'descricao': 'Vencer uma fase com movimentação aleatória dos motores ativada',
                'icone': 'Labirinto_game/assets/images/achievements/Mestre_dos_Servos.png',
                'desbloqueada': False
            },
            'pegadas_de_bronze': {
                'nome': 'Pegadas de Bronze', 
                'descricao': 'Jogue o jogo 50 vezes',
                'icone': 'Labirinto_game/assets/images/achievements/Pegadas_de_Bronze.png',
                'desbloqueada': False
            }
        }
        
        # Notificação de conquista
        self.notificacao_ativa = False
        self.notificacao_texto = []
        self.notificacao_inicio = 0
        self.notificacao_duracao = 5  # segundos
        
        # Fonte para notificação
        self.fonte_notificacao = pygame.font.SysFont("comicsansms", resize(30, eh_X=True))
        
        self.conquistas_recentes = []
    
    def carregar_conquistas_usuario(self, usuario):
        """Carrega as conquistas do usuário"""
        usuarios_data = carregar_usuarios()
        if usuario in usuarios_data:
            if 'conquistas' not in usuarios_data[usuario]:
                usuarios_data[usuario]['conquistas'] = {k: False for k in self.conquistas.keys()}
                salvar_usuarios(usuarios_data)
            
            # Sincroniza o estado das conquistas
            for key in self.conquistas:
                self.conquistas[key]['desbloqueada'] = usuarios_data[usuario]['conquistas'].get(key, False)
        
        return self.conquistas
    
    def salvar_conquistas_usuario(self, usuario):
        """Salva as conquistas do usuário"""
        usuarios_data = carregar_usuarios()
        if usuario in usuarios_data:
            if 'conquistas' not in usuarios_data[usuario]:
                usuarios_data[usuario]['conquistas'] = {}
            
            for key in self.conquistas:
                usuarios_data[usuario]['conquistas'][key] = self.conquistas[key]['desbloqueada']
            
            salvar_usuarios(usuarios_data)
    
    def verificar_conquistas(self, usuario, dados_jogo):
        """Verifica se alguma conquista foi desbloqueada"""
        
        # Carrega conquistas atuais
        self.carregar_conquistas_usuario(usuario)
        
        # Verificações
        conquistas_desbloqueadas = []
        
        # Fio de Ariadne - Complete seu primeiro nível com sucesso
        niveis_completados = [t for t in dados_jogo.get('tentativas', []) if t.get('vidas', 0) > 0]
        if not self.conquistas['fio_de_ariadne']['desbloqueada'] and len(niveis_completados) >= 1:
            self.conquistas['fio_de_ariadne']['desbloqueada'] = True
            conquistas_desbloqueadas.append('fio_de_ariadne')
            print("Conquista FIO DE ARIADNE desbloqueada!")
        
        # Coragem de Teseu - Complete um nível sem perder nenhuma vida
        nivel_atual = dados_jogo.get('nivel_atual', 1)
        vidas_atuais = dados_jogo.get('vidas_restantes', 0)
        vidas_iniciais = dados_jogo.get('vidas_iniciais', 3)
        if not self.conquistas['coragem_de_teseu']['desbloqueada'] and dados_jogo.get('concluido') and vidas_atuais == vidas_iniciais:
            self.conquistas['coragem_de_teseu']['desbloqueada'] = True
            conquistas_desbloqueadas.append('coragem_de_teseu')
            print("Conquista CORAGEM DE TESEU desbloqueada!")
        
        # Despertar da Fúria - Complete um nível após perder 2 vidas
        if not self.conquistas['despertar_da_furia']['desbloqueada'] and dados_jogo.get('concluido') and vidas_iniciais - vidas_atuais >= 2:
            self.conquistas['despertar_da_furia']['desbloqueada'] = True
            conquistas_desbloqueadas.append('despertar_da_furia')
            print("Conquista DESPERTAR DA FÚRIA desbloqueada!")
        
        # Domador do Labirinto - Complete 5 fases diferentes
        niveis_diferentes_completados = set(t.get('nivel') for t in dados_jogo.get('tentativas', []) if t.get('vidas', 0) > 0)
        if not self.conquistas['domador_do_labirinto']['desbloqueada'] and len(niveis_diferentes_completados) >= 5:
            self.conquistas['domador_do_labirinto']['desbloqueada'] = True
            conquistas_desbloqueadas.append('domador_do_labirinto')
            print("Conquista DOMADOR DO LABIRINTO desbloqueada!")
        
        # Renascido - Tente a mesma fase 7 vezes consecutivas
        nivel_atual = dados_jogo.get('nivel_atual', 1)
        tentativas_nivel = [t for t in dados_jogo.get('tentativas', []) if t.get('nivel') == nivel_atual]
        if not self.conquistas['renascido']['desbloqueada'] and len(tentativas_nivel) >= 7:
            self.conquistas['renascido']['desbloqueada'] = True
            conquistas_desbloqueadas.append('renascido')
            print("Conquista RENASCIDO desbloqueada!")
        
        # Herói de Atenas - Complete todas as fases do jogo
        total_niveis = dados_jogo.get('total_niveis', 8)  # Assumindo que há 8 níveis no jogo
        if not self.conquistas['heroi_de_atenas']['desbloqueada'] and len(niveis_diferentes_completados) >= total_niveis:
            self.conquistas['heroi_de_atenas']['desbloqueada'] = True
            conquistas_desbloqueadas.append('heroi_de_atenas')
            print("Conquista HERÓI DE ATENAS desbloqueada!")
        
        # Velocista Olímpico - Completar um nível em menos de 10 segundos
        if not self.conquistas['velocista_olimpico']['desbloqueada'] and dados_jogo.get('tempo_gasto', 999) < 10 and dados_jogo.get('concluido'):
            self.conquistas['velocista_olimpico']['desbloqueada'] = True
            conquistas_desbloqueadas.append('velocista_olimpico')
            print("Conquista VELOCISTA OLÍMPICO desbloqueada!")
        
        # Mestre dos Servos - Vencer uma fase com movimentação aleatória dos motores ativada
        if not self.conquistas['mestre_dos_servos']['desbloqueada'] and dados_jogo.get('concluido') and dados_jogo.get('motores_aleatorios'):
            self.conquistas['mestre_dos_servos']['desbloqueada'] = True
            conquistas_desbloqueadas.append('mestre_dos_servos')
            print("Conquista MESTRE DOS SERVOS desbloqueada!")
        
        # Pegadas de Bronze - Jogue o jogo 50 vezes
        total_jogos = len(dados_jogo.get('tentativas', []))
        if not self.conquistas['pegadas_de_bronze']['desbloqueada'] and total_jogos >= 50:
            self.conquistas['pegadas_de_bronze']['desbloqueada'] = True
            conquistas_desbloqueadas.append('pegadas_de_bronze')
            print("Conquista PEGADAS DE BRONZE desbloqueada!")
        
        # Salva conquistas atualizadas
        self.salvar_conquistas_usuario(usuario)
        
        # Se desbloqueou alguma, ativa notificação
        if conquistas_desbloqueadas:
            for chave in conquistas_desbloqueadas:
                self.mostrar_notificacao(f"Conquista desbloqueada: {self.conquistas[chave]['nome']}")
            self.conquistas_recentes = conquistas_desbloqueadas.copy()
            
        return conquistas_desbloqueadas
    
    def mostrar_notificacao(self, texto):
        from utils.audio_manager import audio_manager
        """Ativa a notificação de conquista"""
        self.notificacao_ativa = True
        self.notificacao_texto.append(texto)
        self.notificacao_inicio = time.time()
        audio_manager.play_sound("achievement")
    
    def desenhar_notificacao(self, tela):
        """Desenha a notificação de conquista na tela com efeitos visuais aprimorados"""
        if not self.notificacao_ativa or not self.notificacao_texto:
            return

        # Verifica se a notificação ainda deve ser exibida
        tempo_decorrido = time.time() - self.notificacao_inicio
        if tempo_decorrido > self.notificacao_duracao:
            self.notificacao_ativa = False
            self.notificacao_texto = []
            return
        
        # Configurações visuais
        largura_tela, altura_tela = tela.get_size()
        altura_notificacao = resize(100)
        largura_notificacao = resize(700, eh_X=True)
        
        # Efeitos de animação baseados no tempo
        progresso = min(1.0, tempo_decorrido / 0.5)  # 0.5s para entrada completa
        progresso_saida = max(0.0, min(1.0, (tempo_decorrido - (self.notificacao_duracao - 0.8)) / 0.8)) if tempo_decorrido > (self.notificacao_duracao - 0.8) else 0
        
        # Efeito de entrada/saída
        deslocamento_y = int((1.0 - progresso) * resize(-150))  # Vem de cima
        deslocamento_y += int(progresso_saida * resize(150))  # Sai para cima
        
        # Efeito de opacidade
        opacidade = int(255 * progresso * (1.0 - progresso_saida))
        
        y_offset = 0
        for index, texto in enumerate(self.notificacao_texto):
            if not texto:
                continue
                
            # Extrai a chave da conquista do texto
            chave_conquista = None
            for chave in self.conquistas:
                if self.conquistas[chave]['nome'] in texto:
                    chave_conquista = chave
                    break
            
            # Posição base da notificação
            x = (largura_tela - largura_notificacao) // 2
            y = resize(80) + y_offset + deslocamento_y
            
            # Superfície para a notificação
            notificacao_surface = pygame.Surface((largura_notificacao, altura_notificacao), pygame.SRCALPHA)
            
            # Fundo gradiente com cantos arredondados
            gradiente_surface = pygame.Surface((largura_notificacao, altura_notificacao), pygame.SRCALPHA)
            for i in range(altura_notificacao):
                cor = (40, 40, 60, min(200, opacidade) * (i / altura_notificacao))
                pygame.draw.line(gradiente_surface, cor, (0, i), (largura_notificacao, i))
            
            # Criar uma máscara com cantos arredondados
            mascara = pygame.Surface((largura_notificacao, altura_notificacao), pygame.SRCALPHA)
            pygame.draw.rect(mascara, (255, 255, 255, 255), 
                            pygame.Rect(0, 0, largura_notificacao, altura_notificacao), 
                            border_radius=resize(15))
            
            # Aplicar a máscara ao gradiente para criar o gradiente com cantos arredondados
            gradiente_final = pygame.Surface((largura_notificacao, altura_notificacao), pygame.SRCALPHA)
            gradiente_final.blit(mascara, (0, 0))
            gradiente_final.blit(gradiente_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Aplicar o gradiente com cantos arredondados à notificação
            notificacao_surface.blit(gradiente_final, (0, 0))
            
            # Borda
            pygame.draw.rect(notificacao_surface, (255, 215, 0, opacidade), 
                             (0, 0, largura_notificacao, altura_notificacao), 
                             width=resize(3), border_radius=resize(15))
            
            # Desenha fundo principal
            pygame.draw.rect(notificacao_surface, (20, 20, 40, min(230, opacidade)), 
                             (resize(3, eh_X=True), resize(3), largura_notificacao-resize(6, eh_X=True), altura_notificacao-resize(6)), 
                             border_radius=resize(13))
            
            # Adiciona brilho na borda (efeito pulsante)
            pulso = 0.5 + 0.5 * math.sin(time.time() * 5)
            cor_brilho = (255, 215, 0, int(120 * pulso * (1.0 - progresso_saida)))
            pygame.draw.rect(notificacao_surface, cor_brilho, 
                             (0, 0, largura_notificacao, altura_notificacao), 
                             width=resize(3), border_radius=resize(15))
            
            # Desenha ícone da conquista, se disponível
            if chave_conquista and chave_conquista in self.conquistas:
                icone_path = self.conquistas[chave_conquista].get('icone')
                if icone_path and os.path.exists(icone_path):
                    try:
                        icone = pygame.image.load(icone_path).convert_alpha()
                        icone = pygame.transform.scale(icone, (resize(80, eh_X=True), resize(80)))
                        # Aplicar efeito de brilho ao redor do ícone
                        glow_surface = pygame.Surface((resize(96, eh_X=True), resize(96)), pygame.SRCALPHA)
                        for raio in range(resize(8), 0, -resize(2)):
                            pygame.draw.circle(glow_surface, (255, 215, 0, 15), (resize(48, eh_X=True), resize(48)), resize(40) + raio)
                        notificacao_surface.blit(glow_surface, (resize(10, eh_X=True), altura_notificacao//2 - resize(48)))
                        notificacao_surface.blit(icone, (resize(18, eh_X=True), altura_notificacao//2 - resize(40)))
                    except Exception as e:
                        print(f"Erro ao carregar ícone: {e}")
            
            # Texto "CONQUISTA DESBLOQUEADA!"
            fonte_titulo = pygame.font.SysFont("comicsansms", resize(22, eh_X=True), bold=True)
            texto_titulo = fonte_titulo.render("CONQUISTA DESBLOQUEADA!", True, (255, 215, 0))
            notificacao_surface.blit(texto_titulo, (resize(120, eh_X=True), resize(15)))
            
            # Texto da conquista
            nome_conquista = texto.replace("Conquista desbloqueada: ", "")
            fonte_conquista = pygame.font.SysFont("comicsansms", resize(28, eh_X=True))
            texto_conquista = fonte_conquista.render(nome_conquista, True, (255, 255, 255))
            notificacao_surface.blit(texto_conquista, (resize(120, eh_X=True), resize(45)))
            
            # Renderiza os brilhos e partículas
            tempo_atual = pygame.time.get_ticks() / 1000.0
            for i in range(10):
                pos_x = resize(120, eh_X=True) + int(resize(300, eh_X=True) * math.sin(tempo_atual * 2 + i * 0.5))
                pos_y = resize(45) + int(resize(10) * math.cos(tempo_atual * 3 + i * 0.7))
                raio = resize(2) + int(resize(2) * math.sin(tempo_atual * 4 + i))
                pygame.draw.circle(notificacao_surface, (255, 255, 200, int(100 * pulso)), 
                                  (pos_x % largura_notificacao, pos_y), raio)
            
            # Aplica a notificação na tela
            tela.blit(notificacao_surface, (x, y))
            
            y_offset += altura_notificacao + resize(10)
                
    def limpar_notificacoes(self):
        """Limpa todas as notificações pendentes e desativa a notificação atual"""
        self.fila_notificacoes = []
        self.notificacao_ativa = False
        self.notificacao_texto = []
        print("Fila de notificações limpa!")