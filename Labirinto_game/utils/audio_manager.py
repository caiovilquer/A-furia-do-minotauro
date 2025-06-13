import pygame
import os
import random
from constants import SOUND_PATH, SOM_LIGADO

class AudioManager:
    """Gerenciador de áudio para o jogo com canais separados para música, SFX e vozes."""
    
    def __init__(self):
        self.sounds = {}
        self.current_bg_music = None
        self.bg_volume = 0.5      # Volume da música de fundo
        self.sfx_volume = 0.7     # Volume dos efeitos sonoros
        self.voice_volume = 0.8   # Volume das vozes
        self._som_ligado = SOM_LIGADO
        self.current_voiced_dialogue = None
        
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        pygame.mixer.set_num_channels(16)
        
        # Canal 0: Reservado para pygame.mixer.music (música de fundo)
        # Canais 1-8: Efeitos sonoros (SFX)
        self.sfx_channels = [pygame.mixer.Channel(i) for i in range(1, 9)]
        
        # Canais 9-15: Vozes (diálogos dublados)
        self.voice_channels = [pygame.mixer.Channel(i) for i in range(9, 16)]
        
        self.current_voice_channel_index = 0
    
    def load_sounds(self):
        """Carrega todos os sons usados no jogo."""
        os.makedirs(SOUND_PATH, exist_ok=True)
        
        sound_files = {
            "background": os.path.join(SOUND_PATH, "initial_background_music.mp3"),
            "hover": os.path.join(SOUND_PATH, "hover.wav"),
            "click": os.path.join(SOUND_PATH, "click1.wav"),
            "success": os.path.join(SOUND_PATH, "success.wav"),
            "failure": os.path.join(SOUND_PATH, "failure.wav"),
            "collision": os.path.join(SOUND_PATH, "collision.wav"),
            "achievement": os.path.join(SOUND_PATH, "achievement.wav"),
            "earthquake": os.path.join(SOUND_PATH, "earthquake.wav"),
            "qte_start": os.path.join(SOUND_PATH, "qte_start.wav"),
            "qte_hit": os.path.join(SOUND_PATH, "qte_hit.wav"),
            "qte_fail": os.path.join(SOUND_PATH, "qte_fail.wav"),
            "qte_success": os.path.join(SOUND_PATH, "qte_success.wav"),
        }
        
        for name, path in sound_files.items():
            if os.path.exists(path):
                if name == "background":
                    self.sounds[name] = {
                        "file": path,
                        "volume": self.bg_volume,
                        "type": "music"
                    }
                else:
                    sound = pygame.mixer.Sound(path)
                    self.sounds[name] = {
                        "sound": sound,
                        "volume": self.sfx_volume,
                        "type": "sfx"
                    }
            else:
                print(f"Arquivo de som não encontrado: {path}")
        
        self.load_voiced_dialogues()
        self._update_all_volumes()
    
    def load_voiced_dialogues(self):
        """Carrega os áudios dublados para eventos específicos."""
        dialogos_path = os.path.join(SOUND_PATH, "dialogos")
        if not os.path.exists(dialogos_path):
            print(f"Pasta de diálogos dublados não encontrada: {dialogos_path}")
            return
            
        eventos = {
            "colisao_1vida": ["uma_vida_1", "uma_vida_2", "uma_vida_3", "uma_vida_4", "uma_vida_5", 
                     "uma_vida_6", "uma_vida_7", "uma_vida_8", "uma_vida_9", "uma_vida_10"],
            "colisao_2vidas": ["duas_vidas_1", "duas_vidas_2", "duas_vidas_3", "duas_vidas_4", "duas_vidas_5", 
                      "duas_vidas_6", "duas_vidas_7", "duas_vidas_8", "duas_vidas_9", "duas_vidas_10"],
            "perdeu": ["perdeu_1", "perdeu_2", "perdeu_3", "perdeu_4", "perdeu_5", 
                  "perdeu_6", "perdeu_7", "perdeu_8", "perdeu_9", "perdeu_10"],
            "ganhou": ["ganhou_1", "ganhou_2", "ganhou_3", "ganhou_4", "ganhou_5", 
                  "ganhou_6", "ganhou_7", "ganhou_8", "ganhou_9", "ganhou_10"],
            "conclusao": ["conclusao_1", "conclusao_2", "conclusao_3", "conclusao_4", "conclusao_5"]
        }
        
        for evento, variacoes in eventos.items():
            self.sounds[evento] = []
            for variacao in variacoes:
                arquivo_path = os.path.join(dialogos_path, f"{variacao}.mp3")
                if os.path.exists(arquivo_path):
                    sound = pygame.mixer.Sound(arquivo_path)
                    self.sounds[evento].append({
                        "sound": sound,
                        "volume": self.voice_volume,
                        "name": variacao,
                        "type": "voice"
                    })
                else:
                    print(f"Arquivo de áudio dublado não encontrado: {arquivo_path}")
    
    def _update_all_volumes(self):
        """Atualiza os volumes de todos os canais com base nas configurações atuais."""
        if pygame.mixer.music.get_busy() and self._som_ligado:
            pygame.mixer.music.set_volume(self.bg_volume)
        else:
            pygame.mixer.music.set_volume(0)
            
        for channel in self.sfx_channels:
            channel.set_volume(self.sfx_volume if self._som_ligado else 0)
            
        for channel in self.voice_channels:
            channel.set_volume(self.voice_volume if self._som_ligado else 0)
    
    @property
    def som_ligado(self):
        return self._som_ligado
    
    @som_ligado.setter
    def som_ligado(self, value):
        """Define se o som está ativado ou desativado."""
        if self._som_ligado != value:
            self._som_ligado = value
            if not value:
                pygame.mixer.music.pause()
                for channel in self.sfx_channels + self.voice_channels:
                    channel.set_volume(0)
            else:
                if self.current_bg_music:
                    pygame.mixer.music.unpause()
                self._update_all_volumes()
    
    def _get_available_channel(self, channel_type="sfx"):
        """Obtém um canal disponível para reprodução."""
        channels = self.sfx_channels if channel_type == "sfx" else self.voice_channels
        
        for channel in channels:
            if not channel.get_busy():
                return channel
        
        if channel_type == "voice":
            self.current_voice_channel_index = (self.current_voice_channel_index + 1) % len(self.voice_channels)
            return self.voice_channels[self.current_voice_channel_index]
        else:
            return channels[0]
    
    def play_sound(self, sound_name):
        """Toca um efeito sonoro no canal de SFX."""
        if not self._som_ligado or sound_name not in self.sounds:
            return
        
        sound_info = self.sounds[sound_name]
        if "sound" not in sound_info:
            return
        
        channel_type = sound_info.get("type", "sfx")
        if channel_type != "voice":
            channel_type = "sfx"
        
        channel = self._get_available_channel(channel_type)
        
        volume = self.voice_volume if channel_type == "voice" else self.sfx_volume
        volume_adjusted = volume * sound_info.get("volume", 1.0)
        
        sound_info["sound"].set_volume(volume_adjusted)
        channel.play(sound_info["sound"])
    
    def play_background(self, sound_name="background"):
        """Inicia a reprodução da música de fundo."""
        if not self._som_ligado or sound_name not in self.sounds or "file" not in self.sounds[sound_name]:
            return
        
        pygame.mixer.music.stop()
        
        sound_info = self.sounds[sound_name]
        pygame.mixer.music.load(sound_info["file"])
        volume_adjusted = self.bg_volume * sound_info.get("volume", 1.0)
        pygame.mixer.music.set_volume(volume_adjusted)
        pygame.mixer.music.play(-1)
        self.current_bg_music = sound_name
    
    def stop_background(self):
        """Para a reprodução da música de fundo."""
        pygame.mixer.music.stop()
        self.current_bg_music = None
    
    def set_bg_volume(self, volume):
        """Ajusta o volume da música de fundo."""
        self.bg_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.music.get_busy() and self._som_ligado:
            pygame.mixer.music.set_volume(self.bg_volume)
    
    def set_music_volume(self, v):
        """Define o volume da música de fundo."""
        self.bg_volume = max(0.0, min(1.0, v))
        if pygame.mixer.music.get_busy() and self._som_ligado:
            pygame.mixer.music.set_volume(self.bg_volume)
    
    def set_sfx_volume(self, v):
        """Define o volume dos efeitos sonoros."""
        self.sfx_volume = max(0.0, min(1.0, v))
        for channel in self.sfx_channels:
            if self._som_ligado:
                channel.set_volume(self.sfx_volume)
    
    def set_voice_volume(self, v):
        """Define o volume das vozes."""
        self.voice_volume = max(0.0, min(1.0, v))
        for channel in self.voice_channels:
            if self._som_ligado:
                channel.set_volume(self.voice_volume)
    
    def set_sound_volume(self, sound_name, volume):
        """Define o volume de um som específico."""
        if sound_name not in self.sounds:
            return
        
        volume = max(0.0, min(1.0, volume))
        
        if isinstance(self.sounds[sound_name], list):
            for sound_info in self.sounds[sound_name]:
                sound_info["volume"] = volume
                if self.current_voiced_dialogue and self.current_voiced_dialogue.get("name") == sound_info.get("name"):
                    sound_info["sound"].set_volume(volume * self.voice_volume if self._som_ligado else 0)
        else:
            self.sounds[sound_name]["volume"] = volume
            
            if sound_name == self.current_bg_music and "file" in self.sounds[sound_name]:
                pygame.mixer.music.set_volume(volume * self.bg_volume if self._som_ligado else 0)
    
    def stop_voiced_dialogue(self):
        """Para a reprodução do diálogo atual se houver algum."""
        for channel in self.voice_channels:
            channel.stop()
        self.current_voiced_dialogue = None
    
    def play_voiced_dialogue(self, evento):
        """Reproduz aleatoriamente uma das variações de áudio dublado para um evento."""
        if not self._som_ligado or evento not in self.sounds or not isinstance(self.sounds[evento], list) or not self.sounds[evento]:
            return False
        
        self.stop_voiced_dialogue()
        
        variacao = random.choice(self.sounds[evento])
        if "sound" not in variacao:
            return False
        
        channel = self._get_available_channel("voice")
        
        sound = variacao["sound"]
        volume_adjusted = self.voice_volume * variacao.get("volume", 1.0)
        sound.set_volume(volume_adjusted)
        channel.play(sound)
        
        self.current_voiced_dialogue = variacao
        return True

# Crie uma instância única do gerenciador de áudio
audio_manager = AudioManager()
