#include <Servo.h>
#include <avr/pgmspace.h>

// --- MAPEAMENTO DE PINOS E CONSTANTES ---
const int pinoServo1 = 9;
const int pinoServo2 = 10;
const int pinoHallInicio = 12;
const int pinoHallFim = 13;
const int pinoLedR = 6, pinoLedG = 7, pinoLedB = 8;
const int BTN_L = 5, BTN_R = 4;
const int LedMR = 3, LedMB = 2;
const int fioLabirinto = A0;

Servo servo1;
Servo servo2;

// --- ESTRUTURAS DE DADOS E PADRÕES DE MOVIMENTO EM PROGMEM ---
struct ServoStep {
    uint8_t angle;
    uint16_t hold;
};

const ServoStep level1_pattern[] PROGMEM = { {90, 8000} };
const ServoStep level2_pattern[] PROGMEM = { {70, 2000}, {110, 1500} };
const ServoStep level3_pattern[] PROGMEM = { {90, 1500}, {120, 1200}, {60, 1200} };
const ServoStep level4_pattern[] PROGMEM = { {90, 1200}, {130, 1000}, {50, 1000}, {110, 1000} };
const ServoStep level5_pattern[] PROGMEM = { {90, 1000}, {140, 800}, {40, 800}, {120, 700}, {60, 700} };
const ServoStep level6_pattern[] PROGMEM = { {90, 800}, {140, 600}, {50, 600}, {130, 500}, {70, 500} };
const ServoStep level7_pattern[] PROGMEM = { {90, 800}, {145, 500}, {40, 500}, {120, 400}, {60, 400} };
const ServoStep level8_pattern[] PROGMEM = { {90, 600}, {150, 400}, {30, 400}, {125, 350}, {55, 350}, {140, 300} };

const ServoStep* const servoPatternsTable[] PROGMEM = {
    level1_pattern, level2_pattern, level3_pattern, level4_pattern,
    level5_pattern, level6_pattern, level7_pattern, level8_pattern
};

const uint8_t numStepsPerLevel[] PROGMEM = {
    sizeof(level1_pattern) / sizeof(ServoStep), sizeof(level2_pattern) / sizeof(ServoStep),
    sizeof(level3_pattern) / sizeof(ServoStep), sizeof(level4_pattern) / sizeof(ServoStep),
    sizeof(level5_pattern) / sizeof(ServoStep), sizeof(level6_pattern) / sizeof(ServoStep),
    sizeof(level7_pattern) / sizeof(ServoStep), sizeof(level8_pattern) / sizeof(ServoStep)
};

enum ServoState { MOVING, HOLDING };
ServoState estadoAtualServo = HOLDING;

// --- VARIÁVEIS DE ESTADO ---
bool jogoAtivo = false;
int nivelAtual = 1;
bool ledsAtivados = true;
unsigned long debounceColisaoMs = 200;
unsigned long ultimoTempoColisao = 0;
bool servosCongelados = false;
int passoAtualServo = -1; // Inicia em -1 para carregar o passo 0 na primeira transição
unsigned long proximoMovimentoServoTimestamp = 0;
int anguloAtualServo1 = 90, anguloAtualServo2 = 90;
int anguloAlvoServo1 = 90, anguloAlvoServo2 = 90;
unsigned long ultimoPassoServoTimestamp = 0;
int velocidadeServo = 15;
bool estadoBtnL_anterior = HIGH, estadoBtnR_anterior = HIGH;
const long debounceBotaoMs = 50;
unsigned long ultimoTempoBtnL = 0, ultimoTempoBtnR = 0;


// --- SETUP ---
void setup() {
    Serial.begin(9600);
    // ... (resto do setup igual)
    pinMode(fioLabirinto, INPUT_PULLUP);
    pinMode(pinoHallInicio, INPUT_PULLUP);
    pinMode(pinoHallFim, INPUT_PULLUP);
    pinMode(BTN_L, INPUT_PULLUP);
    pinMode(BTN_R, INPUT_PULLUP);
    pinMode(pinoLedR, OUTPUT);
    pinMode(pinoLedG, OUTPUT);
    pinMode(pinoLedB, OUTPUT);
    pinMode(LedMR, OUTPUT);
    pinMode(LedMB, OUTPUT);
    servo1.attach(pinoServo1);
    servo2.attach(pinoServo2);
    resetServos();
    apagarLedsMesa();
    apagarLedsManopla();
}

// --- LOOP ---
void loop() {
    if (Serial.available() > 0) {
        processarComandoSerial();
    }
    if (jogoAtivo) {
        monitorarSensoresJogo();
        atualizarServos();
    }
}

void atualizarServos() {
    if (servosCongelados || !jogoAtivo || nivelAtual <= 0 || nivelAtual > 8) {
        return;
    }

    unsigned long agora = millis();

    switch (estadoAtualServo) {
        case HOLDING:
            // Fase de espera: Apenas verifica se o tempo de 'hold' acabou.
            if (agora >= proximoMovimentoServoTimestamp) {
                // Tempo de espera concluído. Prepara para o próximo movimento.
                uint8_t totalPassos = pgm_read_byte(&numStepsPerLevel[nivelAtual - 1]);
                if (totalPassos == 0) return;

                passoAtualServo = (passoAtualServo + 1) % totalPassos;

                ServoStep passoCorrente;
                const ServoStep* patternPointer = (const ServoStep*)pgm_read_ptr(&servoPatternsTable[nivelAtual - 1]);
                memcpy_P(&passoCorrente, &patternPointer[passoAtualServo], sizeof(ServoStep));
                
                anguloAlvoServo1 = passoCorrente.angle;
                anguloAlvoServo2 = 180 - passoCorrente.angle;
                
                // Muda o estado para iniciar o movimento.
                estadoAtualServo = MOVING;
            }
            break;

        case MOVING:
            // Fase de movimento: Move os servos gradualmente até o alvo.
            if (agora >= ultimoPassoServoTimestamp + velocidadeServo) {
                ultimoPassoServoTimestamp = agora;
                
                bool servo1NoAlvo = (anguloAtualServo1 == anguloAlvoServo1);
                bool servo2NoAlvo = (anguloAtualServo2 == anguloAlvoServo2);

                // Se ambos os servos já chegaram, não faz mais nada nesta fase.
                if (servo1NoAlvo && servo2NoAlvo) {
                    // O movimento terminou. Agora inicia a contagem do tempo de espera.
                    ServoStep passoCorrente;
                    const ServoStep* patternPointer = (const ServoStep*)pgm_read_ptr(&servoPatternsTable[nivelAtual - 1]);
                    memcpy_P(&passoCorrente, &patternPointer[passoAtualServo], sizeof(ServoStep));

                    proximoMovimentoServoTimestamp = agora + passoCorrente.hold;
                    estadoAtualServo = HOLDING; // Muda o estado para aguardar.
                    break; 
                }

                // Move os servos um grau por vez se ainda não chegaram ao alvo.
                if (!servo1NoAlvo) {
                    if (anguloAtualServo1 < anguloAlvoServo1) anguloAtualServo1++;
                    else anguloAtualServo1--;
                    servo1.write(anguloAtualServo1);
                }
                
                if (!servo2NoAlvo) {
                    if (anguloAtualServo2 < anguloAlvoServo2) anguloAtualServo2++;
                    else anguloAtualServo2--;
                    servo2.write(anguloAtualServo2);
                }
            }
            break;
    }
}


// --- LÓGICA DO JOGO E ESTADOS ---
void resetServoStateMachine() {
    passoAtualServo = -1; 
    proximoMovimentoServoTimestamp = millis();
    anguloAlvoServo1 = 90;
    anguloAlvoServo2 = 90;
    estadoAtualServo = HOLDING; // Garante que o estado inicial seja 'HOLDING'
}

void processarComandoSerial() {
    String comando = Serial.readStringUntil('\n');
    comando.trim();
    if (comando == "INICIAR") {
        Serial.println("OK");
    } else if (comando.startsWith("NIVEL:")) {
        nivelAtual = comando.substring(6).toInt();
        iniciarNivel(nivelAtual);
    } else if (comando.startsWith("QTE:")) {
        mostrarSequenciaQTE(comando.substring(4));
    } else if (comando == "LEVEL_FAILED") {
        piscarLed(255, 0, 0, 3, 200);
    } else if (comando == "TERMINAR") {
        terminarNivel();
    } else if (comando.startsWith("DEBOUNCE:")) {
        debounceColisaoMs = comando.substring(9).toInt();
    } else if (comando.startsWith("FEEDBACK:")) {
        ledsAtivados = (comando.substring(9) != "som");
    } else if (comando.startsWith("FREEZE:")) {
        servosCongelados = (comando.substring(7).toInt() == 1);
    } else if (comando.startsWith("SERVO:")) {
        String velocidade = comando.substring(6);
        if (velocidade == "lento") velocidadeServo = 30;
        else if (velocidade == "normal") velocidadeServo = 15;
        else if (velocidade == "rapido") velocidadeServo = 5;
    }
}
void iniciarNivel(int nivel) {
    jogoAtivo = true;
    apagarLedsMesa();
    resetServos();
    resetServoStateMachine();
    while (digitalRead(pinoHallInicio) == HIGH) {
        if (ledsAtivados) { digitalWrite(LedMB, HIGH); delay(150); digitalWrite(LedMB, LOW); delay(150); } 
        else { delay(300); }
    }
    Serial.println("PLAYER_AT_START");
    apagarLedsManopla();
}
void terminarNivel() {
    jogoAtivo = false;
    resetServos();
    apagarLedsMesa();
    apagarLedsManopla();
    resetServoStateMachine();
}
void monitorarSensoresJogo() {
    if (digitalRead(fioLabirinto) == LOW) {
        if (millis() - ultimoTempoColisao > debounceColisaoMs) {
            ultimoTempoColisao = millis();
            Serial.println("COLLISION");
            piscarLed(255, 255, 0, 2, 200);
        }
    }
    if (digitalRead(pinoHallFim) == LOW) {
        Serial.println("LEVEL_COMPLETE");
        piscarLed(0, 255, 0, 3, 200);
        terminarNivel();
    }
    bool estadoBtnL = digitalRead(BTN_L);
    if (estadoBtnL == LOW && estadoBtnL_anterior == HIGH && millis() - ultimoTempoBtnL > debounceBotaoMs) {
        Serial.println("BTN_E");
        ultimoTempoBtnL = millis();
    }
    estadoBtnL_anterior = estadoBtnL;
    bool estadoBtnR = digitalRead(BTN_R);
    if (estadoBtnR == LOW && estadoBtnR_anterior == HIGH && millis() - ultimoTempoBtnR > debounceBotaoMs) {
        Serial.println("BTN_D");
        ultimoTempoBtnR = millis();
    }
    estadoBtnR_anterior = estadoBtnR;
}
void resetServos() {
    anguloAtualServo1 = 90;
    anguloAtualServo2 = 90;
    servo1.write(anguloAtualServo1);
    servo2.write(anguloAtualServo2);
}
void mostrarSequenciaQTE(String sequencia) {
    if (!ledsAtivados) return;
    apagarLedsManopla();
    delay(500);
    for (unsigned int i = 0; i < sequencia.length(); i++) {
        char passo = sequencia.charAt(i);
        if (passo == 'E') { digitalWrite(LedMB, HIGH); } 
        else if (passo == 'D') { digitalWrite(LedMR, HIGH); }
        delay(400);
        apagarLedsManopla();
        delay(200);
    }
}
void piscarLed(int r, int g, int b, int vezes, int duracao) {
    if (!ledsAtivados) return;
    for (int i = 0; i < vezes; i++) {
        digitalWrite(pinoLedR, (r > 0) ? HIGH : LOW);
        digitalWrite(pinoLedG, (g > 0) ? HIGH : LOW);
        digitalWrite(pinoLedB, (b > 0) ? HIGH : LOW);
        delay(duracao);
        apagarLedsMesa();
        delay(duracao);
    }
}
void apagarLedsMesa() {
    if (!ledsAtivados) return;
    digitalWrite(pinoLedR, LOW);
    digitalWrite(pinoLedG, LOW);
    digitalWrite(pinoLedB, LOW);
}
void apagarLedsManopla() {
    if (!ledsAtivados) return;
    digitalWrite(LedMR, LOW);
    digitalWrite(LedMB, LOW);
}