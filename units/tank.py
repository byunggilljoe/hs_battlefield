from unit import Unit
import pygame

class Tank(Unit):
    def __init__(self, x, y, health, attack, color, game_state):
        super().__init__(x, y, health, attack, color, game_state)
        self.name = "Tank"
        self.taunt = True
    
    def draw(self, screen):
        # 도발 상태를 나타내는 회색 rect를 먼저 그림 (유닛 rect보다 약간 더 크게)
        if self.taunt:
            taunt_thickness = 15
            taunt_surface = pygame.Surface((50 + taunt_thickness, 100 + taunt_thickness), pygame.SRCALPHA)
            pygame.draw.rect(taunt_surface, (128, 128, 128, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                           (0, 0, 50 + taunt_thickness, 100 + taunt_thickness))
            screen.blit(taunt_surface, (self.x - taunt_thickness//2, self.y - taunt_thickness//2))  # 유닛 rect보다 약간 더 크게
        
        # 기본 유닛 그리기 (회색 rect 위에 그려짐)
        super().draw(screen)
