import pygame
from scene import Scene
from battle_scene import BattleScene
from constants import WIDTH, HEIGHT, BLUE, RED
from units.venom import Venom
from units.splash import Splash
from units.healer import Healer
from units.phoenix import Phoenix
from units.bomber import Bomber
from units.tank import Tank
from constants import PLAYER_Y
from game_state import game_state, reset_game_state

class ShopScene(Scene):
    def __init__(self, scene_manager, previous_units=None, previous_gold=None):
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.gold = previous_gold if previous_gold is not None else 1000
        
        # 구매 가능한 유닛들과 가격
        self.available_units = [
            {"type": Tank, "name": "Tank", "cost": 300, "health": 100, "attack": 10},
            {"type": Healer, "name": "Healer", "cost": 250, "health": 50, "attack": 15},
            {"type": Phoenix, "name": "Phoenix", "cost": 400, "health": 60, "attack": 20},
            {"type": Venom, "name": "Venom", "cost": 350, "health": 40, "attack": 25},
            {"type": Bomber, "name": "Bomber", "cost": 300, "health": 45, "attack": 15}
        ]
        
        # 이전 유닛들이 있으면 복원
        print("---previous_units:", previous_units)
        self.selected_units = previous_units if previous_units is not None else []
        
        # 버튼 위치 설정
        self.unit_buttons = []
        for i, unit in enumerate(self.available_units):
            button_rect = pygame.Rect(50, 150 + i * 80, 200, 60)
            self.unit_buttons.append({"rect": button_rect, "unit": unit})
            
        self.start_button = pygame.Rect(WIDTH - 250, HEIGHT - 100, 200, 60)

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # 제목 그리기
        title = self.title_font.render("Shop", True, (0, 0, 0))
        screen.blit(title, (WIDTH/2 - title.get_rect().width/2, 50))
        
        # 골드 표시
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (WIDTH - 200, 50))
        
        # 유닛 버튼 그리기
        for button in self.unit_buttons:
            unit = button["unit"]
            rect = button["rect"]
            
            # 버튼 배경
            pygame.draw.rect(screen, (200, 200, 200), rect)
            
            # 유닛 정보 텍스트
            name_text = self.font.render(f"{unit['name']}", True, (0, 0, 0))
            cost_text = self.font.render(f"{unit['cost']}G", True, (255, 215, 0))
            stats_text = self.font.render(f"HP:{unit['health']} ATK:{unit['attack']}", True, (0, 0, 0))
            
            screen.blit(name_text, (rect.x + 10, rect.y + 5))
            screen.blit(cost_text, (rect.x + rect.width - 70, rect.y + 5))
            screen.blit(stats_text, (rect.x + 10, rect.y + 30))
        
        # 선택된 유닛 표시
        selected_text = self.font.render("Selected Units:", True, (0, 0, 0))
        screen.blit(selected_text, (WIDTH - 300, 150))
        
        for i, unit in enumerate(self.selected_units):
            unit_text = self.font.render(f"- {unit['name']}", True, (0, 0, 0))
            screen.blit(unit_text, (WIDTH - 280, 190 + i * 30))
        
        # 시작 버튼
        pygame.draw.rect(screen, (0, 200, 0), self.start_button)
        start_text = self.font.render("Start Battle", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button.center)
        screen.blit(start_text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 유닛 구매 버튼 클릭 처리
            for button in self.unit_buttons:
                if button["rect"].collidepoint(event.pos):
                    unit = button["unit"]
                    if self.gold >= unit["cost"] and len(self.selected_units) < 4:
                        self.gold -= unit["cost"]
                        self.selected_units.append(unit)
            
            # 전투 시작 버튼 클릭 처리
            if self.start_button.collidepoint(event.pos) and self.selected_units:
                reset_game_state(game_state)
                player_units = []
                
                # 선택된 유닛들로 플레이어 유닛 초기화 (위치 조정)
                player_positions = [(100, PLAYER_Y), (200, PLAYER_Y), 
                                  (300, PLAYER_Y), (400, PLAYER_Y)]
                
                for i, unit in enumerate(self.selected_units):
                    player_unit = unit["type"](
                        x=player_positions[i][0],
                        y=player_positions[i][1],
                        health=unit["health"],
                        attack=unit["attack"],
                        color=BLUE,
                        game_state=game_state
                    )
                    player_units.append(player_unit)
                battle_scene = BattleScene(self.scene_manager, self, player_units)

                self.scene_manager.set_scene(battle_scene)
