import pygame
import sys
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios

def tela_desempenho(tela, usuario):
    """Tela de desempenho do usuário."""
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
        return all_t[-6:]

    titulo_x = resize(100, eh_X=True)
    titulo_y = resize(50)

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
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

        desenhar_texto_sombra(f"Desempenho de {usuario}", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        desenhar_texto_sombra(f"Nível atual: {nivel}", fonte_texto, COR_TEXTO, tela, resize(100, eh_X=True), resize(180))
        
        clicou_ant, _ = desenhar_botao(
            texto="<",
            x=resize(100, eh_X=True),
            y=resize(300),
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

        clicou_prox, _ = desenhar_botao(
            texto=">",
            x=resize(220, eh_X=True),
            y=resize(300),
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

        nivel_escolhido = niveis_jogados[indice_nivel_selecionado]
        desenhar_texto(f"Nível escolhido: {nivel_escolhido}", fonte_texto, COR_TEXTO, tela, resize(320, eh_X=True), resize(320))

        desenhar_texto("Tentativas desse nível (últimas 6):", fonte_texto, COR_TEXTO, tela, resize(100, eh_X=True), resize(400))
        tentativas_nivel = mostrar_tentativas_nivel(nivel_escolhido)
        if tentativas_nivel:
            melhor_tentativa = min(tentativas_nivel, key=lambda x: x["tempo"] if x["vidas"] > 0 else float('inf'))
            desenhar_texto(f"Melhor tempo: {melhor_tentativa['tempo']:.2f} s", fonte_texto, COR_TEXTO, tela, resize(100, eh_X=True), resize(480))
        else:
            desenhar_texto("Nenhuma tentativa registrada.", fonte_texto, COR_TEXTO, tela, resize(100, eh_X=True), resize(480))
        y_pos = resize(560)
        for idx, tent in enumerate(tentativas_nivel):
            texto_tent = (
                f"Tempo: {tent['tempo']:.2f}s, Vidas: {tent['vidas']}, "
                f"Data: {tent['timestamp']}"
            )
            if tent['vidas'] == 0:
                texto_tent += " (Não concluído)"
            else:
                texto_tent += " (Concluído)"
            desenhar_texto(f"{idx+1} - {texto_tent}", fonte_texto, COR_TEXTO, tela, resize(100, eh_X=True), y_pos)
            y_pos += resize(50)

        clicou_voltar, _ = desenhar_botao(
            texto="Voltar",
            x=resize(100, eh_X=True),
            y=y_pos + resize(50),
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