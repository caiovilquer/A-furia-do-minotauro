import pygame
import sys
import json
import os
from pygame.locals import *
from utils.drawing import aplicar_filtro_cinza_superficie, resize
from constants import LARGURA_TELA, ALTURA_TELA

class GerenciadorDialogos:
    """Classe que gerencia a exibição de diálogos entre personagens."""
    
    def __init__(self, tela, arquivo_json):
        # Inicialização da tela e variáveis
        self.tela = tela
        self.largura_tela = tela.get_width()
        self.altura_tela = tela.get_height()
        
        # Carrega o arquivo JSON com os diálogos
        self.carregar_dialogos(arquivo_json)
        
        # Carrega imagens de fundo
        self.carregar_imagens_fundo()
        
        # Configurações da caixa de diálogo
        self.caixa_dialogo = pygame.Rect(
            resize(self.largura_tela * 0.1, eh_X=True),  # x
            resize(self.altura_tela * 0.7),  # y
            resize(self.largura_tela * 0.6, eh_X=True),  # largura
            resize(self.altura_tela * 0.2)   # altura
        )
        
        # Configurações do cabeçalho do personagem
        self.caixa_personagem = pygame.Rect(
            resize(self.largura_tela * 0.1, eh_X=True),  # x (mesma posição X da caixa de diálogo)
            resize(self.altura_tela * 0.7) - resize(40),  # y (levemente acima da caixa de diálogo)
            resize(200, eh_X=True),  # largura para o nome
            resize(40)   # altura
        )
        
        # Configurações do texto
        self.fonte_texto = pygame.font.Font(None, resize(36))
        self.fonte_personagem = pygame.font.Font(None, resize(40))
        self.cor_texto = (255, 255, 255)
        self.cor_nome_personagem = (255, 220, 100)  # Cor dourada para o nome do personagem
        
        # Variáveis de controle da animação de texto
        self.linha_atual = 0
        self.indice_atual = 0
        self.indice_animacao_texto = 0
        self.velocidade_animacao_texto = 1  # Caracteres por quadro
        self.contador_animacao_texto = 0
        
        # Configurações da animação de aparecimento
        self.alpha_despertar = 255  # Começa com tela preta
        self.velocidade_despertar = 2  # Velocidade da animação
        self.despertando = True
        
        # Indicador de "pressione tecla para continuar"
        self.fonte_indicador = pygame.font.Font(None, resize(24))
        self.texto_indicador = "Pressione qualquer tecla para continuar..."
        
        # Espaçamento entre linhas de texto
        self.espacamento_linhas = resize(30)
        self.max_largura_linha = self.caixa_dialogo.width - resize(40, eh_X=True)
        
        # Personagens e suas imagens
        self.personagens = {}
        self.personagem_atual = None
    
    def carregar_dialogos(self, arquivo_json):
        """Carrega diálogos do arquivo JSON."""
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as f:
                self.dados_dialogos = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar arquivo de diálogos: {e}")
            self.dados_dialogos = {}
    
    def carregar_imagens_fundo(self):
        """Carrega imagens de fundo."""
        # Carrega o fundo
        try:
            fundo_path = "Labirinto_game/assets/images/backgrounds/fundo_dialogo_labirinto_dark.png"
            self.fundo = pygame.image.load(fundo_path).convert_alpha()
            self.fundo = pygame.transform.scale(self.fundo, (LARGURA_TELA, ALTURA_TELA))
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
            self.fundo = None
    
    def carregar_personagem(self, nome, imagem_path):
        """Carrega a imagem de um personagem se ainda não foi carregada."""
        if nome not in self.personagens:
            try:
                # Tenta carregar a imagem do personagem
                imagem = pygame.image.load(os.path.join("Labirinto_game/assets/images/characters", imagem_path)).convert_alpha()
                
                # Define o tamanho padrão para personagens
                tamanho = (resize(800, eh_X=True), resize(800))
                imagem = pygame.transform.scale(imagem, tamanho)
                
                # Define a posição do personagem (centralizado à direita da tela)
                personagem_rect = imagem.get_rect(center=(LARGURA_TELA - resize(500, eh_X=True), ALTURA_TELA - resize(400)))
                
                # Armazena o personagem
                self.personagens[nome] = {
                    'imagem': imagem,
                    'rect': personagem_rect
                }
            except Exception as e:
                print(f"Erro ao carregar imagem do personagem {nome}: {e}")
                # Fallback para personagem não encontrado
                self.personagens[nome] = None
    
    def definir_cena(self, nome_cena):
        """Define a cena de diálogo atual."""
        if nome_cena in self.dados_dialogos:
            self.cena_atual = nome_cena
            self.dialogos_cena = self.dados_dialogos[nome_cena]
            self.linha_atual = 0
            self.indice_atual = 0
            self.indice_animacao_texto = 0
            
            # Verifica se a cena tem conteúdo
            if not self.dialogos_cena:
                print(f"Aviso: A cena '{nome_cena}' não contém diálogos.")
                return False
                
            # Carrega imagens de todos os personagens da cena
            for dialogo in self.dialogos_cena:
                self.carregar_personagem(dialogo['personagem'], dialogo.get('imagem', 'teseu.png'))
                
            # Define o personagem inicial
            if self.dialogos_cena:
                self.personagem_atual = self.dialogos_cena[0]['personagem']
            
            return True
        else:
            print(f"Erro: Cena {nome_cena} não encontrada no arquivo de diálogos.")
            return False
    
    def quebrar_texto(self, texto):
        """Quebra o texto em múltiplas linhas para caber na caixa de diálogo."""
        palavras = texto.split(' ')
        linhas = []
        linha_atual = ''
        
        for palavra in palavras:
            # Testa se a palavra cabe na linha atual
            teste_linha = linha_atual + ' ' + palavra if linha_atual else palavra
            largura_teste = self.fonte_texto.size(teste_linha)[0]
            
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
        """Processa eventos de input do usuário."""
        # Verifica se há diálogos para exibir
        if not hasattr(self, 'dialogos_cena') or not self.dialogos_cena:
            print("Erro: Não há diálogos para exibir")
            return True  # Encerra o diálogo se não houver nada para mostrar
            
        # Verifica se o índice atual é válido
        if self.indice_atual >= len(self.dialogos_cena):
            print(f"Alerta: Índice de diálogo inválido ({self.indice_atual}/{len(self.dialogos_cena)})")
            return True  # Encerra o diálogo quando terminamos todos os textos
            
        for evento in pygame.event.get():
            if evento.type == QUIT:
                pygame.quit()
                sys.exit()
            
            # Eventos de teclado e mouse
            if evento.type == KEYDOWN or evento.type == MOUSEBUTTONDOWN:
                if self.despertando:
                    # Pula animação de aparecimento
                    self.despertando = False
                    self.alpha_despertar = 0
                elif self.indice_atual < len(self.dialogos_cena) and self.indice_animacao_texto < len(self.dialogos_cena[self.indice_atual]['texto']):
                    # Exibe o texto completo instantaneamente
                    self.indice_animacao_texto = len(self.dialogos_cena[self.indice_atual]['texto'])
                else:
                    # Avança para o próximo diálogo
                    self.indice_atual += 1
                    self.indice_animacao_texto = 0
                    
                    # Atualiza o personagem atual
                    if self.indice_atual < len(self.dialogos_cena):
                        self.personagem_atual = self.dialogos_cena[self.indice_atual]['personagem']
                    
                    # Retorna True quando todos os diálogos foram exibidos
                    if self.indice_atual >= len(self.dialogos_cena):
                        return True
        
        return False
        
    def atualizar(self):
        """Atualiza a animação do texto e transições."""
        # Atualiza a animação de despertar
        if self.despertando:
            self.alpha_despertar -= self.velocidade_despertar
            if self.alpha_despertar <= 0:
                self.alpha_despertar = 0
                self.despertando = False
        
        # Atualiza a animação do texto
        if not self.despertando and hasattr(self, 'dialogos_cena') and self.indice_atual < len(self.dialogos_cena):
            self.contador_animacao_texto += 1
            if self.contador_animacao_texto >= self.velocidade_animacao_texto:
                self.contador_animacao_texto = 0
                texto_atual = self.dialogos_cena[self.indice_atual]['texto']
                if self.indice_animacao_texto < len(texto_atual):
                    self.indice_animacao_texto += 1
    
    def desenhar(self):
        """Desenha a cena de diálogo na tela."""
        # Desenha o fundo
        if self.fundo:
            self.tela.blit(self.fundo, (0, 0))
        else:
            # Fallback para fundo preto se a imagem não carregou
            self.tela.fill((0, 0, 0))
        
        # Desenha o personagem atual
        if self.personagem_atual and self.personagem_atual in self.personagens and self.personagens[self.personagem_atual]:
            personagem_info = self.personagens[self.personagem_atual]
            self.tela.blit(personagem_info['imagem'], personagem_info['rect'])
        
        # Desenha a caixa do nome do personagem e texto apenas se houver diálogos
        if hasattr(self, 'dialogos_cena') and self.dialogos_cena and self.indice_atual < len(self.dialogos_cena):
            # Desenha a caixa do nome do personagem
            pygame.draw.rect(self.tela, (50, 50, 70), self.caixa_personagem, border_radius=resize(10))
            pygame.draw.rect(self.tela, (220, 180, 50), self.caixa_personagem, width=2, border_radius=resize(10))
            
            # Desenha o nome do personagem
            if self.personagem_atual:
                nome_texto = self.fonte_personagem.render(self.personagem_atual, True, self.cor_nome_personagem)
                nome_rect = nome_texto.get_rect(center=self.caixa_personagem.center)
                self.tela.blit(nome_texto, nome_rect)
            
            # Desenha a caixa de diálogo (semi-transparente)
            superficie_dialogo = pygame.Surface((self.caixa_dialogo.width, self.caixa_dialogo.height), pygame.SRCALPHA)
            superficie_dialogo.fill((0, 0, 0, 180))  # Preto com transparência
            self.tela.blit(superficie_dialogo, (self.caixa_dialogo.x, self.caixa_dialogo.y))
            
            # Desenha o texto se não estiver despertando e houver diálogos para exibir
            if not self.despertando:
                # Obtém o texto atual para exibir (baseado na animação)
                texto_atual = self.dialogos_cena[self.indice_atual]['texto'][:self.indice_animacao_texto]
                
                # Quebra o texto em múltiplas linhas
                linhas_renderizadas = self.quebrar_texto(texto_atual)
                
                # Renderiza cada linha separadamente
                for idx, linha in enumerate(linhas_renderizadas):
                    superficie_texto = self.fonte_texto.render(linha, True, self.cor_texto)
                    posicao_y = self.caixa_dialogo.y + resize(20) + idx * self.espacamento_linhas
                    self.tela.blit(superficie_texto, (self.caixa_dialogo.x + resize(20, eh_X=True), posicao_y))
                
                # Desenha o indicador "pressione qualquer tecla" se a animação do texto estiver completa
                if self.indice_animacao_texto >= len(self.dialogos_cena[self.indice_atual]['texto']):
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
        
        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(self.tela)
    
    def executar(self, nome_cena=None, efeito_sonoro=None, pular_dialogo=False):
        """Executa a cena de diálogo."""
        # Define a cena se for especificada
        if nome_cena:
            if not self.definir_cena(nome_cena):
                return False  # Sai se a cena não foi encontrada
        
        # Se pular_dialogo for True, pulamos a exibição do diálogo e retornamos sucesso
        if pular_dialogo:
            return True
        
        # Toca efeito sonoro se especificado
        if efeito_sonoro:
            from utils.audio_manager import audio_manager
            audio_manager.play_sound(efeito_sonoro)
        
        # Loop principal da cena
        relogio = pygame.time.Clock()
        concluido = False
        
        while not concluido:
            concluido = self.tratar_eventos()
            self.atualizar()
            self.desenhar()
            
            pygame.display.flip()
            relogio.tick(60)
        # Retorna True para indicar que o diálogo foi concluído com sucesso
        return True
