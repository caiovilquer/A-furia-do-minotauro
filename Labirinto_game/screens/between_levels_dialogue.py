import pygame
import sys
from pygame.locals import *
from utils.drawing import resize
from constants import LARGURA_TELA, ALTURA_TELA

class TelaDialogoEntreNiveis:
    def __init__(self, tela, dark=False):
        # Inicialização
        self.tela = tela
        self.largura_tela = tela.get_width()
        self.altura_tela = tela.get_height()
        
        # Carrega imagens
        if not dark:
            self.fundo = pygame.image.load("Labirinto_game/assets/images/fundo_dialogo_labirinto.png").convert_alpha()
        else:
            self.fundo = pygame.image.load("Labirinto_game/assets/images/fundo_dialogo_labirinto_dark.png").convert_alpha()
        self.fundo = pygame.transform.scale(self.fundo, (LARGURA_TELA, ALTURA_TELA))
        
        if not dark:
            self.personagem = pygame.image.load("Labirinto_game/assets/images/teseu.png").convert_alpha()
            self.personagem = pygame.transform.scale(self.personagem, (resize(800, eh_X=True), resize(800)))
        else:
            self.personagem = pygame.image.load("Labirinto_game/assets/images/teseu_old.png").convert_alpha()
            self.personagem = pygame.transform.scale(self.personagem, (resize(540, eh_X=True), resize(800)))
        
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
                "Conseguimos! O primeiro desafio foi superado, mas sinto que as coisas vão ficar mais difíceis... Senti o chão tremer!",
                "Parece que o Minotauro percebeu nossa presença e está furioso! Ele deve estar balançando o labirinto inteiro para nos dificultar.",
                "Dédalo me alertou sobre isso quando cheguei à ilha. O labirinto foi construído sobre um mecanismo que o Minotauro consegue controlar quando irritado.",
                "Vamos precisar de ainda mais concentração agora. O labirinto vai começar a se mover, tornando nossa jornada muito mais desafiadora.",
                "Não desanime! Com sua ajuda, tenho certeza que vamos conseguir chegar até o Minotauro e acabar com essa ameaça a Creta!"
            ]
        else:
            self.linhas_dialogo = [
                "As paredes tremem... O labirinto inteiro vibra com a fúria de seu mestre. O Minotauro sabe que estamos aqui.",
                "Ele está despertando os mecanismos antigos, as engrenagens escondidas que transformam este lugar em uma armadilha mortal.",
                "Os segredos de Dédalo incluíam isso - um labirinto vivo, que se contorce e muda sob o comando da besta. Ele não nos tornará a próxima refeição fácil.",
                "A partir de agora, nossa jornada será contra um inimigo que controla o próprio terreno, que fará as paredes dançarem para nos confundir.",
                "Mantenha o foco. Nosso anel precisa navegar com ainda mais precisão. O Minotauro pode balançar o labirinto, mas não nossa determinação."
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

    def desenhar(self):
        # Desenha o fundo
        self.tela.blit(self.fundo, (0, 0))
        
        # Desenha o personagem
        self.tela.blit(self.personagem, self.personagem_rect)
        
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
        
        # Desenha a animação de despertar (sobreposição preta)
        if self.despertando:
            superficie_despertar = pygame.Surface((self.largura_tela, self.altura_tela))
            superficie_despertar.fill((0, 0, 0))
            superficie_despertar.set_alpha(self.alpha_despertar)
            self.tela.blit(superficie_despertar, (0, 0))
    
    def executar(self):
        relogio = pygame.time.Clock()
        concluido = False
        
        # Adiciona efeito sonoro de tremor/balançar
        from utils.audio_manager import audio_manager
        audio_manager.play_sound("earthquake")
        
        while not concluido:
            concluido = self.tratar_eventos()
            self.atualizar()
            self.desenhar()
            
            pygame.display.flip()
            relogio.tick(60)
        
        return True
