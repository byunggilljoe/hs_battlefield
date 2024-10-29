from unit import Unit
import random
import math
from particle import Particle
import pygame

class Warlord(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=350):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Warlord"
        self.battle_cry = True
        
    def draw(self, screen):
        # 전장의 함성 특성을 나타내는 붉은 테두리
        cry_thickness = 15
        cry_surface = pygame.Surface((50 + cry_thickness, 100 + cry_thickness), pygame.SRCALPHA)
        pygame.draw.rect(cry_surface, (200, 50, 50, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                       (0, 0, 50 + cry_thickness, 100 + cry_thickness))
        screen.blit(cry_surface, (self.x - cry_thickness//2, self.y - cry_thickness//2))
        
        # 기본 유닛 그리기
        super().draw(screen)
        
    def on_spawn(self, player_units, enemy_units):
        # 같은 팀의 모든 유닛 공격력 증가
        if self in player_units:
            team_units = player_units
        else:
            team_units = enemy_units
            
        # 전장의 함성 효과: 모든 아군 유닛의 공격력 25% 증가
        for unit in team_units:
            if unit != self:  # 자신 제외
                unit.attack = int(unit.attack * 2)
                self.create_battle_cry_particles(unit.x, unit.y)
    
    def create_battle_cry_particles(self, x, y):
        cry_colors = [(128, 30, 30), (128, 50, 50), (128, 70, 70)]  # 더 붉은 계열
        
        for _ in range(20):
            particle_x = x + 25 + random.uniform(-30, 30)
            particle_y = y - 20 + random.uniform(-10, 10)  # 유닛 위쪽에서 시작
            
            # 아래 방향으로 떨어지는 각도 설정 (π/2는 아래 방향)
            angle = math.pi/2 + random.uniform(-0.1, 0.1)  # 약간의 무작위성 추가
            self.particles.append(
                Particle(
                    particle_x,
                    particle_y,
                    random.choice(cry_colors),
                    angle,
                    speed_multiplier=0.8,  # 속도를 좀 더 느리게
                    size_range=(4, 8)
                )
            )
