import pygame
import sys
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios
from utils.graphics import GraficoLinha, GraficoBarras, VERMELHO_MINOTAURO, DOURADO_ANTIGO, TERRACOTA

def tela_desempenho(tela, usuario):
    """Tela de desempenho do usuário com gráficos animados."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_texto = FONTE_TEXTO
    fonte_botao = FONTE_BOTAO

    usuarios_data = carregar_usuarios()
    nivel = usuarios_data[usuario].get("nivel", 1)
    tentativas = usuarios_data[usuario].get("tentativas", [])

    niveis_jogados = sorted(set(t["nivel"] for t in tentativas))
    if not niveis_jogados:
        niveis_jogados = [1]

    indice_nivel_selecionado = 0

    def mostrar_tentativas_nivel(nivel_escolhido):
        all_t = [t for t in tentativas if t["nivel"] == nivel_escolhido]
        return all_t

    titulo_x = resize(100, eh_X=True)
    titulo_y = resize(50)
    
    # Inicialização dos gráficos animados
    fonte_grafico = pygame.font.SysFont("arial", resize(24))
    fonte_titulo_grafico = pygame.font.SysFont("arial", resize(30))
    
    # Definir dados iniciais para os gráficos
    dados_grafico_tentativas = []
    dados_grafico_colisoes = []
    
    # Flag para indicar quando os gráficos devem ser atualizados
    atualizar_graficos = True
    
    # Criar instâncias dos gráficos
    grafico_linha = None
    grafico_tentativas = None
    grafico_colisoes = None
    grafico_colisoes_tentativa = None
    
    # Aba selecionada
    # 0 = Tempo médio por fase
    # 1 = Tempo por tentativa em nível (Linha)
    # 2 = Colisões por nível (Barras - Média)
    # 3 = Colisões por tentativa em nível (Linha)
    aba_selecionada = 0
    tabs = ["Tempo Médio/Fase", "Tempo/Tentativa", "Média Colisões/Nível", "Colisões/Tentativa",]
    
    # Sistema de paginação para estatísticas detalhadas
    pagina_atual = 0
    tentativas_por_pagina = 5  # Número de tentativas exibidas por página

    while True:
        events = pygame.event.get()
        dt = clock.tick(FPS) / 10  # Normaliza o tempo para animações
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        # Título principal
        desenhar_texto_sombra(f"Desempenho de {usuario}", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        desenhar_texto_sombra(f"Nível atual: {nivel}", fonte_texto, COR_TEXTO, tela, titulo_x + resize(10), resize(140))
        
        # Abas para diferentes visualizações de gráficos - Ajustar largura para 5 abas
        tab_width = resize(400, eh_X=True) 
        tab_height = resize(50)
        tab_y = resize(170)
        
        for i, tab_text in enumerate(tabs):
            tab_x = resize(100, eh_X=True) + i * (tab_width + resize(15, eh_X=True)) # Espaçamento ajustado
            
            # Determina cor da aba (selecionada ou não)
            tab_color = cor_com_escala_cinza(180, 140, 60) if i == aba_selecionada else cor_com_escala_cinza(100, 100, 100)
            hover_color = cor_com_escala_cinza(220, 180, 80) if i == aba_selecionada else cor_com_escala_cinza(150, 150, 150)
            
            clicou_tab, _ = desenhar_botao(
                texto=tab_text,
                x=tab_x,
                y=tab_y,
                largura=tab_width,
                altura=tab_height,
                cor_normal=tab_color,
                cor_hover=hover_color,
                fonte=fonte_texto,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(10)
            )
            
            if clicou_tab:
                aba_selecionada = i
                atualizar_graficos = True
                pagina_atual = 0  # Reset da página ao trocar de visualização
        
        # Área para navegação entre níveis - apenas quando necessário (não mostrar no gráfico de tempo médio por fase e média de colisões por nível)
        if aba_selecionada in [1, 3, 4]:  # Se for "Tempo por Tentativa", "Colisões/Tentativa (Linha)" ou "Colisões/Tentativa (Barras)"
            nivel_y = resize(250)
            clicou_ant, _ = desenhar_botao(
                texto="<",
                x=resize(100, eh_X=True),
                y=nivel_y,
                largura=resize(80, eh_X=True),
                altura=resize(80),
                cor_normal=cor_com_escala_cinza(150,150,150),
                cor_hover=cor_com_escala_cinza(200,200,200),
                fonte=pygame.font.SysFont("arial", resize(50, eh_X=True)),
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(40)
            )
            if clicou_ant:
                indice_nivel_selecionado -= 1
                if indice_nivel_selecionado < 0:
                    indice_nivel_selecionado = 0
                atualizar_graficos = True
                pagina_atual = 0

            clicou_prox, _ = desenhar_botao(
                texto=">",
                x=resize(220, eh_X=True),
                y=nivel_y,
                largura=resize(80, eh_X=True),
                altura=resize(80),
                cor_normal=cor_com_escala_cinza(150,150,150),
                cor_hover=cor_com_escala_cinza(200,200,200),
                fonte=pygame.font.SysFont("arial", resize(50, eh_X=True)),
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(40)
            )
            if clicou_prox:
                indice_nivel_selecionado += 1
                if indice_nivel_selecionado >= len(niveis_jogados):
                    indice_nivel_selecionado = len(niveis_jogados) - 1
                atualizar_graficos = True
                pagina_atual = 0

            nivel_escolhido = niveis_jogados[indice_nivel_selecionado]
            desenhar_texto(f"Nível escolhido: {nivel_escolhido}", fonte_texto, COR_TEXTO, tela, resize(320, eh_X=True), nivel_y + resize(30))

        # Atualizar dados dos gráficos quando necessário
        if atualizar_graficos:
            if aba_selecionada == 0: 
                # Tempo médio por fase - APENAS tentativas bem-sucedidas
                dados_grafico_tempo_medio = []
                for n in sorted(niveis_jogados):
                    # Filtrar apenas tentativas bem-sucedidas (vidas > 0)
                    tentativas_n = [t for t in tentativas if t["nivel"] == n and t["vidas"] > 0]
                    if tentativas_n:
                        tempo_medio = sum(t["tempo"] for t in tentativas_n) / len(tentativas_n)
                        dados_grafico_tempo_medio.append({
                            "nivel": n, 
                            "tempo": tempo_medio, 
                            "rotulo": f"Nível {n}"
                        })
                
    
                grafico_linha = GraficoBarras(
                    pos=(resize(100, eh_X=True), resize(240)),
                    tamanho=(LARGURA_TELA - resize(200, eh_X=True), resize(380)),
                    dados=dados_grafico_tempo_medio,
                    titulo="Tempo Médio por Fase (segundos)",
                    cor_barras=[VERMELHO_MINOTAURO, DOURADO_ANTIGO, TERRACOTA],
                    campo_valor="tempo",
                    campo_rotulo="rotulo",
                    fonte_titulo=fonte_titulo_grafico,
                    fonte_eixos=fonte_grafico,
                    is_discrete_y=False 
                )
                grafico_linha.reiniciar_animacao()
                
            elif aba_selecionada == 1:  
                nivel_escolhido = niveis_jogados[indice_nivel_selecionado]
                # Obtém apenas as tentativas bem-sucedidas deste nível em ordem cronológica
                tentativas_nivel = sorted(
                    [t for t in tentativas if t["nivel"] == nivel_escolhido and t["vidas"] > 0], 
                    key=lambda x: x["timestamp"]
                )
                
                dados_grafico_tentativas = []
                for i, t in enumerate(tentativas_nivel):
                    # Adicionar conector visual (nome da tentativa) para marcar tentativas não concluídas
                    status = "OK" if t["vidas"] > 0 else "FALHA"
                    rotulo = f"{i+1} {status}"
                    dados_grafico_tentativas.append({
                        "indice": i,
                        "tempo": t["tempo"], 
                        "rotulo": rotulo
                    })
                
                grafico_tentativas = GraficoLinha(
                    pos=(resize(100, eh_X=True), resize(350)),
                    tamanho=(LARGURA_TELA - resize(200, eh_X=True), resize(300)), 
                    dados=dados_grafico_tentativas,
                    titulo=f"Tempo em Cada Tentativa do Nível {nivel_escolhido} (segundos)",
                    cor_linha=DOURADO_ANTIGO,
                    grossura_linha=4,
                    campo_x="indice",
                    campo_y="tempo",
                    rotulos_x=[d["rotulo"] for d in dados_grafico_tentativas],
                    fonte_titulo=fonte_titulo_grafico,
                    fonte_eixos=fonte_grafico,
                    is_discrete_y=False 
                )
                grafico_tentativas.reiniciar_animacao()
                
            elif aba_selecionada == 2:  
                # Média de colisões por nível - INCLUINDO tentativas falhas
                dados_grafico_colisoes = []
                for n in sorted(niveis_jogados):
                    # Pega TODAS as tentativas deste nível (incluindo falhas)
                    tentativas_n = [t for t in tentativas if t["nivel"] == n]
                    if tentativas_n:
                        colisoes = [t.get("colisoes", 0) for t in tentativas_n]
                        colisoes_media = sum(colisoes) / len(colisoes) if colisoes else 0
                        dados_grafico_colisoes.append({
                            "nivel": n, 
                            "colisoes": colisoes_media, 
                            "rotulo": f"Nível {n}"
                        })
                
                grafico_colisoes = GraficoBarras(
                    pos=(resize(100, eh_X=True), resize(240)),
                    tamanho=(LARGURA_TELA - resize(200, eh_X=True), resize(380)), 
                    dados=dados_grafico_colisoes,
                    titulo="Média de Colisões por Nível",
                    cor_barras=[TERRACOTA, VERMELHO_MINOTAURO, DOURADO_ANTIGO],
                    campo_valor="colisoes",
                    campo_rotulo="rotulo",
                    fonte_titulo=fonte_titulo_grafico,
                    fonte_eixos=fonte_grafico,
                    is_discrete_y=False 
                )
                grafico_colisoes.reiniciar_animacao()
            
            elif aba_selecionada == 3:
                nivel_escolhido = niveis_jogados[indice_nivel_selecionado]

                # Incluir TODAS as tentativas neste nível (incluindo falhas)
                tentativas_nivel = sorted(
                    [t for t in tentativas if t["nivel"] == nivel_escolhido], 
                    key=lambda x: x["timestamp"]
                )
                
                dados_grafico_colisoes_tentativa = []
                for i, t in enumerate(tentativas_nivel):
                    # Adicionar conector visual (nome da tentativa) para marcar tentativas não concluídas
                    status = "OK" if t["vidas"] > 0 else "FALHA"
                    rotulo = f"{i+1} {status}"
                    dados_grafico_colisoes_tentativa.append({
                        "indice": i,
                        "colisoes": t.get("colisoes", 0), 
                        "rotulo": rotulo
                    })
                
                grafico_colisoes_tentativa = GraficoLinha(
                    pos=(resize(100, eh_X=True), resize(350)),
                    tamanho=(LARGURA_TELA - resize(200, eh_X=True), resize(300)),
                    dados=dados_grafico_colisoes_tentativa,
                    titulo=f"Colisões/Tentativa Nível {nivel_escolhido} (Linha)",
                    cor_linha=TERRACOTA,
                    grossura_linha=4,
                    campo_x="indice",
                    campo_y="colisoes",
                    rotulos_x=[d["rotulo"] for d in dados_grafico_colisoes_tentativa],
                    fonte_titulo=fonte_titulo_grafico,
                    fonte_eixos=fonte_grafico,
                    is_discrete_y=True # Colisões são discretas
                )
                grafico_colisoes_tentativa.reiniciar_animacao()
            
            atualizar_graficos = False
        
        # Desenhar e atualizar gráficos
        if aba_selecionada == 0 and grafico_linha:
            grafico_linha.atualizar_animacao(dt)
            grafico_linha.desenhar(tela)
        elif aba_selecionada == 1 and grafico_tentativas:
            grafico_tentativas.atualizar_animacao(dt)
            grafico_tentativas.desenhar(tela)
        elif aba_selecionada == 2 and grafico_colisoes:
            grafico_colisoes.atualizar_animacao(dt)
            grafico_colisoes.desenhar(tela)
        elif aba_selecionada == 3 and grafico_colisoes_tentativa:
            grafico_colisoes_tentativa.atualizar_animacao(dt)
            grafico_colisoes_tentativa.desenhar(tela)
        
        # Estatísticas detalhadas abaixo dos gráficos - ajusta posição Y dependendo do gráfico atual
        if aba_selecionada == 0 or aba_selecionada == 2: # Gráficos de visão geral (Tempo Médio/Fase, Média Colisões/Nível)
            y_stats = resize(630)
        else: # Gráficos por tentativa (Tempo/Tentativa, Colisões/Tentativa Linha, Colisões/Tentativa Barras)
            y_stats = resize(650)
        
        # Cabeçalho da tabela de estatísticas
        desenhar_texto("Estatísticas Detalhadas das Tentativas", fonte_texto, COR_TITULO, 
                      tela, resize(100, eh_X=True), y_stats)
        
        # Linhas de informação detalhada
        y_linhas = y_stats + resize(40)
        
        # Determinar tentativas a exibir com base na navegação - SEMPRE mostrar TODAS as tentativas
        if aba_selecionada == 0 or aba_selecionada == 2: 
            # Para gráfico de tempo médio, mostrar todas as tentativas
            tentativas_exibir = tentativas
        else:
            # Para outros gráficos, mostrar todas as tentativas do nível escolhido
            nivel_escolhido = niveis_jogados[indice_nivel_selecionado]
            tentativas_exibir = [t for t in tentativas if t["nivel"] == nivel_escolhido]
        
        tentativas_exibir = sorted(tentativas_exibir, key=lambda t: t["timestamp"], reverse=True)
        

        total_paginas = max(1, (len(tentativas_exibir) + tentativas_por_pagina - 1) // tentativas_por_pagina)
        if pagina_atual >= total_paginas:
            pagina_atual = total_paginas - 1
            
        inicio = pagina_atual * tentativas_por_pagina
        fim = min(inicio + tentativas_por_pagina, len(tentativas_exibir))
        
  
        cabecalho = ["Nível", "Tempo (s)", "Vidas", "Colisões", "Data"]
        espacamento_x = resize(180, eh_X=True)
        x_inicio = resize(100, eh_X=True)
        
        for i, titulo_col in enumerate(cabecalho):
            desenhar_texto(
                titulo_col, 
                pygame.font.SysFont("arial", resize(26), bold=True), 
                DOURADO_ANTIGO,
                tela, 
                x_inicio + i * espacamento_x, 
                y_linhas
            )
        
        # Linhas de separação
        pygame.draw.line(
            tela,
            DOURADO_ANTIGO,
            (x_inicio, y_linhas + resize(30)),
            (x_inicio + espacamento_x * len(cabecalho), y_linhas + resize(30)),
            2
        )
        
        # Desenhar dados das tentativas
        for i, t in enumerate(tentativas_exibir[inicio:fim]):
            y = y_linhas + resize(40) + i * resize(35)
            
            # Status baseado nas vidas restantes (para códigos de cores)
            status_sucesso = t["vidas"] > 0
            cor_status = (0, 200, 0) if status_sucesso else (200, 50, 50)

            dados = [
                str(t["nivel"]),
                f"{t['tempo']:.2f}",
                f"{t['vidas']} {'OK' if status_sucesso else 'FALHA'}", 
                str(t.get("colisoes", 0)),
                t["timestamp"]
            ]
            
            for j, dado in enumerate(dados):
                # O indicador de sucesso/falha tem cor especial
                cor = cor_status if j == 2 else COR_TEXTO
                desenhar_texto(
                    dado, 
                    pygame.font.SysFont("arial", resize(24)), 
                    cor,
                    tela, 
                    x_inicio + j * espacamento_x, 
                    y
                )
        
        # Controles de navegação para as páginas (quando houver mais de uma página)
        if total_paginas > 1:
            nav_y = y_linhas + resize(40) + tentativas_por_pagina * resize(35) + resize(20)
            

            clicou_ant_pag, _ = desenhar_botao(
                texto="< Anterior",
                x=resize(100, eh_X=True),
                y=nav_y,
                largura=resize(150, eh_X=True),
                altura=resize(50),
                cor_normal=cor_com_escala_cinza(150,150,150),
                cor_hover=cor_com_escala_cinza(200,200,200),
                fonte=pygame.font.SysFont("arial", resize(24, eh_X=True)),
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(10)
            )
            if clicou_ant_pag and pagina_atual > 0:
                pagina_atual -= 1
            

            desenhar_texto(
                f"Página {pagina_atual + 1}/{total_paginas}", 
                pygame.font.SysFont("arial", resize(24)), 
                COR_TEXTO,
                tela, 
                LARGURA_TELA // 2 - resize(70, eh_X=True),  # Posição X ajustada para centralizar
                nav_y + resize(15)
            )
            

            clicou_prox_pag, _ = desenhar_botao(
                texto="Próximo >",
                x=LARGURA_TELA - resize(250, eh_X=True),
                y=nav_y,
                largura=resize(150, eh_X=True),
                altura=resize(50),
                cor_normal=cor_com_escala_cinza(150,150,150),
                cor_hover=cor_com_escala_cinza(200,200,200),
                fonte=pygame.font.SysFont("arial", resize(24, eh_X=True)),
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(10)
            )
            if clicou_prox_pag and pagina_atual < total_paginas - 1:
                pagina_atual += 1


        botao_voltar_y = ALTURA_TELA - resize(80)
        if total_paginas > 1:

            nav_bottom = y_linhas + resize(40) + tentativas_por_pagina * resize(35) + resize(90)
            botao_voltar_y = max(nav_bottom, ALTURA_TELA - resize(80))
        
        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=LARGURA_TELA//2 - resize(200, eh_X=True),
            y=botao_voltar_y,
            largura=resize(400, eh_X=True),
            altura=resize(70),
            cor_normal=cor_com_escala_cinza(255, 200, 0),
            cor_hover=cor_com_escala_cinza(255, 255, 0),
            fonte=fonte_botao,
            tela=tela,
            events=events,
            imagem_fundo=BUTTON_PATH,
            border_radius=resize(15)
        )
        if clicou_voltar:
            return

        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)
            
        pygame.display.update()