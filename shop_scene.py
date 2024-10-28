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
        self.gold = previous_gold if previous_gold is not None else 5000
        
        # 구매 가능한 유닛들과 가격
        self.available_units = [
            {"type": Tank, "name": "Tank", "cost": 300, "health": 100, "attack": 10},
            {"type": Healer, "name": "Healer", "cost": 250, "health": 50, "attack": 15},
            {"type": Phoenix, "name": "Phoenix", "cost": 400, "health": 60, "attack": 20},
            {"type": Venom, "name": "Venom", "cost": 350, "health": 40, "attack": 25},
            {"type": Bomber, "name": "Bomber", "cost": 300, "health": 20, "attack": 15}
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

        # 선택된 유닛 버튼 영역 설정
        self.selected_unit_buttons = []
        self.update_selected_unit_buttons()

        # 드래그 앤 드롭 관련 변수 추가
        self.dragging = False
        self.drag_unit_index = None
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.mouse_moved = False  # 마우스 이동 여부를 추적하는 변수 추가

    def update(self):
        pass
    
    def update_selected_unit_buttons(self):
        # 선택된 유닛들의 버튼 위치 업데이트
        self.selected_unit_buttons = []
        for i, unit in enumerate(self.selected_units):
            button_rect = pygame.Rect(WIDTH - 280, 190 + i * 60, 250, 50)
            self.selected_unit_buttons.append({"rect": button_rect, "unit": unit})

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
        selected_text = self.font.render("Selected Units (drag to reorder):", True, (0, 0, 0))
        screen.blit(selected_text, (WIDTH - 300, 150))
        
        small_font = pygame.font.Font(None, 24)
        
        # 드래그 중인 유닛이 아닌 경우에만 마우스 오버 효과 표시
        for i, unit in enumerate(self.selected_units):
            if self.dragging and i == self.drag_unit_index:
                continue
                
            y_pos = 190 + i * 60
            button_rect = pygame.Rect(WIDTH - 280, y_pos, 250, 50)
            
            # 마우스 오버 효과 (드래그 중이 아닐 때만)
            if not self.dragging and button_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (240, 240, 240), button_rect)
                sell_price = int(unit["cost"] * 0.8)
                hint_text = self.font.render(f"Click to sell for {sell_price}G", True, (100, 100, 100))
                screen.blit(hint_text, (button_rect.right + 10, button_rect.centery - 10))
            
            self.draw_unit_slot(screen, unit, y_pos, small_font)
        
        # 드래그 중인 유닛 표시
        if self.dragging and self.drag_unit_index is not None:
            mouse_pos = pygame.mouse.get_pos()
            drag_y = mouse_pos[1] - 25
            self.draw_unit_slot(screen, self.selected_units[self.drag_unit_index], 
                              drag_y, small_font, True)

        # 시작 버튼
        pygame.draw.rect(screen, (0, 200, 0), self.start_button)
        start_text = self.font.render("Start Battle", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button.center)
        screen.blit(start_text, text_rect)

    def draw_unit_slot(self, screen, unit, y_pos, small_font, is_dragging=False):
        # 유닛 슬롯 그리기 함수
        sell_price = int(unit["cost"] * 0.8)
        
        # 배경 rect
        button_rect = pygame.Rect(WIDTH - 280, y_pos, 250, 50)
        if is_dragging:
            pygame.draw.rect(screen, (230, 230, 250), button_rect)  # 드래그 중일 때 다른 색상
        elif button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, (240, 240, 240), button_rect)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
        
        # 텍스트 정보
        unit_name = self.font.render(f"- {unit['name']}", True, (0, 0, 0))
        unit_price = small_font.render(f"Sell: {sell_price}G", True, (100, 100, 100))
        unit_stats = small_font.render(f"HP: {unit['health']} | ATK: {unit['attack']}", 
                                     True, (50, 50, 50))
        
        screen.blit(unit_name, (WIDTH - 280, y_pos))
        screen.blit(unit_price, (WIDTH - 280, y_pos + 25))
        screen.blit(unit_stats, (WIDTH - 180, y_pos + 25))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭
                # 선택된 유닛 영역 확인
                mouse_pos = event.pos
                for i, button in enumerate(self.selected_unit_buttons):
                    if button["rect"].collidepoint(mouse_pos):
                        self.dragging = True
                        self.drag_unit_index = i
                        self.drag_start_pos = mouse_pos
                        self.mouse_moved = False  # 마우스 이동 초기화
                        return
                
                # 구매 버튼 처리
                for button in self.unit_buttons:
                    if button["rect"].collidepoint(event.pos):
                        unit = button["unit"]
                        if self.gold >= unit["cost"] and len(self.selected_units) < 4:
                            self.gold -= unit["cost"]
                            self.selected_units.append(unit)
                            self.update_selected_unit_buttons()
                
                # 전투 시작 버튼 처리
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
            
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.mouse_moved = True  # 마우스가 움직였음을 표시
                self.drag_current_pos = event.pos
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:  # 드래그 종료
                if self.mouse_moved:  # 드래그 했을 경우
                    drop_pos = event.pos
                    new_index = self.get_drop_index(drop_pos)
                    
                    if new_index is not None and new_index != self.drag_unit_index:
                        # 유닛 순서 변경
                        unit = self.selected_units.pop(self.drag_unit_index)
                        self.selected_units.insert(new_index, unit)
                        self.update_selected_unit_buttons()
                else:  # 클릭만 했을 경우 (판매)
                    sold_unit = self.selected_units[self.drag_unit_index]
                    sell_price = int(sold_unit["cost"] * 0.8)  # 구매가의 80%로 판매
                    self.gold += sell_price
                    self.selected_units.pop(self.drag_unit_index)
                    self.update_selected_unit_buttons()
                
                # 드래그 상태 초기화
                self.dragging = False
                self.drag_unit_index = None
                self.drag_start_pos = None
                self.drag_current_pos = None
                self.mouse_moved = False

    def get_drop_index(self, pos):
        # 드롭 위치에 해당하는 인덱스 계산
        if WIDTH - 280 <= pos[0] <= WIDTH - 30:  # x 좌표가 유닛 목록 영역 안에 있는지 확인
            relative_y = pos[1] - 190  # 첫 번째 슬롯 위치 기준
            if relative_y >= 0:
                new_index = relative_y // 60  # 슬롯 높이로 나누어 인덱스 계산
                return min(new_index, len(self.selected_units) - 1)
        return None
