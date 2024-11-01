from unit import Unit
import random
import math
from particle import Particle
import pygame

class Venom(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=350):
        super().__init__(x, y, health, attack, color, game_state, cost)  # 고정된 스탯 사용
        self.name = "Venom"
        self.venom_charges = 3
        self.poison_particle_timer = 0
        self.image_path = "images/units/venom.png"
        self.load_image()
    def draw(self, screen):
        # 독 상태를 나타내는 녹색 rect를 먼저 그림
        venom_thickness = 15
        venom_surface = pygame.Surface((50 + venom_thickness, 100 + venom_thickness), pygame.SRCALPHA)
        pygame.draw.rect(venom_surface, (0, 128, 0, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                       (0, 0, 50 + venom_thickness, 100 + venom_thickness))
        screen.blit(venom_surface, (self.x - venom_thickness//2, self.y - venom_thickness//2))
        
        # 기본 유닛 그리기
        super().draw(screen)
        
        # 독 기운 파티클 생성
        self.poison_particle_timer += 1
        if self.poison_particle_timer >= 5:  # 5프레임마다 파티클 생성
            self.create_ambient_poison_particles()
            self.poison_particle_timer = 0
            
    def create_ambient_poison_particles(self):
        poison_colors = [
            (0, 100, 0),  # 어두운 녹색
            (0, 120, 0),  # 중간 녹색
            (0, 140, 0)   # 약간 밝은 녹색
        ]
        
        # 유닛 아래에서 2-3개의 파티클 생성
        for _ in range(random.randint(2, 3)):
            # x 위치는 유닛 너비 내에서 랜덤
            particle_x = self.x + random.uniform(0, 50)
            # y 위치는 유닛 바닥에서 시작
            particle_y = self.y + 100
            
            # 위로 올라가는 방향 (약간의 좌우 흔들림 포함)
            angle = -math.pi/2 + random.uniform(-0.2, 0.2)  # -90도 ± 약 11도
            
            self.particles.append(
                Particle(
                    particle_x, 
                    particle_y,
                    random.choice(poison_colors),
                    angle,
                    speed_multiplier=0.7,  # 천천히 올라가도록 속도 조절
                    size_range=(3, 5)  # 작은 크기의 파티클
                )
            )
    
    def on_spawn(self, spawned_unit, player_units, enemy_units):
        if spawned_unit is not self:
            return
        # 독 충전량 초기화
        self.venom_charges = 3  # 3번의 즉사 독 사용 가능
        
    def on_attack(self, attacker, target, player_units, enemy_units):
        if self.venom_charges > 0:
            # 독 사용 시 대상 즉시 처치
            target.update_health(0)  # 체력을 0으로 만듦
            self.venom_charges -= 1
            
            # 독 효과를 표현하는 초록색 파티클 생성
            self.create_poison_particles(target.x, target.y)
            
    def apply_damage(self, target_unit):
        target_unit.update_health(0)
        
    def create_poison_particles(self, x, y):
        poison_color = (0, 140, 0)  # 공격 시 파티클은 좀 더 밝은 녹색
        for _ in range(30):
            particle_x = x + random.uniform(-20, 20)
            particle_y = y + random.uniform(-20, 20)
            self.particles.append(Particle(particle_x, particle_y, poison_color, 
                                        random.uniform(0, 2*math.pi), 
                                        speed_multiplier=1.5, 
                                        size_range=(4, 10)))
