from unit import Unit
import random
import math
from particle import Particle
import pygame
from constants import BLUE

class Necromancer(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=400):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Necromancer"
        self.image_path = "assets/necromancer.png"
        self.load_image()
        self.dead_allies = []  # 죽은 아군 유닛을 저장할 리스트
        
    def on_death(self, dead_unit, player_units, enemy_units):
        """
        유닛이 죽었을 때 호출되는 메서드
        - 자신이 아닌 아군이 죽었을 때: dead_allies 리스트에 추가
        - 자신이 죽었을 때: dead_allies에 있는 모든 유닛을 부활
        """
        # 죽은 유닛이 아군이고 자신이 아닐 경우
        alley_units = player_units if self in player_units else enemy_units

        if dead_unit in alley_units and dead_unit != self:
            self.dead_allies.append(dead_unit)
            # self.create_death_particles(dead_unit.x, dead_unit.y)
            
        # 자신이 죽었을 경우
        elif dead_unit == self:
            # 모든 죽은 아군을 부활
            print(f"부활 시작: {self.dead_allies}")
            for ally in self.dead_allies:
                self.revive_unit(ally, alley_units)
            print(f"부활 후 아군 유닛: {alley_units}")
            self.dead_allies.clear()  # 부활 후 리스트 비우기
            self.game_state["initial_adjustment"] = True
    
    def revive_unit(self, ally, alley_units):
        ally.health = 1  # 체력 1로 부활
        ally.dead = False
        ally.exploded = False
        ally.fade_alpha = 50
        ally.fading = False
        ally.ready_to_fade = False
        alley_units.append(ally)
        self.create_revival_particles(ally.x, ally.y)
        
    def create_death_particles(self, x, y):
        """죽은 아군 흡수 효과를 나타내는 파티클"""
        death_colors = [(128, 0, 128), (75, 0, 130), (106, 90, 205)]  # 보라색 계열
        
        for _ in range(8):
            particle_x = x + 25 + random.uniform(-20, 20)
            particle_y = y + 50 + random.uniform(-20, 20)
            
            angle = math.atan2(self.y - y, self.x - x)  # 네크로맨서 방향으로 향하는 각도
            self.particles.append(
                Particle(
                    particle_x,
                    particle_y,
                    random.choice(death_colors),
                    angle,
                    speed_multiplier=0.7,
                    size_range=(3, 6)
                )
            )

    def create_revival_particles(self, x, y):
        """부활 효과를 나타내는 파티클"""
        revival_colors = [(0, 255, 0), (144, 238, 144), (152, 251, 152)]  # 초록색 계열
        
        for _ in range(12):
            particle_x = x + 25 + random.uniform(-20, 20)
            particle_y = y + 50 + random.uniform(-20, 20)
            
            angle = random.uniform(0, 2 * math.pi)
            self.particles.append(
                Particle(
                    particle_x,
                    particle_y,
                    random.choice(revival_colors),
                    angle,
                    speed_multiplier=0.6,
                    size_range=(4, 8)
                )
            ) 