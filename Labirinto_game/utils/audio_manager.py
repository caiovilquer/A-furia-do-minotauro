import pygame
import os
import random
from constants import SOUND_PATH, SOM_LIGADO

class AudioManager:
    """Gerenciador de áudio para o jogo."""
    
    def __init__(self):
        self.sounds = {}
        self.current_bg_music = None
        self.bg_volume = 0.5
        self.fx_volume = 1.0
        self._som_ligado = SOM_LIGADO
        self.current_voiced_dialogue = None  # Para rastrear o diálogo atual em reprodução
        
        # Certifique-se de que o mixer pygame esteja inicializado
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
    
    def load_sounds(self):
        """Carrega todos os sons usados no jogo."""
        # Cria a pasta de sons se não existir
        os.makedirs(SOUND_PATH, exist_ok=True)
        
        # Caminhos para os arquivos de sons
        sound_files = {
            "background": os.path.join(SOUND_PATH, "initial_background_music.mp3"),
            "hover": os.path.join(SOUND_PATH, "hover.wav"),
            "click": os.path.join(SOUND_PATH, "click1.wav"),
            "success": os.path.join(SOUND_PATH, "success.wav"),
            "failure": os.path.join(SOUND_PATH, "failure.wav"),
            "collision": os.path.join(SOUND_PATH, "collision.wav"),
            "achievement": os.path.join(SOUND_PATH, "achievement.wav"),
            "earthquake": os.path.join(SOUND_PATH, "earthquake.wav"),
        }
        
        # Verificar se os arquivos existem antes de carregar
        for name, path in sound_files.items():
            if os.path.exists(path):
                if name == "background":
                    self.sounds[name] = {
                        "file": path,  # Caminho para a música de fundo
                        "volume": self.bg_volume  # Volume individual
                    }
                else:
                    sound = pygame.mixer.Sound(path)
                    self.sounds[name] = {
                        "sound": sound,
                        "volume": self.fx_volume  # Volume individual
                    }
            else:
                print(f"Arquivo de som não encontrado: {path}")
        
        # Carrega os áudios dublados para eventos específicos
        self.load_voiced_dialogues()
    
    def load_voiced_dialogues(self):
        """Carrega os áudios dublados para eventos específicos."""
        dialogos_path = os.path.join(SOUND_PATH, "dialogos")
        if not os.path.exists(dialogos_path):
            print(f"Pasta de diálogos dublados não encontrada: {dialogos_path}")
            return
            
        # Eventos e suas variações
        eventos = {
            "colisao_1vida":["uma_vida_1", "uma_vida_2", "uma_vida_3"],
            "colisao_2vidas": ["duas_vidas_1", "duas_vidas_2", "duas_vidas_3"] ,
            "perdeu": ["perdeu_1", "perdeu_2", "perdeu_3"],
            "ganhou": ["ganhou_1", "ganhou_2", "ganhou_3"]
        }
        
        # Carregar cada variação de áudio
        for evento, variacoes in eventos.items():
            self.sounds[evento] = []
            for variacao in variacoes:
                arquivo_path = os.path.join(dialogos_path, f"{variacao}.mp3")
                if os.path.exists(arquivo_path):
                    sound = pygame.mixer.Sound(arquivo_path)
                    self.sounds[evento].append({
                        "sound": sound,
                        "volume": self.fx_volume,
                        "name": variacao
                    })
                else:
                    print(f"Arquivo de áudio dublado não encontrado: {arquivo_path}")
    
    @property
    def som_ligado(self):
        return self._som_ligado
    
    @som_ligado.setter
    def som_ligado(self, value):
        """Define se o som está ativado ou desativado."""
        self._som_ligado = value
        if not value:
            pygame.mixer.music.pause()
        elif self.current_bg_music:
            pygame.mixer.music.unpause()
    
    def play_sound(self, sound_name):
        """Toca um efeito sonoro com seu volume individual."""
        if self._som_ligado and sound_name in self.sounds:
            sound_info = self.sounds[sound_name]
            if "sound" in sound_info:
                sound = sound_info["sound"]
                sound.set_volume(sound_info["volume"])
                sound.play()
    
    def play_background(self, sound_name="background"):
        """Inicia a reprodução da música de fundo com seu volume individual."""
        if self._som_ligado and sound_name in self.sounds and "file" in self.sounds[sound_name]:
            # Pare qualquer música que esteja tocando
            pygame.mixer.music.stop()
            
            # Carregue e reproduza a nova música
            sound_info = self.sounds[sound_name]
            pygame.mixer.music.load(sound_info["file"])
            pygame.mixer.music.set_volume(sound_info["volume"])
            pygame.mixer.music.play(-1)  # -1 para repetir infinitamente
            self.current_bg_music = sound_name
    
    def stop_background(self):
        """Para a reprodução da música de fundo."""
        pygame.mixer.music.stop()
        self.current_bg_music = None
    
    def set_bg_volume(self, volume):
        """Ajusta o volume da música de fundo."""
        self.bg_volume = max(0.0, min(1.0, volume))
        
        # Atualizar o volume da música atual se existir
        if self.current_bg_music and self.current_bg_music in self.sounds:
            self.sounds[self.current_bg_music]["volume"] = self.bg_volume
            pygame.mixer.music.set_volume(self.bg_volume)
    
    def set_fx_volume(self, volume):
        """Ajusta o volume padrão dos efeitos sonoros."""
        self.fx_volume = max(0.0, min(1.0, volume))
    
    def set_sound_volume(self, sound_name, volume):
        """Define o volume de um som específico."""
        if sound_name in self.sounds:
            volume = max(0.0, min(1.0, volume))
            self.sounds[sound_name]["volume"] = volume
            
            # Se for a música de fundo atual, atualize também o mixer
            if sound_name == self.current_bg_music:
                pygame.mixer.music.set_volume(volume)
    
    def stop_voiced_dialogue(self):
        """Para a reprodução do diálogo atual se houver algum."""
        if self.current_voiced_dialogue and 'sound' in self.current_voiced_dialogue:
            self.current_voiced_dialogue['sound'].stop()
            self.current_voiced_dialogue = None
    
    def play_voiced_dialogue(self, evento):
        """Reproduz aleatoriamente uma das variações de áudio dublado para um evento."""
        if self._som_ligado and evento in self.sounds and isinstance(self.sounds[evento], list) and self.sounds[evento]:
            # Para qualquer diálogo que esteja sendo reproduzido
            self.stop_voiced_dialogue()
            
            # Seleciona aleatoriamente uma das variações
            variacao = random.choice(self.sounds[evento])
            if "sound" in variacao:
                sound = variacao["sound"]
                sound.set_volume(variacao["volume"])
                sound.play()
                self.current_voiced_dialogue = variacao  # Registra o diálogo atual
                return True
        return False

# Crie uma instância única do gerenciador de áudio
audio_manager = AudioManager()
