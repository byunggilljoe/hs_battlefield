from unit import Unit
from units.warlord import Warlord
import random
import pygame
class Barracks(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=300):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Barracks"
        self.taunt = True
        self.image_path = "images/units/barracks.png"
        self.load_image()
        
    def on_death(self, dead_unit, player_units, enemy_units):
        if self is not dead_unit:
            return
            
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

        super().on_death(dead_unit, player_units, enemy_units)
