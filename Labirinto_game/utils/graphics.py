import pygame
import math
from typing import List, Dict, Tuple, Any, Optional

# Cores temáticas da mitologia grega
VERMELHO_MINOTAURO = (180, 40, 40)
DOURADO_ANTIGO = (200, 160, 60)
TERRACOTA = (180, 90, 40)
MARROM_LABIRINTO = (120, 80, 40)
PRETO_TAURINO = (40, 30, 30)

# Elementos gráficos decorativos
def desenhar_colunas_gregas(superficie, rect, cor=(200, 160, 60)):
    """Desenha elementos decorativos no estilo colunas gregas"""
    x, y, largura, altura = rect
    
    # Desenhar topo da coluna (capitel)
    pygame.draw.rect(superficie, cor, (x, y, largura, altura * 0.08), 0, 3)
    pygame.draw.rect(superficie, cor, (x, y + altura * 0.08, largura, altura * 0.04), 0)
    
    # Desenhar base da coluna
    pygame.draw.rect(superficie, cor, (x, y + altura * 0.92, largura, altura * 0.08), 0)
    pygame.draw.rect(superficie, cor, (x, y + altura * 0.88, largura, altura * 0.04), 0)
    
    # Desenhar ranhuras verticais
    num_ranhuras = 5
    ranhura_largura = largura / (num_ranhuras * 2 - 1)
    for i in range(num_ranhuras):
        x_ranhura = x + i * ranhura_largura * 2
        pygame.draw.rect(
            superficie, 
            cor, 
            (x_ranhura, y + altura * 0.12, ranhura_largura, altura * 0.76),
            0
        )

class GraficoBase:
    """Classe base para os gráficos animados"""
    def __init__(
        self,
        pos: Tuple[int, int],
        tamanho: Tuple[int, int],
        titulo: str,
        cor_fundo: Tuple[int, int, int, int] = (40, 30, 30, 180),
        cor_borda: Tuple[int, int, int] = DOURADO_ANTIGO, 
        fonte_titulo=None,
        fonte_eixos=None,
        cor_texto: Tuple[int, int, int] = (220, 220, 220),
    ):
        self.pos = pos
        self.tamanho = tamanho
        self.titulo = titulo
        self.cor_fundo = cor_fundo
        self.cor_borda = cor_borda
        self.cor_texto = cor_texto
        self.fonte_titulo = fonte_titulo or pygame.font.SysFont("arial", 20)
        self.fonte_eixos = fonte_eixos or pygame.font.SysFont("arial", 16)
        self.superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
        self.animacao_progresso = 0.0
        self.velocidade_animacao = 0.03
        self.animacao_completa = False
        
        # Ajustar margens para garantir que os rótulos dos eixos estejam visíveis
        self.margem_inferior_extra = 20  # Pixels extras para acomodar rótulos do eixo X
        self.margem_direita_extra = 10   # Pixels extras para acomodar rótulos do eixo Y
        
    def _desenhar_base(self):
        """Desenha a base do gráfico com fundo, borda e título"""
        # Desenhar fundo com transparência
        pygame.draw.rect(
            self.superficie, 
            self.cor_fundo, 
            (0, 0, self.tamanho[0], self.tamanho[1]), 
            0,
            10  # Border radius
        )
        
        # Adicionar elementos decorativos nas bordas (estilo colunas gregas)
        largura_coluna = 20
        # desenhar_colunas_gregas(
        #     self.superficie,
        #     (5, 5, largura_coluna, self.tamanho[1] - 10),
        #     self.cor_borda
        # )
        # desenhar_colunas_gregas(
        #     self.superficie,
        #     (self.tamanho[0] - largura_coluna - 5, 5, largura_coluna, self.tamanho[1] - 10),
        #     self.cor_borda
        # )
        
        # Desenhar borda
        pygame.draw.rect(
            self.superficie, 
            self.cor_borda, 
            (0, 0, self.tamanho[0], self.tamanho[1]), 
            3,  # Espessura da borda
            10  # Border radius
        )
        
        # Desenhar título com estilo grego
        titulo_surface = self.fonte_titulo.render(self.titulo, True, DOURADO_ANTIGO)
        titulo_rect = titulo_surface.get_rect(midtop=(self.tamanho[0] // 2, 10))
        
        # Fundo do título no estilo mitológico
        pygame.draw.rect(
            self.superficie,
            PRETO_TAURINO,
            (titulo_rect.left - 20, titulo_rect.top - 5, 
             titulo_rect.width + 40, titulo_rect.height + 10),
            0,
            5
        )
        
        # Adicionar borda dourada ao título
        pygame.draw.rect(
            self.superficie,
            DOURADO_ANTIGO,
            (titulo_rect.left - 20, titulo_rect.top - 5, 
             titulo_rect.width + 40, titulo_rect.height + 10),
            2,
            5
        )
        
        self.superficie.blit(titulo_surface, titulo_rect)
    
    def atualizar_animacao(self, dt=1.0):
        """Atualiza o progresso da animação"""
        if not self.animacao_completa:
            self.animacao_progresso += self.velocidade_animacao * dt
            if self.animacao_progresso >= 1.0:
                self.animacao_progresso = 1.0
                self.animacao_completa = True
        return self.animacao_completa
    
    def reiniciar_animacao(self):
        """Reinicia a animação do gráfico"""
        self.animacao_progresso = 0.0
        self.animacao_completa = False
    
    def desenhar(self, superficie_destino):
        """Método a ser sobrescrito pelas subclasses"""
        self.superficie.fill((0, 0, 0, 0))  # Limpar com transparência
        self._desenhar_base()
        superficie_destino.blit(self.superficie, self.pos)


class GraficoLinha(GraficoBase):
    """Gráfico de linha para mostrar evolução temporal"""
    def __init__(
        self,
        pos: Tuple[int, int],
        tamanho: Tuple[int, int],
        dados: List[Dict[str, Any]],
        titulo: str,
        cor_linha: Tuple[int, int, int] = VERMELHO_MINOTAURO,
        grossura_linha: int = 3,
        campo_x: str = "indice",
        campo_y: str = "tempo",
        rotulos_x: Optional[List[str]] = None,
        is_discrete_y: bool = False,  # Novo parâmetro
        **kwargs
    ):
        super().__init__(pos, tamanho, titulo, **kwargs)
        self.dados = dados
        self.cor_linha = cor_linha
        self.grossura_linha = grossura_linha
        self.campo_x = campo_x
        self.campo_y = campo_y
        self.rotulos_x = rotulos_x
        self.is_discrete_y = is_discrete_y # Armazena o novo parâmetro
        
        # Margens para desenho - aumentando a margem inferior para evitar corte dos rótulos
        self.margem_x = 90
        self.margem_y = 60
        self.espaco_rotulos_x = 35  # Espaço extra para os rótulos do eixo X
        self.area_grafico = (
            self.margem_x,
            self.margem_y,
            self.tamanho[0] - self.margem_x * 1.5,
            self.tamanho[1] - self.margem_y * 1.5 - self.espaco_rotulos_x
        )
        
        # Calcular valores máximos e mínimos
        self._calcular_limites()
        
    def _calcular_limites(self):
        """Calcula os valores máximos e mínimos para os eixos"""
        if not self.dados:
            self.max_y = 10 if not self.is_discrete_y else 5
            self.min_y = 0
            return
            
        self.max_y = max([d[self.campo_y] for d in self.dados]) if self.dados else (1 if not self.is_discrete_y else 1)
        self.min_y = min([d[self.campo_y] for d in self.dados]) if self.dados else 0
        
        if self.is_discrete_y:
            self.min_y = math.floor(self.min_y)
            self.max_y = math.ceil(self.max_y)
            if self.max_y == self.min_y: # Caso todos os valores sejam iguais
                self.max_y = self.min_y + 1 
            if self.max_y == 0: # Caso todos os valores sejam 0
                self.max_y = 1 # Mostrar pelo menos até 1
        else:
            # Ajustar para ter um pouco de espaço nas bordas
            range_y = self.max_y - self.min_y
            if range_y == 0:
                range_y = 1  # Evitar divisão por zero
            self.min_y = max(0, self.min_y - range_y * 0.1)
            self.max_y = self.max_y + range_y * 0.1
        
    def _transformar_ponto(self, x_idx, y_valor):
        """Transforma coordenadas de dados em coordenadas de tela"""
        x_norm = x_idx / (len(self.dados) - 1) if len(self.dados) > 1 else 0.5
        y_norm = 1 - ((y_valor - self.min_y) / (self.max_y - self.min_y)) if self.max_y != self.min_y else 0.5
        
        x_pixel = self.area_grafico[0] + x_norm * self.area_grafico[2]
        y_pixel = self.area_grafico[1] + y_norm * self.area_grafico[3]
        
        return x_pixel, y_pixel
    
    def _desenhar_eixos(self):
        """Desenha os eixos X e Y com rotulações"""
        # Eixo X
        pygame.draw.line(
            self.superficie,
            self.cor_borda,
            (self.area_grafico[0], self.area_grafico[1] + self.area_grafico[3]),
            (self.area_grafico[0] + self.area_grafico[2], self.area_grafico[1] + self.area_grafico[3]),
            2
        )
        
        # Linhas de grade X (verticais)
        num_linhas_x = 5
        for i in range(1, num_linhas_x):
            x = self.area_grafico[0] + (self.area_grafico[2] * i / num_linhas_x)
            pygame.draw.line(
                self.superficie,
                (100, 100, 100, 50),  # Cinza semi-transparente
                (x, self.area_grafico[1]),
                (x, self.area_grafico[1] + self.area_grafico[3]),
                1
            )
        
        # Eixo Y
        pygame.draw.line(
            self.superficie,
            self.cor_borda,
            (self.area_grafico[0], self.area_grafico[1]),
            (self.area_grafico[0], self.area_grafico[1] + self.area_grafico[3]),
            2
        )
        
        # Linhas de grade Y (horizontais)
        num_linhas_y = 5
        for i in range(1, num_linhas_y):
            y = self.area_grafico[1] + (self.area_grafico[3] * i / num_linhas_y)
            pygame.draw.line(
                self.superficie,
                (100, 100, 100, 50),  # Cinza semi-transparente
                (self.area_grafico[0], y),
                (self.area_grafico[0] + self.area_grafico[2], y),
                1
            )
        
        # Rotular eixo Y (valores)
        num_marcas_y = 5
        if self.is_discrete_y:
            # Ajustar número de marcas para valores discretos para tentar ter rótulos inteiros
            if self.max_y - self.min_y > 0 and self.max_y - self.min_y <= 5:
                num_marcas_y = int(self.max_y - self.min_y)
            elif self.max_y - self.min_y == 0: # Caso min_y e max_y sejam iguais (e.g. todos 0)
                 num_marcas_y = 1 # Mostrar pelo menos uma marca
            if num_marcas_y == 0: num_marcas_y = 1


        for i in range(num_marcas_y + 1):
            y_valor_ratio = i / num_marcas_y if num_marcas_y > 0 else 0
            y_valor = self.min_y + (self.max_y - self.min_y) * y_valor_ratio
            y_pos = self.area_grafico[1] + self.area_grafico[3] * (1 - y_valor_ratio)
            
            # Marca no eixo
            pygame.draw.line(
                self.superficie,
                self.cor_borda,
                (self.area_grafico[0] - 5, y_pos),
                (self.area_grafico[0], y_pos),
                2
            )
            
            # Texto do valor
            texto = f"{y_valor:.0f}" if self.is_discrete_y else f"{y_valor:.1f}"
            texto_surf = self.fonte_eixos.render(texto, True, self.cor_texto)
            texto_rect = texto_surf.get_rect(
                midright=(self.area_grafico[0] - 10, y_pos)
            )
            self.superficie.blit(texto_surf, texto_rect)
        
        # Rotular eixo X (índices ou rótulos personalizados)
        if len(self.dados) > 1:
            # Limitar número de rótulos baseado no espaço disponível
            espaco_min_rotulos = 80  # Espaço mínimo entre rótulos em pixels
            num_rotulos_possiveis = max(2, int(self.area_grafico[2] / espaco_min_rotulos))
            num_indices = min(len(self.dados), num_rotulos_possiveis)
            
            # Selecionar pontos uniformemente distribuídos para rotular
            indices_para_mostrar = []
            if num_indices <= 2:
                indices_para_mostrar = [0, len(self.dados) - 1] if len(self.dados) > 1 else [0]
            else:
                for i in range(num_indices):
                    idx = int(i * (len(self.dados) - 1) / (num_indices - 1))
                    indices_para_mostrar.append(idx)
            
            for idx in indices_para_mostrar:
                x_pos, _ = self._transformar_ponto(idx, self.min_y)
                
                # Marca no eixo
                pygame.draw.line(
                    self.superficie,
                    self.cor_borda,
                    (x_pos, self.area_grafico[1] + self.area_grafico[3]),
                    (x_pos, self.area_grafico[1] + self.area_grafico[3] + 5),
                    2
                )
                
                # Texto do índice ou rótulo
                if self.rotulos_x and idx < len(self.rotulos_x):
                    texto = str(self.rotulos_x[idx])
                    # Truncar textos muito longos para evitar sobreposição
                    if len(texto) > 10:
                        texto = texto[:8] + "..."
                else:
                    texto = str(idx + 1)  # +1 para base 1 (mais natural para usuários)
                
                texto_surf = self.fonte_eixos.render(texto, True, self.cor_texto)
                texto_rect = texto_surf.get_rect(
                    midtop=(x_pos, self.area_grafico[1] + self.area_grafico[3] + 10)
                )
                
                # Garantir que o texto não ultrapasse as bordas do gráfico
                if texto_rect.left < 0:
                    texto_rect.left = 0
                if texto_rect.right > self.tamanho[0]:
                    texto_rect.right = self.tamanho[0]
                    
                self.superficie.blit(texto_surf , texto_rect)
    
    def desenhar(self, superficie_destino):
        """Desenha o gráfico de linha com animação"""
        self.superficie.fill((0, 0, 0, 0))  # Limpar com transparência
        self._desenhar_base()
        self._desenhar_eixos()
        
        # Desenhar linha do gráfico com animação
        if self.dados and len(self.dados) > 1:
            # Determinar quantos pontos desenhar com base no progresso da animação
            pontos_para_desenhar = max(2, int(len(self.dados) * self.animacao_progresso))
            
            # Gerar pontos para a linha
            pontos = []
            for i in range(pontos_para_desenhar):
                x_pixel, y_pixel = self._transformar_ponto(
                    i, self.dados[i][self.campo_y]
                )
                pontos.append((x_pixel, y_pixel))
            
            # Desenhar linha contínua
            if len(pontos) >= 2:
                # Desenhar sombra da linha para efeito de profundidade
                pontos_sombra = [(p[0]+3, p[1]+3) for p in pontos]
                pygame.draw.lines(
                    self.superficie,
                    (0, 0, 0, 120),  # Sombra semi-transparente
                    False,
                    pontos_sombra,
                    self.grossura_linha
                )
                
                # Desenhar linha principal
                pygame.draw.lines(
                    self.superficie,
                    self.cor_linha,
                    False,
                    pontos,
                    self.grossura_linha
                )
                
                # Adicionar pontos de destaque com decoração grega
                for ponto in pontos:
                    # Círculo externo (dourado)
                    pygame.draw.circle(
                        self.superficie,
                        DOURADO_ANTIGO,
                        ponto,
                        self.grossura_linha + 4
                    )
                    # Círculo interno (vermelho)
                    pygame.draw.circle(
                        self.superficie,
                        self.cor_linha,
                        ponto,
                        self.grossura_linha + 2
                    )
                    # Ponto central (dourado)
                    pygame.draw.circle(
                        self.superficie,
                        DOURADO_ANTIGO,
                        ponto,
                        self.grossura_linha - 1
                    )
        
        # Desenhar visualização "alvo" se a animação não estiver completa
        if not self.animacao_completa and len(self.dados) > 1:
            # Desenhar linha pontilhada para mostrar o destino
            pontos = []
            for i in range(len(self.dados)):
                x_pixel, y_pixel = self._transformar_ponto(
                    i, self.dados[i][self.campo_y]
                )
                pontos.append((x_pixel, y_pixel))
            
            # Desenhar linha pontilhada como referência
            if len(pontos) >= 2:
                for i in range(1, len(pontos)):
                    pygame.draw.line(
                        self.superficie,
                        (self.cor_linha[0], self.cor_linha[1], self.cor_linha[2], 50),  # Semi-transparente
                        pontos[i-1],
                        pontos[i],
                        1  # Linha fina
                    )
        
        superficie_destino.blit(self.superficie, self.pos)


class GraficoBarras(GraficoBase):
    """Gráfico de barras para comparar valores"""
    def __init__(
        self,
        pos: Tuple[int, int],
        tamanho: Tuple[int, int],
        dados: List[Dict[str, Any]],
        titulo: str,
        cor_barras: List[Tuple[int, int, int]] = None,
        campo_valor: str = "tempo",
        campo_rotulo: str = "nivel",
        espaco_barras: float = 0.2,  # Espaço entre barras como fração da largura da barra
        is_discrete_y: bool = False,  # Novo parâmetro
        **kwargs
    ):
        super().__init__(pos, tamanho, titulo, **kwargs)
        self.dados = dados
        self.campo_valor = campo_valor
        self.campo_rotulo = campo_rotulo
        self.espaco_barras = espaco_barras
        self.is_discrete_y = is_discrete_y # Armazena o novo parâmetro
        
        # Determinar cores para as barras
        self.cor_barras = cor_barras or [
            VERMELHO_MINOTAURO,   # Vermelho temático
            DOURADO_ANTIGO,       # Dourado antigo
            TERRACOTA,            # Terracota
            MARROM_LABIRINTO,     # Marrom temático
            (150, 30, 30)         # Vermelho escuro
        ]
        
        # Margens para desenho
        self.margem_x = 90
        self.margem_y = 60
        self.espaco_rotulos_x = 35  # Espaço extra para os rótulos do eixo X
        self.area_grafico = (
            self.margem_x,
            self.margem_y,
            self.tamanho[0] - self.margem_x * 1.5,
            self.tamanho[1] - self.margem_y * 1.5 - self.espaco_rotulos_x
        )
        
        
        # Calcular valores máximos
        self._calcular_limites()
        
    def _calcular_limites(self):
        """Calcula os valores máximos para o eixo Y"""
        if not self.dados:
            self.max_y = 10 if not self.is_discrete_y else 5
            return
            
        self.max_y = max([d[self.campo_valor] for d in self.dados]) if self.dados else (1 if not self.is_discrete_y else 1)
        
        if self.is_discrete_y:
            self.max_y = math.ceil(self.max_y)
            if self.max_y == 0: # Caso todos os valores sejam 0
                self.max_y = 1 # Mostrar pelo menos até 1
        else:
            # Ajustar para ter um pouco de espaço nas bordas
            self.max_y = self.max_y * 1.1
        
    def _calcular_largura_barra(self):
        """Calcula a largura de cada barra"""
        num_barras = len(self.dados)
        espaco_total = self.area_grafico[2]
        
        # Ajustar para espaços entre barras
        if num_barras <= 1:
            return espaco_total * 0.5  # Uma barra única centralizada
            
        largura_com_espaco = espaco_total / num_barras
        return largura_com_espaco * (1 - self.espaco_barras)
    
    def _desenhar_eixos(self):
        """Desenha os eixos X e Y com rotulações"""
        # Eixo X
        pygame.draw.line(
            self.superficie,
            self.cor_borda,
            (self.area_grafico[0], self.area_grafico[1] + self.area_grafico[3]),
            (self.area_grafico[0] + self.area_grafico[2], self.area_grafico[1] + self.area_grafico[3]),
            2
        )
        
        # Eixo Y
        pygame.draw.line(
            self.superficie,
            self.cor_borda,
            (self.area_grafico[0], self.area_grafico[1]),
            (self.area_grafico[0], self.area_grafico[1] + self.area_grafico[3]),
            2
        )
        
        # Linhas de grade Y (horizontais)
        num_linhas_y = 5
        for i in range(1, num_linhas_y):
            y = self.area_grafico[1] + (self.area_grafico[3] * i / num_linhas_y)
            pygame.draw.line(
                self.superficie,
                (100, 100, 100, 50),  # Cinza semi-transparente
                (self.area_grafico[0], y),
                (self.area_grafico[0] + self.area_grafico[2], y),
                1
            )
        
        # Rotular eixo Y (valores)
        num_marcas_y = 5
        min_y_display = 0 # Para barras, o mínimo é sempre 0
        
        if self.is_discrete_y:
            if self.max_y - min_y_display > 0 and self.max_y - min_y_display <= 5:
                num_marcas_y = int(self.max_y - min_y_display)
            elif self.max_y - min_y_display == 0:
                 num_marcas_y = 1
            if num_marcas_y == 0: num_marcas_y = 1

        for i in range(num_marcas_y + 1):
            y_valor_ratio = i / num_marcas_y if num_marcas_y > 0 else 0
            y_valor = min_y_display + (self.max_y - min_y_display) * y_valor_ratio
            y_pos = self.area_grafico[1] + self.area_grafico[3] * (1 - y_valor_ratio)
            
            # Marca no eixo
            pygame.draw.line(
                self.superficie,
                self.cor_borda,
                (self.area_grafico[0] - 5, y_pos),
                (self.area_grafico[0], y_pos),
                2
            )
            
            # Texto do valor
            texto = f"{y_valor:.0f}" if self.is_discrete_y else f"{y_valor:.1f}"
            texto_surf = self.fonte_eixos.render(texto, True, self.cor_texto)
            texto_rect = texto_surf.get_rect(
                midright=(self.area_grafico[0] - 10, y_pos)
            )
            self.superficie.blit(texto_surf, texto_rect)
    
    def desenhar(self, superficie_destino):
        """Desenha o gráfico de barras com animação"""
        self.superficie.fill((0, 0, 0, 0))  # Limpar com transparência
        self._desenhar_base()
        self._desenhar_eixos()
        
        if not self.dados:
            texto_surf = self.fonte_eixos.render("Sem dados para exibir", True, self.cor_texto)
            texto_rect = texto_surf.get_rect(center=(self.tamanho[0]/2, self.tamanho[1]/2))
            self.superficie.blit(texto_surf, texto_rect)
            superficie_destino.blit(self.superficie, self.pos)
            return
        
        # Calcular largura das barras
        largura_barra = self._calcular_largura_barra()
        espaco_total_por_barra = largura_barra / (1 - self.espaco_barras)
        
        # Desenhar barras com animação
        for i, dado in enumerate(self.dados):
            # Calcular posição da barra
            x_centro = self.area_grafico[0] + i * espaco_total_por_barra + espaco_total_por_barra / 2
            x_barra = x_centro - largura_barra / 2
            
            valor = dado[self.campo_valor]
            altura_maxima = self.area_grafico[3] * (valor / self.max_y)
            
            # Aplicar animação (altura cresce progressivamente)
            altura_atual = altura_maxima * self.animacao_progresso
            
            # Desenhar barra
            cor_idx = i % len(self.cor_barras)
            cor = self.cor_barras[cor_idx]
            
            # Desenhar sombra da barra para efeito 3D
            pygame.draw.rect(
                self.superficie,
                (30, 30, 30, 150),  # Sombra semi-transparente
                (
                    x_barra + 3,
                    self.area_grafico[1] + self.area_grafico[3] - altura_atual + 3,
                    largura_barra,
                    altura_atual
                ),
                0,  # Preenchido
                5   # Border radius
            )
            
            # Desenhar barra principal com gradiente de cor
            y_topo = self.area_grafico[1] + self.area_grafico[3] - altura_atual
            
            # Desenhar retângulo principal
            pygame.draw.rect(
                self.superficie,
                cor,
                (
                    x_barra,
                    y_topo,
                    largura_barra,
                    altura_atual
                ),
                0,  # Preenchido
                5   # Border radius
            )
            
            # Adicionar detalhes de estilo grego (ranhuras horizontais)
            num_ranhuras = min(int(altura_atual / 10), 8)
            if num_ranhuras > 2:
                for j in range(num_ranhuras):
                    y_ranhura = y_topo + j * (altura_atual / num_ranhuras)
                    pygame.draw.line(
                        self.superficie,
                        (255, 255, 255, 40),  # Branco semi-transparente
                        (x_barra + 2, y_ranhura),
                        (x_barra + largura_barra - 2, y_ranhura),
                        1
                    )
            
            # Desenhar contorno da barra
            pygame.draw.rect(
                self.superficie,
                DOURADO_ANTIGO,  # Contorno dourado
                (
                    x_barra,
                    y_topo,
                    largura_barra,
                    altura_atual
                ),
                2,  # Espessura do contorno
                5   # Border radius
            )
            
            # Desenhar valor na barra
            if self.animacao_progresso > 0.5:  # Mostrar valores apenas depois que a barra já cresceu um pouco
                texto = f"{valor:.0f}" if self.is_discrete_y else f"{valor:.1f}"
                texto_surf = self.fonte_eixos.render(texto, True, (255, 255, 255))
                texto_rect = texto_surf.get_rect(
                    midbottom=(
                        x_centro,
                        y_topo - 5
                    )
                )
                
                # Desenhar fundo para o texto (para melhorar legibilidade)
                pygame.draw.rect(
                    self.superficie,
                    (0, 0, 0, 150),
                    (texto_rect.left - 2, texto_rect.top - 2, 
                     texto_rect.width + 4, texto_rect.height + 4),
                    0,
                    3
                )
                
                self.superficie.blit(texto_surf, texto_rect)
            
            # Desenhar rótulo abaixo da barra
            if self.campo_rotulo in dado:
                rotulo = str(dado[self.campo_rotulo])
                texto_surf = self.fonte_eixos.render(rotulo, True, self.cor_texto)
                texto_rect = texto_surf.get_rect(
                    midtop=(
                        x_centro,
                        self.area_grafico[1] + self.area_grafico[3] + 10
                    )
                )
                self.superficie.blit(texto_surf, texto_rect)
        
        superficie_destino.blit(self.superficie, self.pos)
