from unit import Unit
from units.warlord import Warlord
import random
import pygame
class Barracks(Unit):
    def __init__(self, x, y, health, attack, color, game_state):
        super().__init__(x, y, health, attack, color, game_state)
        self.name = "Barracks"
        self.taunt = True
        
    def draw(self, screen):
        # 도발 상태를 나타내는 회색 rect를 먼저 그림
        taunt_thickness = 15
        taunt_surface = pygame.Surface((50 + taunt_thickness, 100 + taunt_thickness), pygame.SRCALPHA)
        pygame.draw.rect(taunt_surface, (128, 128, 128, self.fade_alpha if self.fading and self.ready_to_fade else 255), 
                       (0, 0, 50 + taunt_thickness, 100 + taunt_thickness))
        screen.blit(taunt_surface, (self.x - taunt_thickness//2, self.y - taunt_thickness//2))
        
        # 기본 유닛 그리기
        super().draw(screen)

    def on_death(self):
            
        # 자신이 속한 팀을 확인
        if self in self.game_state['player_units']:
            team_units = self.game_state['player_units']
        else:
            team_units = self.game_state['enemy_units']
        
        # 자신의 인덱스를 찾음
        index = team_units.index(self)
        
        # 새로운 Warlord 유닛 생성
        new_warlord = Warlord(self.x, self.y, 
                            random.randint(40, 60),  # health
                            random.randint(12, 18),  # attack
                            self.color, 
                            self.game_state)
        
        # 생성된 Warlord를 자신의 위치에 추가
        team_units.insert(index+1, new_warlord)
        
        # on_spawn 호출하여 전장의 함성 효과 발동
        new_warlord.on_spawn(self.game_state['player_units'], 
                            self.game_state['enemy_units'])
        self.game_state["adjusting_positions"] = True

        super().on_death()
