import pygame
import sys
from pygame.locals import *
from utils.drawing import resize
from constants import LARGURA_TELA, ALTURA_TELA

class TelaDialogoInicial:
    def __init__(self, tela, dark =False):
        # Inicialização
        self.tela = tela
        self.largura_tela = tela.get_width()
        self.altura_tela = tela.get_height()
        
        # Carrega imagens
        if not dark:
            self.fundo = pygame.image.load("Labirinto_game/assets/images/fundo_dialogo.png").convert_alpha()
        else :
            self.fundo = pygame.image.load("Labirinto_game/assets/images/fundo_dialogo_dark.png").convert_alpha()
        self.fundo = pygame.transform.scale(self.fundo, (LARGURA_TELA, ALTURA_TELA))
        
        if not dark:
            self.personagem = pygame.image.load("Labirinto_game/assets/images/teseu.png").convert_alpha()
        else:
            self.personagem = pygame.image.load("Labirinto_game/assets/images/teseu_old.png").convert_alpha()
        self.personagem = pygame.transform.scale(self.personagem, (resize(800, eh_X=True), resize(800)))
        # Posiciona personagem no meio da tela
        self.personagem_rect = self.personagem.get_rect(center=(LARGURA_TELA - resize(500, eh_X=True), ALTURA_TELA - resize(400)))
        
        # Configurações da caixa de diálogo
        self.caixa_dialogo = pygame.Rect(
            resize(self.largura_tela * 0.1, eh_X=True),  # x
            resize(self.altura_tela * 0.7),  # y
            resize(self.largura_tela * 0.6, eh_X=True),   # largura
            resize(self.altura_tela * 0.2)    # altura
        )
        
        # Configurações do texto de diálogo
        self.fonte = pygame.font.Font(None, resize(36))
        self.cor_texto = (255, 255, 255)
        if not dark:
            self.linhas_dialogo = [
            "Ei, que bom que você chegou! Eu sou Teseu, e estou explorando este grande labirinto mágico. Ouvi falar que ele tem caminhos que se mexem e um monstro escondido chamado Minotauro.",
            "Eu preciso de alguém especial para me acompanhar. Não consigo percorrer todos esses corredores sozinho! Você poderá usar um anel mágico para desviar das paredes de metal. Mas cuidado: se encostar, perdemos uma vida.",
            "Se isso acontecer, não desanime! Podemos tentar outra vez. Quando acertarmos o caminho, sons e luzes vão nos dar dicas de que estamos indo bem. E lá na frente, quem sabe... pode ter uma surpresa!",
            "Então, o que acha? Vamos nos aventurar juntos? O labirinto é grande, mas com a sua ajuda, tenho certeza de que chegaremos ao fim!"
        ]
        else:
            self.linhas_dialogo = [
            "Está se perguntando onde veio parar, não é? Bem-vindo(a) a Creta. Este é o Labirinto que todos temem: passagens que mudam de forma, metal que vibra, e algo mais sombrio esperando no coração dele.",
            "Eu sou Teseu, mas eu sozinho não basto. Dizem que um monstro chamado Minotauro vaga por aí, e só a união de coragem e foco pode nos levar até ele. Se você acha que tem isso então me diga o seu nome e juntos triunfaremos.",
            "Nosso instrumento é este anel, que deslizará por fios metálicos sem encostar. Parece simples, mas as paredes são imprevisíveis. Cada colisão custa uma vida, e você só tem três chances por etapa para não fracassar.",
            "Enquanto avançamos, fique atento(a) aos sinais de luz e som. Eles podem salvar nossa pele. Se falhar, aprenda com o erro; se triunfar, avance mais fundo no Labirinto. Dizem que o próprio Minotauro vigia suas presas…",
            "Então faremos parte da lenda de Creta. E talvez a própria ilha nos reconheça como libertadores."
        ]
        self.linha_atual = 0
        self.indice_animacao_texto = 0
        self.velocidade_animacao_texto = 1  # Caracteres por quadro
        self.contador_animacao_texto = 0
        
        # Configurações da animação de despertar
        self.alpha_despertar = 255  # Começa com tela preta
        self.velocidade_despertar = 2  # Velocidade da animação de despertar
        self.despertando = True
        
        # Indicador de pressionar tecla
        self.fonte_indicador = pygame.font.Font(None, resize(24))
        self.texto_indicador = "Pressione qualquer tecla para continuar..."
        
        # Espaçamento entre linhas de texto
        self.espacamento_linhas = resize(30)
        self.max_largura_linha = self.caixa_dialogo.width - resize(40, eh_X=True)
        
        # Variáveis para o popup de entrada de nome
        self.mostrar_popup = False
        self.nome_usuario = ""
        self.ativo_input = False
        self.fonte_popup = pygame.font.SysFont("comicsansms", resize(40, eh_X=True))
        self.cor_popup_inativa = (150, 150, 150)
        self.cor_popup_ativa = (200, 200, 200)
        self.cor_botao_confirmar = (0, 150, 0)
        self.cor_botao_confirmar_hover = (0, 200, 0)
        self.nome_escolhido = None  # Para armazenar o nome após confirmação
        
        # Retângulo do campo de entrada de texto
        self.rect_entrada = pygame.Rect(
            LARGURA_TELA//2 - resize(200, eh_X=True),
            ALTURA_TELA//2 - resize(30),
            resize(400, eh_X=True),
            resize(60)
        )
        
        # Retângulo do botão de confirmação
        self.rect_confirmar = pygame.Rect(
            LARGURA_TELA//2 - resize(100, eh_X=True),
            self.rect_entrada.y + self.rect_entrada.height + resize(20),
            resize(200, eh_X=True),
            resize(50)
        )
    
    def quebrar_texto(self, texto):
        """Quebra o texto em múltiplas linhas para caber na caixa de diálogo"""
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ''
        
        for palavra in palavras:
            # Teste se a palavra cabe na linha atual
            teste_linha = linha_atual + ' ' + palavra if linha_atual else palavra
            largura_teste = self.fonte.size(teste_linha)[0]
            
            if largura_teste <= self.max_largura_linha:
                linha_atual = teste_linha
            else:
                # Se não couber, adiciona a linha atual e começa uma nova
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = palavra
        
        # Adiciona a última linha se não estiver vazia
        if linha_atual:
            linhas.append(linha_atual)
            
        return linhas
    
    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if self.mostrar_popup:
                # Eventos para o popup de entrada de nome
                if evento.type == MOUSEBUTTONDOWN:
                    # Verifica se clicou no campo de texto
                    if self.rect_entrada.collidepoint(evento.pos):
                        self.ativo_input = True
                    else:
                        self.ativo_input = False
                        
                    # Verifica se clicou no botão confirmar
                    if self.rect_confirmar.collidepoint(evento.pos) and self.nome_usuario.strip():
                        self.mostrar_popup = False
                        self.nome_escolhido = self.nome_usuario.strip()
                        # Continua o diálogo a partir da linha 3 (índice 2)
                        self.linha_atual = 2
                        self.indice_animacao_texto = 0
                        
                elif evento.type == KEYDOWN:
                    if self.ativo_input:
                        if evento.key == pygame.K_RETURN and self.nome_usuario.strip():
                            self.mostrar_popup = False
                            self.nome_escolhido = self.nome_usuario.strip()
                            # Continua o diálogo a partir da linha 3 (índice 2)
                            self.linha_atual = 2
                            self.indice_animacao_texto = 0
                        elif evento.key == pygame.K_BACKSPACE:
                            self.nome_usuario = self.nome_usuario[:-1]
                        else:
                            # Limita o tamanho do nome a 15 caracteres
                            if len(self.nome_usuario) < 15:
                                self.nome_usuario += evento.unicode
                return False
            
            else:
                # Eventos normais do diálogo
                if evento.type == KEYDOWN or evento.type == MOUSEBUTTONDOWN:
                    if self.despertando:
                        # Pular animação de despertar se alguma tecla for pressionada
                        self.despertando = False
                        self.alpha_despertar = 0
                    elif self.indice_animacao_texto < len(self.linhas_dialogo[self.linha_atual]):
                        # Exibe a linha completa instantaneamente se a animação não estiver completa
                        self.indice_animacao_texto = len(self.linhas_dialogo[self.linha_atual])
                    else:
                        # Passa para a próxima linha se a animação estiver completa
                        self.linha_atual += 1
                        self.indice_animacao_texto = 0
                        
                        # Verifica se precisa mostrar o popup após a segunda linha
                        if self.linha_atual == 2:  # Após a segunda linha (índices 0 e 1)
                            self.mostrar_popup = True
                            return False
                        
                        # Retorna True quando todo o diálogo for exibido
                        if self.linha_atual >= len(self.linhas_dialogo):
                            return True
        
        return False
    
    def atualizar(self):
        # Atualiza a animação de despertar
        if self.despertando:
            self.alpha_despertar -= self.velocidade_despertar
            if self.alpha_despertar <= 0:
                self.alpha_despertar = 0
                self.despertando = False
        
        # Atualiza a animação do texto
        if not self.despertando and self.linha_atual < len(self.linhas_dialogo):
            self.contador_animacao_texto += 1
            if self.contador_animacao_texto >= self.velocidade_animacao_texto:
                self.contador_animacao_texto = 0
                if self.indice_animacao_texto < len(self.linhas_dialogo[self.linha_atual]):
                    self.indice_animacao_texto += 1

    def desenhar_popup(self):
        """Desenha o popup para entrada do nome do usuário"""
        # Overlay semi-transparente para escurecer o fundo
        overlay = pygame.Surface((self.largura_tela, self.altura_tela), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.tela.blit(overlay, (0, 0))
        
        # Desenha o painel do popup
        popup_rect = pygame.Rect(
            LARGURA_TELA//2 - resize(250, eh_X=True),
            ALTURA_TELA//2 - resize(150),
            resize(500, eh_X=True),
            resize(300)
        )
        pygame.draw.rect(self.tela, (50, 50, 70), popup_rect, border_radius=resize(15))
        pygame.draw.rect(self.tela, (200, 200, 220), popup_rect, width=resize(3), border_radius=resize(15))
        
        # Título do popup
        titulo_texto = self.fonte_popup.render("Digite seu nome:", True, (255, 255, 255))
        titulo_rect = titulo_texto.get_rect(center=(LARGURA_TELA//2, popup_rect.y + resize(40)))
        self.tela.blit(titulo_texto, titulo_rect)
        
        # Campo de entrada de texto
        cor_atual = self.cor_popup_ativa if self.ativo_input else self.cor_popup_inativa
        pygame.draw.rect(self.tela, cor_atual, self.rect_entrada, border_radius=resize(10))
        
        # Texto digitado pelo usuário
        texto_superficie = self.fonte_popup.render(self.nome_usuario, True, (0, 0, 0))
        # Centralize o texto verticalmente e o alinhe à esquerda horizontalmente
        self.tela.blit(texto_superficie, (self.rect_entrada.x + resize(10, eh_X=True), 
                                         self.rect_entrada.y + self.rect_entrada.height//2 - texto_superficie.get_height()//2))
        
        # Adiciona cursor piscante quando ativo
        if self.ativo_input and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = self.rect_entrada.x + resize(10, eh_X=True) + texto_superficie.get_width() + resize(2, eh_X=True)
            pygame.draw.line(self.tela, (0, 0, 0), 
                            (cursor_x, self.rect_entrada.y + resize(15)),
                            (cursor_x, self.rect_entrada.y + self.rect_entrada.height - resize(15)), 
                            resize(2, eh_X=True))
        
        # Botão de confirmação
        pos_mouse = pygame.mouse.get_pos()
        mouse_sobre_botao = self.rect_confirmar.collidepoint(pos_mouse)
        cor_botao = self.cor_botao_confirmar_hover if mouse_sobre_botao else self.cor_botao_confirmar
        
        pygame.draw.rect(self.tela, cor_botao, self.rect_confirmar, border_radius=resize(10))
        botao_texto = self.fonte_popup.render("Confirmar", True, (255, 255, 255))
        botao_rect = botao_texto.get_rect(center=self.rect_confirmar.center)
        self.tela.blit(botao_texto, botao_rect)

    def desenhar(self):
        # Desenha o fundo
        self.tela.blit(self.fundo, (0, 0))
        
        # Desenha o personagem
        self.tela.blit(self.personagem, self.personagem_rect)
        
        if not self.mostrar_popup:
            # Desenha a caixa de diálogo (semi-transparente)
            superficie_dialogo = pygame.Surface((self.caixa_dialogo.width, self.caixa_dialogo.height), pygame.SRCALPHA)
            superficie_dialogo.fill((0, 0, 0, 180))  # Preto com transparência
            self.tela.blit(superficie_dialogo, (self.caixa_dialogo.x, self.caixa_dialogo.y))
            
            # Desenha o texto se não estiver despertando e houver linhas para exibir
            if not self.despertando and self.linha_atual < len(self.linhas_dialogo):
                # Obtém o texto atual para exibir (baseado na animação)
                texto_atual = self.linhas_dialogo[self.linha_atual][:self.indice_animacao_texto]
                
                # Quebra o texto em múltiplas linhas
                linhas_renderizadas = self.quebrar_texto(texto_atual)
                
                # Renderiza cada linha separadamente
                for idx, linha in enumerate(linhas_renderizadas):
                    superficie_texto = self.fonte.render(linha, True, self.cor_texto)
                    posicao_y = self.caixa_dialogo.y + resize(20) + idx * self.espacamento_linhas
                    self.tela.blit(superficie_texto, (self.caixa_dialogo.x + resize(20, eh_X=True), posicao_y))
                
                # Desenha o indicador "pressione qualquer tecla" se a animação do texto estiver completa
                if self.indice_animacao_texto >= len(self.linhas_dialogo[self.linha_atual]):
                    superficie_indicador = self.fonte_indicador.render(self.texto_indicador, True, self.cor_texto)
                    posicao_indicador = (
                        self.caixa_dialogo.x + self.caixa_dialogo.width - superficie_indicador.get_width() - resize(20, eh_X=True),
                        self.caixa_dialogo.y + self.caixa_dialogo.height - superficie_indicador.get_height() - resize(10)
                    )
                    self.tela.blit(superficie_indicador, posicao_indicador)
        else:
            # Desenhar o popup quando ativado
            self.desenhar_popup()
        
        # Desenha a animação de despertar (sobreposição preta)
        if self.despertando:
            superficie_despertar = pygame.Surface((self.largura_tela, self.altura_tela))
            superficie_despertar.fill((0, 0, 0))
            superficie_despertar.set_alpha(self.alpha_despertar)
            self.tela.blit(superficie_despertar, (0, 0))
    
    def executar(self):
        relogio = pygame.time.Clock()
        concluido = False
        nome_usuario = None
        
        while not concluido:
            concluido = self.tratar_eventos()
            self.atualizar()
            self.desenhar()
            
            pygame.display.flip()
            relogio.tick(60)
        
        return self.nome_escolhido  # Retorna o nome escolhido pelo usuário