import pygame
import sys
import math
import os
from constants import *
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie, TransitionEffect
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, set_acessibilidade, get_acessibilidade
from utils.audio_manager import audio_manager

class Slider:
    def __init__(self, x, y, largura, valor_inicial, min_valor, max_valor, cor, nome, fonte, step=0.01, sufixo=""):
        self.rect = pygame.Rect(x, y, largura, resize(16))
        self.valor = valor_inicial
        self.min_valor = min_valor
        self.max_valor = max_valor
        if isinstance(cor, (list, tuple)) and len(cor) >= 3:
            self.cor = (int(cor[0]), int(cor[1]), int(cor[2]))
        else:
            self.cor = (100, 100, 200)  # Cor padrão caso inválida
        
        r, g, b = self.cor
        self.cor_hover = (min(r+40, 255), min(g+40, 255), min(b+40, 255))
        self.cor_handle = (255, 255, 255)
        self.nome = nome
        self.fonte = fonte
        self.step = step
        self.sufixo = sufixo
        self.is_dragging = False
        self.handle_radius = resize(12)
        self.hover = False
        self.touched = False  # Flag para quando o valor foi alterado
        
    def update_valor(self, x_mouse):
        # Calcula o valor baseado na posição do mouse no slider
        rel_x = max(0, min(1, (x_mouse - self.rect.x) / self.rect.width))
        new_valor = self.min_valor + rel_x * (self.max_valor - self.min_valor)
        if self.step:
            new_valor = round(new_valor / self.step) * self.step
        new_valor = max(self.min_valor, min(self.max_valor, new_valor))
        
        if new_valor != self.valor:
            self.touched = True
            self.valor = new_valor
            return True
        return False
    
    def handle_event(self, event, callback=None):
        if event.type == pygame.MOUSEMOTION:
            x, y = event.pos
            self.hover = self.rect.collidepoint(x, y)
            if self.is_dragging:
                valor_changed = self.update_valor(x)
                if valor_changed and callback:
                    callback(self.valor)
                return valor_changed
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo
                x, y = event.pos
                # Verificar se o clique foi no slider
                if self.rect.collidepoint(x, y):
                    self.is_dragging = True
                    valor_changed = self.update_valor(x)
                    if valor_changed and callback:
                        callback(self.valor)
                    return valor_changed
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Botão esquerdo
                self.is_dragging = False
        
        return False
        
    def draw(self, tela):
        # Área de fundo
        track_color = (80, 80, 80)
        if self.hover or self.is_dragging:
            track_color = (100, 100, 100)
            
        pygame.draw.rect(tela, (0, 0, 0, 100), 
                        pygame.Rect(self.rect.x-resize(5, eh_X=True), self.rect.y-resize(10), 
                                   self.rect.width+resize(10, eh_X=True), resize(36)),
                        border_radius=resize(12))
            
        # Desenha a trilha do slider
        pygame.draw.rect(tela, track_color, self.rect, border_radius=resize(8))
        
        # Desenha a parte preenchida
        pos = int((self.valor - self.min_valor) / (self.max_valor - self.min_valor) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, pos, self.rect.height)
        
        # Efeito gradiente no preenchimento 
        r, g, b = self.cor
        for i in range(fill_rect.width):
            if i >= self.rect.width:
                break  # Evitar acesso fora dos limites
                
            progresso = i / max(1, self.rect.width)  # Evitar divisão por zero
            
            # Calcular nova cor com verificação de limites
            cor_atual = (
                max(0, min(255, int(r - 30 + 60 * progresso))),
                max(0, min(255, int(g - 30 + 60 * progresso))),
                max(0, min(255, int(b - 30 + 60 * progresso)))
            )
            
            pygame.draw.line(tela, cor_atual, 
                           (self.rect.x + i, self.rect.y), 
                           (self.rect.x + i, self.rect.y + self.rect.height), 1)
        
        # Borda do slider
        pygame.draw.rect(tela, (150,150,150), self.rect, width=1, border_radius=resize(8))
        

        handle_x = self.rect.x + pos
        handle_y = self.rect.y + self.rect.height // 2
        handle_color = self.cor if not self.hover else self.cor_hover
        
        # Sombra do handle
        pygame.draw.circle(tela, (20, 20, 20, 150), (handle_x+resize(2), handle_y+resize(2)), self.handle_radius)
        
        # Handle principal
        pygame.draw.circle(tela, handle_color, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(tela, self.cor_handle, (handle_x, handle_y), self.handle_radius-resize(4))
        
        # Desenha o texto com formato adequado ao tipo de valor
        if self.step == 1:  # Valores inteiros
            valor_texto = f"{int(self.valor)}{self.sufixo}"
        else:  # Valores decimais
            valor_texto = f"{self.valor:.2f}{self.sufixo}"
            
        texto_completo = f"{self.nome}: {valor_texto}"
        desenhar_texto_sombra(texto_completo, self.fonte, (220, 220, 220), 
                            tela, self.rect.x, self.rect.y - resize(30))


class Checkbox:
    def __init__(self, x, y, checked, nome, fonte):
        self.rect = pygame.Rect(x, y, resize(32), resize(32))
        self.checked = checked
        self.nome = nome
        self.fonte = fonte
        self.hover = False
        self.touched = False  # Flag para quando o valor foi alterado
        
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                self.touched = True
                return True
        return False
        
    def draw(self, tela):
        # Área de fundo
        background_rect = pygame.Rect(
            self.rect.x - resize(5), self.rect.y - resize(5),
            self.rect.width + resize(10), self.rect.height + resize(10)
        )
        pygame.draw.rect(tela, (0, 0, 0, 100), background_rect, border_radius=resize(8))
        
        # Fundo do checkbox
        color = (220, 220, 220) if self.hover else (200, 200, 200)
        pygame.draw.rect(tela, color, self.rect, border_radius=resize(6))
        
        # Se estiver marcado, desenha o checkmark
        if self.checked:
            # Efeito de gradiente para checkmark
            check_color = (0, 200, 0)
            caixa_interior = self.rect.inflate(-resize(8), -resize(8))
            
            # Fundo verde mais escuro
            pygame.draw.rect(tela, (0, 150, 0), caixa_interior, border_radius=resize(4))
            
            # Checkmark branco
            pygame.draw.line(tela, (255, 255, 255), 
                           (self.rect.x + resize(8), self.rect.y + resize(16)), 
                           (self.rect.x + resize(14), self.rect.y + resize(24)), resize(3))
            pygame.draw.line(tela, (255, 255, 255), 
                           (self.rect.x + resize(14), self.rect.y + resize(24)), 
                           (self.rect.x + resize(24), self.rect.y + resize(10)), resize(3))
        
        # Texto descritivo
        desenhar_texto_sombra(self.nome, self.fonte, (220, 220, 220), 
                            tela, self.rect.x + resize(42), self.rect.y + resize(6))


class Selector:
    def __init__(self, x, y, largura, opcoes, indice, nome, fonte):
        self.rect = pygame.Rect(x, y, largura, resize(40))
        self.opcoes = opcoes
        self.indice = indice
        self.nome = nome
        self.fonte = fonte
        self.hover = False
        self.touched = False  # Flag para quando o valor foi alterado
        
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.indice = (self.indice + 1) % len(self.opcoes)
                self.touched = True
                return True
        return False
        
    def draw(self, tela):
        # Área de fundo
        background_rect = pygame.Rect(
            self.rect.x - resize(5), self.rect.y - resize(5),
            self.rect.width + resize(10), self.rect.height + resize(10)
        )
        pygame.draw.rect(tela, (0, 0, 0, 100), background_rect, border_radius=resize(8))
        
        # Fundo do selector
        color = (60, 60, 80) if self.hover else (50, 50, 70)
        pygame.draw.rect(tela, color, self.rect, border_radius=resize(8))
        
        # Bordas laterais para indicar que é clicável
        pygame.draw.line(tela, (150, 150, 200), 
                       (self.rect.x + resize(10, eh_X=True), self.rect.y + resize(10)), 
                       (self.rect.x + resize(20, eh_X=True), self.rect.centery), resize(2))
        pygame.draw.line(tela, (150, 150, 200), 
                       (self.rect.x + resize(20, eh_X=True), self.rect.centery), 
                       (self.rect.x + resize(10, eh_X=True), self.rect.bottom - resize(10)), resize(2))
        
        pygame.draw.line(tela, (150, 150, 200), 
                       (self.rect.right - resize(10, eh_X=True), self.rect.y + resize(10)), 
                       (self.rect.right - resize(20, eh_X=True), self.rect.centery), resize(2))
        pygame.draw.line(tela, (150, 150, 200), 
                       (self.rect.right - resize(20, eh_X=True), self.rect.centery), 
                       (self.rect.right - resize(10, eh_X=True), self.rect.bottom - resize(10)), resize(2))
        
        texto_completo = f"{self.nome}: {self.opcoes[self.indice]}"
        desenhar_texto_sombra(texto_completo, self.fonte, (220, 220, 220), 
                            tela, self.rect.x + resize(50, eh_X=True), self.rect.y + resize(12))

def carregar_icone(nome, tamanho=32):
    """Carrega um ícone da pasta de ícones"""
    caminho = f"Labirinto_game/assets/images/icons/{nome}.png"
    try:
        if os.path.exists(caminho):
            imagem = pygame.image.load(caminho).convert_alpha()
            return pygame.transform.scale(imagem, (resize(tamanho), resize(tamanho)))
    except Exception as e:
        print(f"Erro ao carregar ícone {caminho}: {e}")
    return None

def criar_botao_navegacao(tela, x, y, largura, altura, texto, icone, cor, selecionado, events):
    """Cria um botão de navegação para as abas de opções"""
    hover = False
    mouse_pos = pygame.mouse.get_pos()
    rect = pygame.Rect(x, y, largura, altura)
    hover = rect.collidepoint(mouse_pos)
    
    if selecionado:
        cor_bg = (min(cor[0] + 20, 255), min(cor[1] + 20, 255), min(cor[2] + 20, 255))
        cor_borda = (255, 255, 255)
    elif hover:
        cor_bg = (min(cor[0] + 10, 255), min(cor[1] + 10, 255), min(cor[2] + 10, 255))
        cor_borda = (200, 200, 200)
    else:
        cor_bg = cor
        cor_borda = (120, 120, 120)
    
    pygame.draw.rect(tela, cor_bg, rect, border_radius=resize(10))
    pygame.draw.rect(tela, cor_borda, rect, width=resize(2), border_radius=resize(10))
    
    # Desenha ícone à esquerda, se existir
    if icone:
        tela.blit(icone, (x + resize(10, eh_X=True), y + (altura - icone.get_height()) // 2))
        pos_texto_x = x + resize(50, eh_X=True)
    else:
        pos_texto_x = x + resize(10, eh_X=True)
    
    fonte = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(22))
    desenhar_texto_sombra(texto, fonte, (255, 255, 255), tela, pos_texto_x, y + resize(8))
    
    clicado = False
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if rect.collidepoint(event.pos):
                audio_manager.play_sound("click")
                clicado = True
                break
    
    return clicado

def tela_opcoes_acessibilidade(tela, usuario):
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte = FONTE_TEXTO
    fonte_menor = pygame.font.Font("Labirinto_game/assets/fonts/greek-freak.regular.ttf", resize(30))
    
    # Variável para limitar a frequência dos testes de som
    ultimo_teste_audio = pygame.time.get_ticks()
    
    # Importa diretamente as constantes para poder salvá-las
    import constants
    ESCALA_CINZA = constants.ESCALA_CINZA
    SOM_LIGADO = constants.SOM_LIGADO
    
    icones = {
        "audio": carregar_icone("audio", 32),
        "imagem": carregar_icone("display", 32),
        "jogabilidade": carregar_icone("joystick", 32),
        "feedback": carregar_icone("warning", 32),
        "controle": carregar_icone("controller", 32),
        "texto": carregar_icone("text", 32),
    }
    
    cores_categoria = {
        "audio": (100, 140, 220),
        "imagem": (220, 140, 100),
        "jogabilidade": (100, 180, 100),
        "feedback": (220, 200, 100),
        "controle": (180, 120, 200),
        "texto": (100, 180, 180),
    }
    
    usuarios_data = carregar_usuarios()
    opcoes = get_acessibilidade(usuario, usuarios_data).copy()
    
    # Valores padrão
    defval = lambda k, v: opcoes.setdefault(k, v)
    defval("VOLUME_MUSICA", VOLUME_MUSICA)
    defval("VOLUME_SFX", VOLUME_SFX)
    defval("VOLUME_VOZ", VOLUME_VOZ)
    defval("REDUZIR_FLASHES", REDUZIR_FLASHES)
    defval("SERVO_VELOCIDADE", SERVO_VELOCIDADE)
    defval("NUM_VIDAS", NUM_VIDAS)
    defval("DEBOUNCE_COLISAO_MS", DEBOUNCE_COLISAO_MS)
    defval("MODO_PRATICA", MODO_PRATICA)
    defval("FEEDBACK_CANAL", FEEDBACK_CANAL)
    defval("FEEDBACK_INTENSIDADE", FEEDBACK_INTENSIDADE)
    defval("QUICK_TIME_EVENTS", QUICK_TIME_EVENTS)
    defval("DIALOGO_VELOCIDADE", DIALOGO_VELOCIDADE)
    
    # Define valores para os selects
    servo_opts = ["lento", "normal", "rapido"]
    feedback_opts = ["som", "cor", "led", "multiplo"]
    
    # Posições e dimensões base
    x_central = LARGURA_TELA // 2
    y_base = resize(300)  #
    espac = resize(100)
    largura_slider = resize(500, eh_X=True)
    
    # Categoria inicial selecionada
    categoria_atual = "audio"
    
    # Dicionário com os controles organizados por categoria
    controles_por_categoria = {
        "audio": {
            "sliders": {
                "VOLUME_MUSICA": Slider(x_central - largura_slider//2, y_base + espac, largura_slider, 
                                      opcoes["VOLUME_MUSICA"], 0, 1, cores_categoria["audio"], 
                                      "Volume da Música", fonte_menor, 0.05),
                "VOLUME_SFX": Slider(x_central - largura_slider//2, y_base + espac*2, largura_slider, 
                                   opcoes["VOLUME_SFX"], 0, 1, cores_categoria["audio"], 
                                   "Volume dos Efeitos Sonoros", fonte_menor, 0.05),
                "VOLUME_VOZ": Slider(x_central - largura_slider//2, y_base + espac*3, largura_slider, 
                                   opcoes["VOLUME_VOZ"], 0, 1, cores_categoria["audio"], 
                                   "Volume das Vozes", fonte_menor, 0.05),
            },
            "checkboxes": {
                "SOM_LIGADO": Checkbox(x_central - largura_slider//2, y_base + espac*4 + resize(20), SOM_LIGADO, 
                                     "Ativar Som (Geral)", fonte_menor),
            },
            "selectors": {},
        },
        "imagem": {
            "sliders": {
            },
            "checkboxes": {
                "REDUZIR_FLASHES": Checkbox(x_central - largura_slider//2, y_base + espac//2 + resize(20), opcoes["REDUZIR_FLASHES"], 
                                          "Reduzir Efeitos Visuais (flashes, tremores)", fonte_menor),
                "ESCALA_CINZA": Checkbox(x_central - largura_slider//2, y_base + espac + resize(40), ESCALA_CINZA, 
                                       "Modo Escala de Cinza", fonte_menor),
            },
            "selectors": {},
        },
        "jogabilidade": {
            "sliders": {
                "NUM_VIDAS": Slider(x_central - largura_slider//2, y_base + espac, largura_slider, 
                                  opcoes["NUM_VIDAS"], 1, 5, cores_categoria["jogabilidade"], 
                                  "Número de Vidas", fonte_menor, 1),
                "DEBOUNCE_COLISAO_MS": Slider(x_central - largura_slider//2, y_base + espac*2, largura_slider, 
                                            opcoes["DEBOUNCE_COLISAO_MS"], 50, 1000, 
                                            cores_categoria["jogabilidade"], 
                                            "Tempo de Imunidade após Colisão", fonte_menor, 10, "ms"),
            },
            "checkboxes": {
                "MODO_PRATICA": Checkbox(x_central - largura_slider//2, y_base + espac*3 + resize(20), opcoes["MODO_PRATICA"], 
                                       "Modo Prática (sem timer, vidas infinitas)", fonte_menor),
            },
            "selectors": {},
        },
        "feedback": {
            "sliders": {
                "FEEDBACK_INTENSIDADE": Slider(x_central - largura_slider//2, y_base + espac*2, largura_slider, 
                                             opcoes["FEEDBACK_INTENSIDADE"], 0, 100, 
                                             cores_categoria["feedback"], 
                                             "Intensidade de Feedback", fonte_menor, 1, "%"),
            },
            "checkboxes": {},
            "selectors": {
                "SERVO_VELOCIDADE": Selector(x_central - largura_slider//2, y_base + espac, largura_slider, 
                                          servo_opts, servo_opts.index(opcoes["SERVO_VELOCIDADE"]), 
                                          "Velocidade do Servo", fonte_menor),
                "FEEDBACK_CANAL": Selector(x_central - largura_slider//2, y_base + espac*3, largura_slider, 
                                        feedback_opts, feedback_opts.index(opcoes["FEEDBACK_CANAL"]), 
                                        "Canal de Feedback", fonte_menor),
            },
        },
        "controle": {
            "sliders": {},
            "checkboxes": {
                "QUICK_TIME_EVENTS": Checkbox(x_central - largura_slider//2, y_base + espac, opcoes["QUICK_TIME_EVENTS"], 
                                            "Ativar Eventos de Tempo Rápido (QTE)", fonte_menor),
            },
            "selectors": {},
        },
        "texto": {
            "sliders": {
                "DIALOGO_VELOCIDADE": Slider(x_central - largura_slider//2, y_base + espac, largura_slider, 
                                           opcoes["DIALOGO_VELOCIDADE"], 10, 100, 
                                           cores_categoria["texto"], 
                                           "Velocidade do Texto em Diálogos", fonte_menor, 1, "ms"),
            },
            "checkboxes": {},
            "selectors": {},
        },
    }
    
    
    def salvar_configuracoes():
        """Salva as configurações e aplica ao jogo"""
        for categoria, conteudo in controles_por_categoria.items():
            for key, slider in conteudo["sliders"].items():
                # Não salve UI_ESCALA
                if key == "UI_ESCALA":
                    continue
                opcoes[key] = slider.valor if key != "NUM_VIDAS" else int(slider.valor)
                
            for key, checkbox in conteudo["checkboxes"].items():
                if key == "ESCALA_CINZA":
                    constants.ESCALA_CINZA = checkbox.checked
                    opcoes[key] = checkbox.checked  # Salva na opção do usuário
                elif key == "SOM_LIGADO":
                    constants.SOM_LIGADO = checkbox.checked
                    audio_manager.som_ligado = checkbox.checked
                    opcoes[key] = checkbox.checked  # Salva na opção do usuário
                else:
                    opcoes[key] = checkbox.checked
                
            for key, selector in conteudo["selectors"].items():
                if key == "SERVO_VELOCIDADE":
                    opcoes[key] = servo_opts[selector.indice]
                elif key == "FEEDBACK_CANAL":
                    opcoes[key] = feedback_opts[selector.indice]
        
        # Salva na base de dados do usuário
        set_acessibilidade(usuario, opcoes, usuarios_data)
        
        # Aplica as configurações imediatamente
        audio_manager.set_music_volume(opcoes["VOLUME_MUSICA"])
        audio_manager.set_sfx_volume(opcoes["VOLUME_SFX"])  
        audio_manager.set_voice_volume(opcoes["VOLUME_VOZ"])
    
    running = True
    while running:
        tempo = pygame.time.get_ticks()
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                salvar_configuracoes()
                running = False
            
            # Processa eventos dos controles da categoria atual
            controles_categoria = controles_por_categoria[categoria_atual]
            
            for key, controle in controles_categoria["sliders"].items():
                if controle.handle_event(event, callback=None):
                    # Aplica alterações de volume imediatamente para feedback
                    if key == "VOLUME_MUSICA":
                        audio_manager.set_music_volume(controle.valor)
                    elif key == "VOLUME_SFX":
                        audio_manager.set_sfx_volume(controle.valor)
                        if tempo - ultimo_teste_audio > 300:
                            audio_manager.play_sound("hover")
                            ultimo_teste_audio = tempo
                    elif key == "VOLUME_VOZ":
                        audio_manager.set_voice_volume(controle.valor)
            
            for key, checkbox in controles_categoria["checkboxes"].items():
                if checkbox.handle_event(event):
                    if key == "SOM_LIGADO":
                        audio_manager.som_ligado = checkbox.checked
                        constants.SOM_LIGADO = checkbox.checked
                
            for selector in controles_categoria["selectors"].values():
                selector.handle_event(event)
        
        # Renderização do fundo
        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)
        
        # Painel central semi-transparente
        largura_painel = LARGURA_TELA - resize(200, eh_X=True)
        altura_painel = ALTURA_TELA - resize(200)
        x_painel = (LARGURA_TELA - largura_painel) // 2
        y_painel = (ALTURA_TELA - altura_painel) // 2
        
        # Fundo com gradiente
        painel = pygame.Surface((largura_painel, altura_painel), pygame.SRCALPHA)
        for y in range(altura_painel):
            alpha = 180  
            fator_y = y / altura_painel
            r = int(20 + 20 * fator_y)
            g = int(20 + 20 * fator_y)
            b = int(40 + 30 * fator_y)
            pygame.draw.line(painel, (r, g, b, alpha), (0, y), (largura_painel, y))
        
        # Bordas decorativas
        borda_espessura = resize(4)
        pygame.draw.rect(painel, (0, 0, 0, 0), pygame.Rect(0, 0, largura_painel, altura_painel), border_radius=resize(20))
        
        tela.blit(painel, (x_painel, y_painel))
        
        # Borda dourada
        pygame.draw.rect(tela, cor_com_escala_cinza(255, 215, 0), 
                        pygame.Rect(x_painel, y_painel, largura_painel, altura_painel), 
                        width=borda_espessura, border_radius=resize(20))
        
        # Título principal
        desenhar_texto_sombra("Opções de Acessibilidade", fonte_titulo, COR_TITULO, 
                            tela, x_painel + resize(75, eh_X=True), y_painel + resize(30))
        
        # Calcula espaçamento dos botões de navegação com base no número de categorias
        categorias = list(cores_categoria.keys())
        num_categorias = len(categorias)
        
        # Se temos muitas categorias, ajustamos o tamanho dos botões
        if num_categorias > 5:
            largura_btn = resize(200, eh_X=True)
            espaco_btn = resize(20, eh_X=True)
        else:
            largura_btn = resize(200, eh_X=True)
            espaco_btn = resize(25, eh_X=True)
            
        altura_btn = resize(40)
        
        # Calcula a largura total de todos os botões + espaçamento
        largura_total = num_categorias * largura_btn + (num_categorias-1) * espaco_btn
        
        # Se a largura total ainda for maior que o espaço disponível, organizamos em duas linhas
        largura_disponivel = largura_painel - resize(50, eh_X=True)
        if largura_total > largura_disponivel:
            # Organiza em duas linhas
            categorias_linha1 = categorias[:num_categorias//2]
            categorias_linha2 = categorias[num_categorias//2:]
            
            # Recalcula espaçamento para cada linha
            largura_linha1 = len(categorias_linha1) * largura_btn + (len(categorias_linha1)-1) * espaco_btn
            largura_linha2 = len(categorias_linha2) * largura_btn + (len(categorias_linha2)-1) * espaco_btn
            
            x_inicial_linha1 = x_central - largura_linha1 // 2
            x_inicial_linha2 = x_central - largura_linha2 // 2
            
            for i, cat in enumerate(categorias_linha1):
                x_btn = x_inicial_linha1 + i * (largura_btn + espaco_btn)
                y_btn = y_base - resize(80)  # Primeira linha mais acima
                

                nome_cat = cat.upper()
                cor = cores_categoria[cat]
                
                selecionado = (cat == categoria_atual)
                
                if criar_botao_navegacao(tela, x_btn, y_btn, largura_btn, altura_btn, 
                                       nome_cat, icones[cat], cor, selecionado, events):
                    # Muda para a categoria selecionada
                    categoria_atual = cat
            
            # Segunda linha de botões
            for i, cat in enumerate(categorias_linha2):
                x_btn = x_inicial_linha2 + i * (largura_btn + espaco_btn)
                y_btn = y_base - resize(35)
                
                nome_cat = cat.upper()
                cor = cores_categoria[cat]
                
                selecionado = (cat == categoria_atual)
                
                if criar_botao_navegacao(tela, x_btn, y_btn, largura_btn, altura_btn, 
                                       nome_cat, icones[cat], cor, selecionado, events):
                    categoria_atual = cat
        else:
            x_inicial_btn = x_central - largura_total // 2
            
            for i, cat in enumerate(categorias):
                x_btn = x_inicial_btn + i * (largura_btn + espaco_btn)
                y_btn = y_base - resize(60)
                
                nome_cat = cat.upper()
                cor = cores_categoria[cat]
                
                selecionado = (cat == categoria_atual)
                
                if criar_botao_navegacao(tela, x_btn, y_btn, largura_btn, altura_btn, 
                                       nome_cat, icones[cat], cor, selecionado, events):
                    categoria_atual = cat
                
        # Desenha uma linha divisória após os botões
        y_linha = y_base - resize(10)
        pygame.draw.line(tela, cores_categoria[categoria_atual], 
                       (x_painel + resize(50, eh_X=True), y_linha),
                       (x_painel + largura_painel - resize(50, eh_X=True), y_linha),
                       resize(3))
        
        titulo_cat = f"Configurações de {categoria_atual.capitalize()}"
        texto_width = fonte_menor.size(titulo_cat)[0]
        desenhar_texto_sombra(titulo_cat, fonte_menor, cores_categoria[categoria_atual], 
                            tela, x_central - texto_width//2, y_base - resize(5))
        
        controles = controles_por_categoria[categoria_atual]
        
        if controles["sliders"]:
            for slider in controles["sliders"].values():
                slider.draw(tela)
            
        if controles["checkboxes"]:    
            for checkbox in controles["checkboxes"].values():
                checkbox.draw(tela)
            
        if controles["selectors"]:
            for selector in controles["selectors"].values():
                selector.draw(tela)
        
        descricoes = {
            "audio": "Ajuste os volumes de música, efeitos sonoros e vozes do jogo.",
            "imagem": "Configure a escala da interface, efeitos visuais e modo escala de cinza.",
            "jogabilidade": "Defina o número de vidas, tempo de imunidade e modo de jogo.",
            "feedback": "Controle como o jogo fornece feedback durante a jogabilidade.",
            "controle": "Ajuste as opções de controles e eventos interativos.",
            "texto": "Configure a velocidade de exibição dos textos nos diálogos."
        }
        
        if categoria_atual in descricoes:
            descricao = descricoes[categoria_atual]
            fonte_descricao = pygame.font.Font(None, resize(24))
            # Cria um fundo semitransparente para a descrição
            surf_desc = fonte_descricao.render(descricao, True, (220, 220, 220))
            rect_desc = surf_desc.get_rect(center=(x_central, ALTURA_TELA - resize(250)))
            
            # Fundo com um pouco de transparência
            bg_rect = rect_desc.inflate(resize(20), resize(10))
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 120))
            tela.blit(bg_surface, bg_rect)
            
            # Texto
            tela.blit(surf_desc, rect_desc)
        
        clicou_voltar, _ = desenhar_botao(
            texto="Salvar e Voltar",
            x=LARGURA_TELA//2 - resize(430, eh_X=True),
            y=ALTURA_TELA - resize(120),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        
        clicou_padrao, _ = desenhar_botao(
            texto="Restaurar Padrão",
            x=LARGURA_TELA//2 + resize(40, eh_X=True),
            y=ALTURA_TELA - resize(120),
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(150, 50, 50),
            cor_hover=cor_com_escala_cinza(200, 50, 50),
            fonte=fonte,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        
        if clicou_voltar:
            salvar_configuracoes()
            running = False
            
        if clicou_padrao:
            # Restaura configurações padrão da categoria atual
            for key, slider in controles_por_categoria[categoria_atual]["sliders"].items():
                if key in globals():
                    padrao = globals()[key]
                    slider.valor = padrao
                    
                    # Aplica imediatamente para obter feedback
                    if key == "VOLUME_MUSICA":
                        audio_manager.set_music_volume(padrao)
                    elif key == "VOLUME_SFX":
                        audio_manager.set_sfx_volume(padrao)
                    elif key == "VOLUME_VOZ":
                        audio_manager.set_voice_volume(padrao)
                
            for key, checkbox in controles_por_categoria[categoria_atual]["checkboxes"].items():
                if key in globals():
                    padrao = globals()[key]
                    checkbox.checked = padrao
                    
                    # Aplica alterações de som imediatamente
                    if key == "SOM_LIGADO":
                        constants.SOM_LIGADO = padrao
                        audio_manager.som_ligado = padrao
                    elif key == "ESCALA_CINZA":
                        constants.ESCALA_CINZA = padrao
                
            for key, selector in controles_por_categoria[categoria_atual]["selectors"].items():
                if key == "SERVO_VELOCIDADE" and "SERVO_VELOCIDADE" in globals():
                    selector.indice = servo_opts.index(SERVO_VELOCIDADE)
                elif key == "FEEDBACK_CANAL" and "FEEDBACK_CANAL" in globals():
                    selector.indice = feedback_opts.index(FEEDBACK_CANAL)
            
            # Tocar um som para feedback
            audio_manager.play_sound("click")
        
        # Aplica o filtro de escala de cinza se estiver ativo
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)
            
        pygame.display.update()
    
    TransitionEffect.fade_out(tela, velocidade=10)

def desenhar_secao(tela, texto, icone, cor, x, y):
    """Desenha o cabeçalho de uma seção"""
    fonte_secao = FONTE_BOTAO_REDUZIDA
    
    # Fundo da seção
    fundo_rect = pygame.Rect(x, y, resize(700, eh_X=True), resize(50))
    pygame.draw.rect(tela, (30, 30, 50, 150), fundo_rect, border_radius=resize(25))
    
    # Borda com a cor temática
    pygame.draw.rect(tela, cor, fundo_rect, width=resize(2), border_radius=resize(25))
    
    # Título da seção
    desenhar_texto_sombra(texto, fonte_secao, cor, tela, x + resize(55, eh_X=True), y + resize(10))
    
    # Ícone
    if icone:
        tela.blit(icone, (x + resize(15, eh_X=True), y + resize(8)))
        
    # Linha decorativa à direita
    pygame.draw.line(tela, cor, 
                   (x + resize(270, eh_X=True), y + resize(25)),
                   (x + resize(670, eh_X=True), y + resize(25)),
                   resize(2))
