## Labirinto Sensorial Tecnológico

Este projeto consiste em um **jogo sério** que tem como objetivo **facilitar a melhoria da coordenação motora fina** de pessoas com Transtorno do Espectro Autista (TEA) por meio de um **labirinto sensorial** controlado por Arduino e integrado a uma **interface digital** desenvolvida em Python (Pygame). A proposta une conceitos de **jogos educacionais**, **feedback sensorial** e **movimentação motora**, seguindo princípios indicados em literaturas especializadas.

---

## Sumário
1. [Contexto e Motivação](#contexto-e-motivação)
2. [Objetivos](#objetivos)
3. [Arquitetura do Projeto](#arquitetura-do-projeto)
4. [Funcionalidades Principais](#funcionalidades-principais)
5. [Hardware (Arduino)](#hardware-arduino)
6. [Software (Python / Pygame)](#software-python--pygame)
7. [Instalação e Execução](#instalação-e-execução)
8. [Estrutura de Arquivos](#estrutura-de-arquivos)
9. [Contribuições e Créditos](#contribuições-e-créditos)
10. [Referências](#referências)

---

## Contexto e Motivação

A coordenação motora fina é uma habilidade fundamental para a autonomia e a qualidade de vida de pessoas com TEA, auxiliando em atividades cotidianas como escrever, usar talheres e manipular objetos com precisão. Pesquisas e trabalhos acadêmicos sobre **jogos sérios** e **jogos baseados em gestos** têm demonstrado resultados promissores na melhora dessas habilidades de maneira lúdica e motivadora.  
   
Foi nesse contexto que surgiu o **Labirinto Sensorial Tecnológico**: um jogo que desafia o usuário a conduzir um anel condutor por um labirinto metálico, com feedbacks sensoriais (sonoros, visuais) em tempo real e dados de desempenho registrados no software.

---

## Objetivos

- **Melhorar a coordenação motora fina** de pessoas com TEA, a partir de um treinamento lúdico e interativo.  
- **Fornecer feedback sensorial** (sonoros, LEDs, buzzer) em tempo real para aumentar o engajamento e a correção de movimentos.  
- **Monitorar e gravar o progresso** do jogador (vidas, colisões, tempo de conclusão, nível atual etc.), possibilitando avaliar a evolução ao longo do uso.  
- **Tornar o projeto acessível** e de fácil customização, permitindo que profissionais e educadores possam adaptá-lo às necessidades de cada pessoa.

---

## Arquitetura do Projeto

1. **Arduino** cuida da leitura de sensores e do controle de atuadores:
   - Estrutura metálica do labirinto.
   - Anel condutor.
   - Servomotores (para movimentos do labirinto).
   - Buzzer e LED RGB (feedback sensorial).
   - Sensores de efeito Hall e medições de tensão no anel para detectar contato.

2. **Computador (Python/Pygame)**:
   - Interface gráfica (menu, seleção de usuário, jogo, desempenho).
   - Lógica principal do jogo (níveis, colisões, contagem de vidas).
   - Registra tentativas e evolução do usuário (JSON).

---

## Funcionalidades Principais

1. **Seleção de Usuário / Criação e Exclusão**  
   - Permite escolher usuários existentes ou criar um novo.  
   - É possível **excluir** um usuário e todo o seu histórico de progresso.

2. **Jogo (Labirinto Sensorial)**  
   - O labirinto metálico é controlado por servomotores que fazem movimentos para aumentar ou reduzir a dificuldade.  
   - O anel condutor deve ser guiado sem tocar nas bordas do labirinto.  
   - Cada colisão reduz vidas e gera feedback (sonoro e LED via Arduino, e mensagem no Pygame).  
   - Caso as vidas acabem, o jogador precisa reiniciar o nível.

3. **Progressão de Níveis**  
   - A dificuldade aumenta a cada nível, com diferentes padrões de movimentação do labirinto e limite de tempo.  
   - Ao concluir cada nível, o usuário pode optar por repetir o nível para melhorar o tempo, ir para o próximo nível ou voltar ao menu.

4. **Estatísticas e Desempenho**  
   - Todos os dados (tempo de conclusão, vidas restantes, nível e data/hora) são salvos em um arquivo JSON.  
   - Um menu dedicado exibe o **histórico** (últimas tentativas) para o nível selecionado.  
   - Permite acompanhar a evolução do jogador ao longo do tempo.

5. **Rejogar Níveis**  
   - O jogador pode revisitar níveis anteriores para treinar mais e buscar melhores resultados.

---

## Hardware (Arduino)

### Componentes Principais
- **Arduino UNO** ou similar.
- **Estrutura metálica** do labirinto.
- **Anel condutor** conectado a um cabo (ADC do Arduino).
- **Sensores de efeito Hall lineares** para detecção de início/fim de curso.
- **Servomotores** para movimentar partes do labirinto.
- **Buzzer** passivo para saída de áudio.
- **LED RGB** para indicar estados (vidas restantes, vitória etc.).

### Principais Funções no Arduino
- **Detecção de colisão**: ao perceber o contato do anel com o labirinto (queda de tensão no ADC).  
- **Geração de sinais de feedback**:  
  - **Buzzer** para sons de alerta (ex.: número de vidas restantes).  
  - **LED RGB** indicando cores diferentes conforme o status (amarelo para perda de vida, vermelho para reinício, verde para conclusão etc.).  
- **Movimentação do labirinto**: o Arduino recebe comandos via serial do software para acionar os servomotores, gerando padrões de movimento.

### Esquemático Simplificado
```
[ Labirinto Metalico ] --(5V)--> [ Arduino ADC ] --(GND)
[ Sensores Hall ] ----> [ Arduino Entradas Digitais ]
[ Servomotor ] <-- [ Arduino PWM ]
[ Buzzer, LED RGB ] --> [ Arduino Saídas Digitais ]
[ Comunicação Serial ] <-> [ Computador (Pygame) ]
```

---

## Software (Python / Pygame)

O **código Python** está dividido em telas principais:  

1. **Seleção de Usuário** (com criação e deleção de usuários).  
2. **Menu Principal** (iniciar jogo, ver desempenho, rejogar nível ou sair).  
3. **Tela do Jogo** (loop principal, leitura de colisões e controle de níveis).  
4. **Tela de Desempenho** (para exibir histórico de tentativas por nível).  
5. **Tela de Rejogar** (seleciona qual nível já concluído deve ser re-executado).

As telas usam botões e texto via Pygame, com um background temático. Os dados de progresso são salvos em um **arquivo JSON** (nomeado `usuarios.json`).

---

## Instalação e Execução

1. **Clonar ou baixar** este repositório:
   ```bash
   git clone https://github.com/caiovilquer/labirinto-sensorial-PCS.git
   ```
2. **Instalar dependências** do Python:
   ```bash
   pip install pygame
   pip install pyserial
   ```
3. **Conectar o Arduino**:
   - Carregue o firmware para o Arduino que faz a leitura do anel e sensores, e se comunica com o Pygame via porta serial.  
   - Ajuste a porta serial correspondente (ex.: `COM3` no Windows ou `/dev/ttyACM0` no Linux) no código Python, se necessário.

4. **Executar o jogo**:
   ```bash
   python labirinto.py
   ```
   - Caso o arquivo principal possua outro nome, substitua o `labirinto.py` adequadamente.  

5. **Navegação**:
   - Na tela inicial, selecione ou crie um usuário.  
   - Em seguida, navegue pelo menu para iniciar o jogo, visualizar desempenho ou rejogar algum nível.

---

## Estrutura de Arquivos

```
labirinto-sensorial/
│
├─ background_labirinto.png   # Imagem de fundo (opcional)
├─ usuarios.json              # Banco de dados local em formato JSON
├─ labirinto.py                    # Arquivo principal que executa o jogo
├─ <outros_arquivos>.py       # Módulos (caso tenha separado telas em diferentes arquivos)
├─ README.md                  # Este arquivo de documentação
└─ firmware_arduino/          # Exemplo de firmware .ino para ler sensores e acionar servos
```

---

## Contribuições e Créditos

- **Equipe**:
  - Caio Vilquer Carvalho
  - Samuel Damasceno Pereira Caldeira
  - Marcello Braga de Oliveira
- **Referências Acadêmicas**:
  - [AUTIBOTS: Jogo Digital Educativo para Desenvolvimento Cognitivo e Motor de Crianças com TEA](https://journals-sol.sbc.org.br/index.php/rbie/article/view/3300)
  - [Gesture-based Video Games to Support Fine-Motor Coordination Skills of Children with Autism](https://dl.acm.org/doi/10.1145/3311927.3325310)
  - [A case study of gesture-based games in enhancing the fine motor skills of children with autism spectrum disorders](https://www.researchgate.net/publication/323214177_A_case_study_of_gesture-based_games_in_enhancing_the_fine_motor_skills_and_recognition_of_children_with_autism)

---

## Referências

Este projeto se apoia no **PDF de documentação** compartilhado (com introdução, especificações e referenciais teóricos) e nos artigos citados acima. Para mais detalhes sobre o funcionamento físico do labirinto e esquemas de ligação elétrica, consulte o documento intitulado **“Documetação_projeto.pdf”**.
