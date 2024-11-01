from unit import Unit
from units.venom import Venom
import random
import pygame
import math

class Phoenix(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=400):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Phoenix"

    def on_death(self, dead_unit, player_units, enemy_units):
        print("Phoenix on_death called.")
        if self is not dead_unit:
            return  
        super().on_death(dead_unit, player_units, enemy_units)

        
        # 자신이 속한 팀을 확인
        if self in self.game_state['player_units']:
            team_units = self.game_state['player_units']
        else:
            team_units = self.game_state['enemy_units']
        
        # 자신의 인덱스를 찾음
        index = team_units.index(self)
        
        # 새로운 Healer 유닛 생성
        for i in range(3):
            new_venom = Venom(self.x, self.y, random.randint(30, 50), random.randint(5, 15), self.color, self.game_state)
            
            # 생성된 Healer를 자신의 위치에 추가
            team_units.insert(index+1, new_venom)
        self.game_state["adjusting_positions"] = True
        print(f"Phoenix died at ({self.x}, {self.y}). New Venom spawned!")

    def draw(self, screen):
        # 기본 유닛 그리기
        super().draw(screen)
        
        # 해골 크기와 위치 설정 (크기 증가)
        skull_size = 20  # 12에서 20으로 증가
        skull_x = self.x + 25 - skull_size // 2
        skull_y = self.y + 5  # 위치 약간 위로 조정
        
        # 해골 머리 (타원형) 그리기
        pygame.draw.ellipse(screen, (255, 255, 255), 
                          (skull_x, skull_y, skull_size, skull_size + 4), 2)
        
        # 눈 그리기 (검은 타원형)
        eye_width = 6
        eye_height = 8
        left_eye_x = skull_x + skull_size//4
        right_eye_x = skull_x + 3*skull_size//4 - eye_width//2
        eye_y = skull_y + skull_size//3
        
        # 눈 테두리
        pygame.draw.ellipse(screen, (255, 255, 255), 
                          (left_eye_x, eye_y, eye_width, eye_height))
        pygame.draw.ellipse(screen, (255, 255, 255), 
                          (right_eye_x, eye_y, eye_width, eye_height))
        
        # 코 그리기 (역삼각형)
        nose_y = eye_y + eye_height + 2
        pygame.draw.polygon(screen, (255, 255, 255), [
            (skull_x + skull_size//2, nose_y),
            (skull_x + skull_size//2 - 4, nose_y + 6),
            (skull_x + skull_size//2 + 4, nose_y + 6)
        ])
        
        # 이빨이 있는 턱 그리기
        jaw_y = skull_y + skull_size - 2
        # 턱 기본 모양
        pygame.draw.arc(screen, (255, 255, 255),
                       (skull_x, jaw_y, skull_size, skull_size//2),
                       0, math.pi, 2)
        
        # 이빨 그리기 (위쪽)
        teeth_count = 4
        teeth_width = skull_size // (teeth_count * 2)
        for i in range(teeth_count):
            tooth_x = skull_x + (i * 2 + 1) * teeth_width
            pygame.draw.line(screen, (255, 255, 255),
                           (tooth_x, jaw_y + 2),
                           (tooth_x, jaw_y + 6))
