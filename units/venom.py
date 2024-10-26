from unit import Unit
import random
import math
from particle import Particle

class Venom(Unit):
    def __init__(self, x, y, health, attack, color, game_state):
        super().__init__(x, y, health, attack, color, game_state)  # 고정된 스탯 사용
        self.name="Venom"
        self.venom_charges = 3
        
    def on_spawn(self, player_units, enemy_units):
        # 독 충전량 초기화
        self.venom_charges = 3  # 3번의 즉사 독 사용 가능
        
    def on_attack(self, target, player_units, enemy_units):
        if self.venom_charges > 0:
            # 독 사용 시 대상 즉시 처치
            target.update_health(0)  # 체력을 0으로 만듦
            self.venom_charges -= 1
            
            # 독 효과를 표현하는 초록색 파티클 생성
            self.create_poison_particles(target.x, target.y)
            
    def apply_damage(self, target_unit):
        target_unit.update_health(0)
        
    def create_poison_particles(self, x, y):
        poison_color = (0, 255, 0)  # 초록색
        for _ in range(30):
            particle_x = x + random.uniform(-20, 20)
            particle_y = y + random.uniform(-20, 20)
            self.particles.append(Particle(particle_x, particle_y, poison_color, 
                                        random.uniform(0, 2*math.pi), 
                                        speed_multiplier=1.5, 
                                        size_range=(4, 10)))
