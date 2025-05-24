# A Fúria do Minotauro

**A Fúria do Minotauro** é um **jogo sério** que integra um labirinto metálico físico controlado por Arduino a uma **interface digital em Python/Pygame**. Inspirado na lenda de Teseu e do Minotauro, o projeto foi concebido para **estimular a coordenação motora fina, foco e perseverança** de crianças e adolescentes, com ênfase em usuários com Transtorno do Espectro Autista (TEA).
O sistema fornece feedback auditivo, visual e tátil em tempo real, registra todo o desempenho em JSON e inclui opções de acessibilidade, narrativa temática e sistema de conquistas motivacionais.

---

## Sumário

1. [Contexto e Motivação](#contexto-e-motivação)
2. [Objetivos](#objetivos)
3. [Arquitetura do Projeto](#arquitetura-do-projeto)
4. [Funcionalidades Principais](#funcionalidades-principais)
5. [Hardware e Firmware](#hardware-e-firmware)
6. [Software (Python / Pygame)](#software-python--pygame)
7. [Instalação e Execução](#instalação-e-execução)
8. [Estrutura de Arquivos](#estrutura-de-arquivos)
9. [Equipe](#equipe)
10. [Referências](#referências)

---

## Contexto e Motivação

Pesquisas recentes demonstram que **jogos baseados em gestos** e recursos lúdicos podem acelerar o desenvolvimento motor de crianças com TEA. A coordenação motora fina é crucial para atividades diárias — escrever, abotoar roupas, usar talheres — mas costuma ser um ponto de dificuldade frequente.
“A Fúria do Minotauro” parte desse cenário e insere o treino motor numa narrativa mitológica: o usuário, ajudando Teseu, deve conduzir um anel pelo labirinto sem tocar nas paredes metálicas, enquanto o labirinto “ganha vida” com movimentos de servos. A história, as conquistas e a estética grega foram escolhidas para **tornar o treino mais imersivo e recompensador**.

---

## Objetivos

* Desenvolver **precisão motora fina** por meio de desafios progressivos.
* Oferecer **feedback sensorial multimodal** (som, luz, buzzer, HUD) em tempo real.
* **Registrar e visualizar** estatísticas de desempenho (colisões, tempo, vidas) para acompanhamento de evolução.
* Prover **acessibilidade** (modo escala de cinza, som mudo) e **narrativa motivadora**.
* Garantir estrutura **modular e extensível** em hardware, firmware e software.

---

## Arquitetura do Projeto

1. **Camada Física (Labirinto + Sensores + Atuadores)**

   * Labirinto metálico conectado a 5 V.
   * Anel condutor ligado ao Arduino (ADC).
   * Sensores de efeito Hall para “início” e “fim” do percurso.
   * Dois micro‑servos que movem seções do labirinto.
   * LED RGB para feedback local.

2. **Camada de Firmware (Arduino)**

   * ISR de colisão em pino digital com INPUT\_PULLUP.
   * Protocolo Serial simples (C,val  F  S) a 115 200 bps.
   * Controle de servos (Servo.h) e LED RGB (PWM).
   * Lógica de debounce e sinalização imediata sem depender do PC.

3. **Camada de Software (Python/Pygame)**

   * Pacotes `screens`, `game`, `utils`, `hw`.
   * `main.py` faz seleção de porta serial, pilha de telas e loop principal.
   * `utils.audio_manager`, `utils.drawing`, `utils.achievements`, `utils.graphics`.
   * Persistência em JSON por usuário.
   * Modularidade permite adicionar níveis, conquistas e modos de jogo sem alterar o núcleo.

---

## Funcionalidades Principais

* **Seleção de Porta Serial**: tela inicial lista portas COM/tty; inclui modo simulação.
* **Gerenciamento de Usuários**: criar, selecionar ou excluir perfis (dados salvos em JSON).
* **Níveis Progressivos**: padrões de movimento dos servos, limite de tempo e vidas crescentes.
* **Barra de Progresso Analógica**: cada colisão envia valor proporcional ao avanço e atualiza HUD.
* **Quick‑Time Events**: botões na manopla disparam minijogos de sequência de cores para ganhar bônus (vida extra, pausa do servo etc.).
* **Sistema de Conquistas**: nove troféus (Fio de Ariadne, Coragem de Teseu, Domador do Labirinto, etc.) com notificações animadas.
* **Modos de Acessibilidade**:
  • Escala de cinza — converte todas as cores para tons de cinza.
  • Mudo — silencia músicas e efeitos sem desligar  ou LED.
* **Tela de Desempenho**: gráfico de linhas e barras (utils.graphics) com evolução de tempos, vidas e porcentagem de colisões por nível.
* **Narrativa Mitológica**: diálogos infantis/teen com Teseu; tela “Inicie o jogo” em estilo 16‑bits com efeito bounce.
* **Interface Responsiva**: redimensiona fontes, botões e imagens para qualquer resolução em modo fullscreen.

---

## Hardware e Firmware

### Principais Componentes

* Arduino UNO ou Nano

* Labirinto em fio resistivo ou segmentado

* Anel condutor com ímã neodímio

* 2 × Micro‑servos SG90

* LED RGB cátodo comum

* Capacitor 100 µF (servos)

* Resistores pull‑down 1 MΩ (A0) e limitadores 220 Ω (LED)

### Fluxo de Dados no Firmware

1. Anel toca labirinto → interrupção FALLING em D2 → flag colisão.
2. Loop principal lê sensores Hall (A1/A2), ADC do anel (A0) e estado de colisão; transmite eventos.
3. Recebe comandos “M” (servo)  do Pygame conforme cada nível.
4. Ações críticas (piscar LED, beep curto) são executadas localmente para latência zero.

---

## Software (Python / Pygame)

* **Estrutura Modular**
  • `screens/` – funções de cada tela.
  • `game/` – classe JogoLabirinto e regras.
  • `utils/` – áudio, cores, conquistas, gráficos, desenho AA, serial utils.
  • `hw/arduino_bridge.py` – leitura/escrita Serial.

* **Fluxo Geral**

  1. `main.py` → tela portas → tela usuários → menu principal.
  2. “Jogar” instancia JogoLabirinto, lê eventos do Arduino a cada frame.
  3. No fim do nível, verifica conquistas e exibe telas de conclusão ou falha.
  4. Menu oferece Desempenho, Conquistas, Rejogar e Configurações.

---

## Instalação e Execução

```bash
# clone
$ git clone https://github.com/caiovilquer/A-furia-do-minotauro.git
$ cd A-furia-do-minotauro/Labirinto_game

# ambiente virtual
$ python -m venv .venv
$ source .venv/bin/activate   # Windows: .venv\Scripts\activate

# dependências
(.venv) $ pip install -r requirements.txt

# carregar firmware no Arduino (pasta firmware_arduino)

# executar
(.venv) $ python main.py
```

---

## Estrutura de Arquivos

```
A-furia-do-minotauro/
├─ Labirinto_game/
│  ├─ main.py
│  ├─ screens/
│  ├─ game/
│  ├─ utils/
│  ├─ assets/
│  │  ├─ images/
│  │  ├─ sounds/
│  │  └─ fonts/
│  └─ data/
├─ firmware_arduino/
│  └─ firmware.ino
└─ Documentação/
   └─ Documentacao_projeto.pdf
```

---

## Equipe:
  - Caio Vilquer Carvalho
  - Samuel Damasceno Pereira Caldeira
  - Marcello Braga de Oliveira
---

## Referências
- [AUTIBOTS: Jogo Digital Educativo para Desenvolvimento Cognitivo e Motor de Crianças com TEA](https://journals-sol.sbc.org.br/index.php/rbie/article/view/3300)
- [Gesture-based Video Games to Support Fine-Motor Coordination Skills of Children with Autism](https://dl.acm.org/doi/10.1145/3311927.3325310)
- [A case study of gesture-based games in enhancing the fine motor skills of children with autism spectrum disorders](https://www.researchgate.net/publication/323214177_A_case_study_of_gesture-based_games_in_enhancing_the_fine_motor_skills_and_recognition_of_children_with_autism)
Este projeto se apoia no **PDF de documentação** compartilhado (com introdução, especificações e referenciais teóricos) e nos artigos citados acima. Para mais detalhes sobre o funcionamento físico do labirinto e esquemas de ligação elétrica, consulte o documento intitulado **“Documetação_projeto.pdf”**.
