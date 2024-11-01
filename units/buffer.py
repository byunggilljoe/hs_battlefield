from unit import Unit
import random
import math
from particle import Particle
import pygame

class Buffer(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=350):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Buffer"
        
    def draw(self, screen):
        # 버프 효과를 나타내는 황금색 테두리
        buff_thickness = 15
        buff_surface = pygame.Surface((50 + buff_thickness, 100 + buff_thickness), pygame.SRCALPHA)
        pygame.draw.rect(buff_surface, (218, 165, 32, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                       (0, 0, 50 + buff_thickness, 100 + buff_thickness))
        screen.blit(buff_surface, (self.x - buff_thickness//2, self.y - buff_thickness//2))
        
        # 기본 유닛 그리기
        super().draw(screen)
        
    def on_spawn(self, spawned_unit, player_units, enemy_units):
        if spawned_unit is not self:
            return
        # 같은 팀의 유닛들 찾기
        
        if self in player_units:
            team_units = player_units
        else:
            team_units = enemy_units
            
        # 자신을 제외한 팀 유닛들 중 랜덤하게 3개 선택
        available_units = [unit for unit in team_units if unit != self]
        units_to_buff = random.sample(available_units, min(3, len(available_units)))
        
        # 선택된 유닛들의 공격력 2배로 증가
        for unit in units_to_buff:
            unit.attack *= 2
            self.create_buff_particles(unit.x, unit.y)
    
    def create_buff_particles(self, x, y):
        buff_colors = [(218, 165, 32), (255, 215, 0), (255, 223, 0)]  # 황금색 계열
        
        for _ in range(20):
            particle_x = x + 25 + random.uniform(-30, 30)
            particle_y = y - 20 + random.uniform(-10, 10)
            
            angle = math.pi/2 + random.uniform(-0.1, 0.1)
            self.particles.append(
                Particle(
                    particle_x,
                    particle_y,
                    random.choice(buff_colors),
                    angle,
                    speed_multiplier=0.8,
                    size_range=(4, 8)
                )
            ) 