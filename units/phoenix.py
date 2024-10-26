from unit import Unit
from units.venom import Venom
import random

class Phoenix(Unit):
    def __init__(self, x, y, health, attack, color, game_state):
        super().__init__(x, y, health, attack, color, game_state)
        self.name = "Phoenix"

    def on_death(self):
        print("Phoenix on_death called.")  
        super().on_death()

        
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
