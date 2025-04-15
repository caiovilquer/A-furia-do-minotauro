import pygame
import sys
from constants import (LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img,
                     FONTE_TITULO, FONTE_BOTAO, FONTE_TEXTO, COR_TITULO, COR_TEXTO, PRETO)
from utils.drawing import desenhar_texto, desenhar_botao, resize
from utils.colors import cor_com_escala_cinza
from utils.user_data import carregar_usuarios, salvar_usuarios

def tela_escolha_usuario(tela):
    """Tela para escolher ou criar um usuário."""
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    input_font = FONTE_TEXTO

    usuarios_data = carregar_usuarios()
    lista_usuarios = list(usuarios_data.keys())

    titulo_x = LARGURA_TELA//2 - resize(400, eh_X=True)
    titulo_y = resize(100)

    y_inicial_botoes = resize(250)  # onde começam a listar os usuários
    espacamento_botoes = resize(90) # espaçamento entre botões de usuários

    input_box = pygame.Rect(LARGURA_TELA//2 - resize(200, eh_X=True), y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + resize(50), resize(400, eh_X=True), resize(60))

    cor_ativo = cor_com_escala_cinza(200, 200, 200)
    cor_inativo = cor_com_escala_cinza(150, 150, 150)
    cor_atual = cor_inativo
    usuario_digitado = ""
    ativo_input = False

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif ativo_input:
                    if event.key == pygame.K_RETURN:
                        if usuario_digitado.strip() != "":
                            if usuario_digitado.strip() not in usuarios_data:
                                usuarios_data[usuario_digitado.strip()] = {
                                    "nivel": 1,
                                    "tentativas": []
                                }
                                salvar_usuarios(usuarios_data)

                            return usuario_digitado.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        usuario_digitado = usuario_digitado[:-1]
                    else:
                        usuario_digitado += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    ativo_input = True
                    cor_atual = cor_ativo
                else:
                    ativo_input = False
                    cor_atual = cor_inativo

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto("Selecione ou Crie um Usuário", fonte_titulo, COR_TITULO, tela, titulo_x-resize(150, eh_X=True), titulo_y)

        # Lista de usuários
        y_offset = y_inicial_botoes
        for usr in lista_usuarios:
            x_user_btn = LARGURA_TELA//2 - resize(220, eh_X=True)
            y_user_btn = y_offset
            w_user_btn = resize(300, eh_X=True)
            h_user_btn = resize(70)

            x_del_btn = x_user_btn + w_user_btn + resize(20, eh_X=True)
            w_del_btn = resize(120, eh_X=True)
            h_del_btn = resize(70)

            clicou_user, _ = desenhar_botao(
                texto=usr,
                x=x_user_btn,
                y=y_user_btn,
                largura=w_user_btn,
                altura=h_user_btn,
                cor_normal=cor_com_escala_cinza(0, 200, 0),
                cor_hover=cor_com_escala_cinza(0, 255, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(10)
            )
            if clicou_user:
                return usr

            clicou_delete, _ = desenhar_botao(
                texto="Del",
                x=x_del_btn,
                y=y_user_btn,
                largura=w_del_btn,
                altura=h_del_btn,
                cor_normal=cor_com_escala_cinza(200, 0, 0),
                cor_hover=cor_com_escala_cinza(255, 0, 0),
                fonte=fonte_botao,
                tela=tela,
                events=events,
                imagem_fundo=None,
                border_radius=resize(10)
            )
            if clicou_delete:
                if usr in usuarios_data:
                    del usuarios_data[usr]
                salvar_usuarios(usuarios_data)
                lista_usuarios.remove(usr)
                input_box = pygame.Rect(LARGURA_TELA//2 - resize(200, eh_X=True), y_inicial_botoes + len(lista_usuarios)*espacamento_botoes + resize(50), resize(400, eh_X=True), resize(60))
                break

            y_offset += espacamento_botoes

        pygame.draw.rect(tela, cor_atual, input_box, 0, border_radius=resize(10))
        txt_surface = input_font.render(usuario_digitado, True, PRETO)
        tela.blit(txt_surface, (input_box.x+resize(10, eh_X=True), input_box.y+resize(10)))
        desenhar_texto("Novo usuário e ENTER:", input_font, COR_TEXTO, tela, input_box.x, input_box.y - resize(50))

        pygame.display.update()