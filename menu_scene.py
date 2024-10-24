import pygame
from scene import Scene

class MenuScene(Scene):
    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 74)
        self.start_button_rect = pygame.Rect(300, 250, 200, 100)

    def update(self):
        pass  # No update logic needed for a static menu

    def draw(self, screen):
        screen.fill((255, 255, 255))  # Fill the screen with white

        # Draw the "Start" button
        pygame.draw.rect(screen, (0, 0, 255), self.start_button_rect)
        text = self.font.render("Start", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.start_button_rect.center)
        screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(event.pos):
                from battle_scene import BattleScene
                self.scene_manager.set_scene(BattleScene())
