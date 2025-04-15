import pygame
from utils.audio_manager import audio_manager
from utils.drawing import resize
import os

class Button:
    def __init__(self, x, y, width, height, text, font, text_color=(255, 255, 255),
                 bg_color=(100, 100, 100), hover_color=(150, 150, 150), border_radius=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.is_hovered = False
        self.was_hovered = False
        self.border_radius = border_radius
        self.image = None
    
    def set_image(self, image_path):
        """Define uma imagem de fundo para o botão"""
        if image_path and os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
    
    def draw(self, surface):
        # Determina a cor com base no estado hover
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Desenhar fundo do botão
        if self.image:
            surface.blit(self.image, self.rect)
            # Adiciona brilho ao passar o mouse
            if self.is_hovered:
                glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
                glow.fill((255, 255, 255, 30))
                surface.blit(glow, self.rect)
        else:
            pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=self.border_radius)
        
        # Renderizar texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        # Verifica se o mouse está sobre o botão
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Tocar som de hover apenas quando o mouse entra no botão
        if self.is_hovered and not was_hovered:
            audio_manager.play_sound("hover")
        
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                audio_manager.play_sound("click")
                return True
        return False
