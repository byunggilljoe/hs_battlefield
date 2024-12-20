from unit import Unit
import random
import math
from particle import Particle
import game_logic
class Bomber(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=300):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Bomber"
        self.exploded = False
        self.bomb_damage = 10
        self.image_path = "images/units/bomber.png"
        self.load_image()

    def on_death(self, dead_unit, player_units, enemy_units):
        # 죽은 유닛이 자신일 때만 폭발 효과 적용
        if dead_unit == self and not self.exploded:
            self.exploded = True
            # 자신이 속한 팀 확인
            if self in player_units:
                target_units = enemy_units
            else:
                target_units = player_units
            
            # 모든 적 유닛의 체력을 감소시키고 해당 위치에 폭발 효과 생성
            for unit in target_units:
                if not unit.dead:
                    unit.update_health(unit.health - self.bomb_damage)
                    self.create_explosion_particles(unit.x, unit.y)
            game_logic.handle_death(target_units)
        
        super().on_death(dead_unit, player_units, enemy_units)
    
    def create_explosion_particles(self, target_x, target_y):
        explosion_colors = [(255, 165, 0), (255, 69, 0), (255, 0, 0)]  # 주황색, 붉은 주황색, 빨간색
        for _ in range(30):  # 각 유닛당 파티클 수 조정
            color = random.choice(explosion_colors)
            particle_x = target_x + 25 + random.uniform(-20, 20)  # 유닛 중심 기준
            particle_y = target_y + 50 + random.uniform(-20, 20)  # 유닛 중심 기준
            self.particles.append(Particle(
                particle_x, 
                particle_y, 
                color,
                random.uniform(0, 2*math.pi),
                speed_multiplier=1.5,
                size_range=(10, 30)
            ))
