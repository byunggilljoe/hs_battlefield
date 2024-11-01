from unit import Unit
import random
import math
from particle import Particle
import pygame
from constants import BLUE

class AttackBuffer(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=300):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "AttackBuffer"
        self.image_path = "assets/attack_buffer.png"  # 이미지 경로 설정
        self.load_image()
        
    def draw(self, screen):
        # 버프 효과를 나타내는 붉은색 테두리
        buff_thickness = 15
        buff_surface = pygame.Surface((50 + buff_thickness, 100 + buff_thickness), pygame.SRCALPHA)
        # 붉은색 테두리로 변경
        pygame.draw.rect(buff_surface, (255, 99, 71, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                       (0, 0, 50 + buff_thickness, 100 + buff_thickness))
        screen.blit(buff_surface, (self.x - buff_thickness//2, self.y - buff_thickness//2))
        
        # 기본 유닛 그리기
        super().draw(screen)
    
    def on_start_move(self, moving_unit, target_unit, player_units, enemy_units):
        """
        아군이 공격할 때 호출되는 메서드
        공격하는 아군의 공격력을 +3 증가시킴
        """
        # 공격하는 유닛이 아군이고, 자신일 경우에만 버프 적용
        if moving_unit == self:
            moving_unit.attack *=2  # 공격력 *2 
            self.create_buff_particles(moving_unit.x, moving_unit.y)

    def create_buff_particles(self, x, y):
        """버프 효과를 시각적으로 표시하는 파티클 생성"""
        buff_colors = [(255, 99, 71), (255, 69, 0), (255, 140, 0)]  # 붉은색/주황색 계열
        
        for _ in range(10):
            particle_x = x + 25 + random.uniform(-20, 20)
            particle_y = y + 50 + random.uniform(-20, 20)
            
            angle = random.uniform(0, 2 * math.pi)
            self.particles.append(
                Particle(
                    particle_x,
                    particle_y,
                    random.choice(buff_colors),
                    angle,
                    speed_multiplier=0.5,
                    size_range=(3, 6)
                )
            ) 