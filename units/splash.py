from unit import Unit
import random
import math
from particle import Particle

class Splash(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=300):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name="Splash"
        
    def on_attack(self, target, player_units, enemy_units):
        # 타겟이 적군인지 아군인지에 따라 공격할 유닛 리스트 선택
        target_units = enemy_units if target in enemy_units else player_units
        
        # 타겟의 인덱스 찾기
        target_index = target_units.index(target)
        
        # 공격할 유닛들의 인덱스 계산 (타겟 및 양옆 유닛)
        attack_indices = [
            i for i in [target_index - 1, target_index + 1]
            if 0 <= i < len(target_units)
        ]
        
        # 해당하는 모든 유닛 공격
        print(f"Splash attack_indices: {attack_indices}")
        for idx in attack_indices:
            unit = target_units[idx]
            unit.update_health(unit.health - self.attack)
            
            # 공격 효과를 표현하는 파티클 생성
            self.create_splash_particles(unit.x + 25, unit.y + 50)  # 유닛의 중앙에서 파티클 생성
    
    def create_splash_particles(self, x, y):
        splash_color = (255, 165, 0)  # 주황색
        for _ in range(15):
            particle_x = x + random.uniform(-15, 15)
            particle_y = y + random.uniform(0, 30)  # 아래쪽으로만 퍼지도록 조정
            direction = random.uniform(math.pi/2, 3*math.pi/2)  # 아래쪽 방향으로 제한 (90도에서 270도 사이)
            self.particles.append(Particle(particle_x, particle_y, splash_color,
                                        direction,
                                        speed_multiplier=1.8,
                                        size_range=(5, 12)))
