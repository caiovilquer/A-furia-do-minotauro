import pygame
import sys
import serial
import serial.tools.list_ports
import time
from constants import BUTTON_PATH, LARGURA_TELA, ALTURA_TELA, FPS, AZUL_CLARO, background_img
from constants import FONTE_TITULO, FONTE_BOTAO, COR_TITULO, FONTE_TEXTO, COR_TEXTO
from utils.drawing import desenhar_texto, desenhar_botao, desenhar_texto_sombra, resize, aplicar_filtro_cinza_superficie
from utils.colors import cor_com_escala_cinza

def tela_selecao_porta(tela):
    """Tela para selecionar a porta do Arduino."""
    global PORTA_SELECIONADA
    clock = pygame.time.Clock()
    fonte_titulo = FONTE_TITULO
    fonte_botao = FONTE_BOTAO
    fonte_texto = FONTE_TEXTO

    lista_portas = [p.device for p in serial.tools.list_ports.comports()]

    titulo_x = LARGURA_TELA//2 - resize(580, eh_X=True)
    titulo_y = resize(80)

    y_inicial_botoes = resize(250)
    espacamento_botoes = resize(90)
    
    # Estado para comunicação com Arduino
    arduino_conectando = False
    arduino_serial = None
    mensagem_status = None
    tempo_inicio_conexao = 0
    
    # Constantes de comunicação
    MENSAGEM_INICIO = b'INICIAR\n'    
    MENSAGEM_CONFIRMACAO = b'OK\n'   
    TIMEOUT_CONEXAO = 5              

    while True:
        events = pygame.event.get()
        clock.tick(FPS)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from constants import PORTA_SELECIONADA
                    globals()['PORTA_SELECIONADA'] = None
                    return None

        if background_img:
            tela.blit(background_img, (0, 0))
        else:
            tela.fill(AZUL_CLARO)

        desenhar_texto_sombra("Selecione a porta do Arduino", fonte_titulo, COR_TITULO, tela, titulo_x, titulo_y)
        
        # Se estiver tentando conectar ao Arduino, mostra mensagem de espera
        if arduino_conectando:
            tempo_decorrido = time.time() - tempo_inicio_conexao
            
            # Verificar timeout
            if tempo_decorrido > TIMEOUT_CONEXAO:
                mensagem_status = "Timeout na comunicação. Tente novamente."
                arduino_conectando = False
                if arduino_serial:
                    arduino_serial.close()
                    arduino_serial = None
            
            # Tentar ler a confirmação do Arduino
            elif arduino_serial and arduino_serial.in_waiting > 0:
                resposta = arduino_serial.readline()
                print(f"Resposta do Arduino: {resposta}")
                if resposta.strip() == MENSAGEM_CONFIRMACAO.strip():
                    from constants import PORTA_SELECIONADA
                    globals()['PORTA_SELECIONADA'] = arduino_serial
                    return arduino_serial
                else:
                    mensagem_status = "Resposta inválida do Arduino."
                    arduino_conectando = False
                    arduino_serial.close()
                    arduino_serial = None
            
            # Mostrar mensagem de aguardando
            pontos = "." * (int(tempo_decorrido) % 4)
            mensagem_conexao = f"Conectando ao Arduino{pontos}"
            desenhar_texto(mensagem_conexao, fonte_texto, COR_TEXTO, tela, 
                           LARGURA_TELA//2 - resize(200, eh_X=True), 
                           y_inicial_botoes + resize(300))
        
        elif mensagem_status:
            desenhar_texto(mensagem_status, fonte_texto, (255, 50, 50), tela, 
                          LARGURA_TELA//2 - resize(180, eh_X=True), 
                          y_inicial_botoes + resize(250))
            
            clicou_tentar, _ = desenhar_botao(
                texto="Tentar Novamente",
                x=LARGURA_TELA//2 - resize(175, eh_X=True),
                y=y_inicial_botoes + resize(320),
                largura=resize(350, eh_X=True),
                altura=resize(65),
                cor_normal=cor_com_escala_cinza(0, 150, 80),
                cor_hover=cor_com_escala_cinza(0, 190, 100),
                fonte=fonte_texto,
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(10)
            )
            if clicou_tentar:
                mensagem_status = None
                arduino_conectando = False
                if arduino_serial and arduino_serial.is_open:
                    arduino_serial.close()
                arduino_serial = None
            
            clicou_simular, _ = desenhar_botao(
                texto="Usar Simulação",
                x=LARGURA_TELA//2 - resize(175, eh_X=True),
                y=y_inicial_botoes + resize(400),
                largura=resize(350, eh_X=True),
                altura=resize(65),
                cor_normal=cor_com_escala_cinza(180, 100, 50),
                cor_hover=cor_com_escala_cinza(200, 120, 60),
                fonte=fonte_texto,
                tela=tela,
                events=events,
                imagem_fundo=BUTTON_PATH,
                border_radius=resize(10)
            )
            if clicou_simular:
                from constants import PORTA_SELECIONADA
                globals()['PORTA_SELECIONADA'] = None
                return None
        
        # Se não estiver conectando, mostrar botões de porta
        else:
            y_offset = y_inicial_botoes
            for port in lista_portas:
                clicou, _ = desenhar_botao(
                    texto=port,
                    x=LARGURA_TELA//2 - resize(160, eh_X=True),
                    y=y_offset,
                    largura=resize(300, eh_X=True),
                    altura=resize(60),
                    cor_normal=cor_com_escala_cinza(0, 150, 200),
                    cor_hover=cor_com_escala_cinza(0, 200, 255),
                    fonte=fonte_botao,
                    tela=tela,
                    events=events,
                    imagem_fundo=BUTTON_PATH,
                    border_radius=resize(10)
                )
                if clicou:
                    try:
                        arduino_serial = serial.Serial(port, 9600, timeout=1)
                        time.sleep(2)  # Aguarda a inicialização da comunicação
                        arduino_serial.write(MENSAGEM_INICIO)
                        arduino_serial.flush()
                        arduino_conectando = True
                        tempo_inicio_conexao = time.time()
                        mensagem_status = None
                        print(f"Tentando conectar à porta {port}")
                    except Exception as e:
                        mensagem_status = f"Erro ao abrir porta: {port}\n{str(e)}"
                        print(mensagem_status)
                        arduino_serial = None
                    
                y_offset += espacamento_botoes

            clicou_semport, _ = desenhar_botao(
                texto="Simulação",
                x=LARGURA_TELA//2 - resize(160, eh_X=True),
                y=y_offset + resize(100),
                largura=resize(300, eh_X=True),
                altura=resize(60),
                cor_normal=cor_com_escala_cinza(180, 100, 50),
                cor_hover=cor_com_escala_cinza(200, 120, 60),
                fonte=fonte_botao,
                tela=tela,
                imagem_fundo=BUTTON_PATH,
                events=events,
                border_radius=resize(10)
            )
            if clicou_semport:
                from constants import PORTA_SELECIONADA
                globals()['PORTA_SELECIONADA'] = None
                return None
            
        import constants
        if constants.ESCALA_CINZA:
            aplicar_filtro_cinza_superficie(tela)

        pygame.display.update()