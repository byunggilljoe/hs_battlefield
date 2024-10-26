from unit import Unit
import random
import math
from particle import Particle

class Healer(Unit):
    def __init__(self, x, y, health, attack, color):
        super().__init__(x, y, health, attack, color)

        
    def on_start_move(self):
        self.health = self.health * 2
        # 힐링 효과를 표현하는 파티클 생성
        self.create_heal_particles()
            
            
    def create_heal_particles(self):
        heal_color = (255, 223, 186)  # 밝은 노란색
        for _ in range(20):
            particle_x = self.x + random.uniform(-20, 20)
            particle_y = self.y + random.uniform(-20, 20)
            self.particles.append(Particle(particle_x, particle_y, heal_color,
                                        random.uniform(0, 2*math.pi),
                                        speed_multiplier=1.2,
                                        size_range=(4, 8)))