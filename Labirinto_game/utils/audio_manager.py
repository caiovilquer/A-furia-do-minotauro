import pygame
import os
from constants import SOUND_PATH, SOM_LIGADO

class AudioManager:
    """Gerenciador de áudio para o jogo."""
    
    def __init__(self):
        self.sounds = {}
        self.current_bg_music = None
        self.bg_volume = 0.5
        self.fx_volume = 1.0
        self._som_ligado = SOM_LIGADO
        
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
                    self.sounds[name] = path  # Apenas armazenamos o caminho para a música de fundo
                else:
                    self.sounds[name] = pygame.mixer.Sound(path)
            else:
                print(f"Arquivo de som não encontrado: {path}")
    
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
        """Toca um efeito sonoro."""
        if self._som_ligado and sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if isinstance(sound, pygame.mixer.Sound):
                sound.set_volume(self.fx_volume)
                sound.play()
    
    def play_background(self, sound_name="background"):
        """Inicia a reprodução da música de fundo."""
        if self._som_ligado and sound_name in self.sounds and isinstance(self.sounds[sound_name], str):
            # Pare qualquer música que esteja tocando
            pygame.mixer.music.stop()
            
            # Carregue e reproduza a nova música
            pygame.mixer.music.load(self.sounds[sound_name])
            pygame.mixer.music.set_volume(self.bg_volume)
            pygame.mixer.music.play(-1)  # -1 para repetir infinitamente
            self.current_bg_music = sound_name
    
    def stop_background(self):
        """Para a reprodução da música de fundo."""
        pygame.mixer.music.stop()
        self.current_bg_music = None
    
    def set_bg_volume(self, volume):
        """Ajusta o volume da música de fundo."""
        self.bg_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.bg_volume)
    
    def set_fx_volume(self, volume):
        """Ajusta o volume dos efeitos sonoros."""
        self.fx_volume = max(0.0, min(1.0, volume))

# Crie uma instância única do gerenciador de áudio
audio_manager = AudioManager()
