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
import math

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

        # 판매 영역 추가
        self.sell_zone = pygame.Rect(50, 150, 150, HEIGHT - 250)
        self.sell_zone_active = False  # 드래그 중일 때 판매 영역 활성화 상태

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
        
        # 드래그 중이 아닌 유닛들 먼저 그리기
        for i, unit in enumerate(self.selected_units):
            if self.dragging and i == self.drag_unit_index:
                continue
                
            y_pos = 190 + i * 60
            button_rect = pygame.Rect(WIDTH - 280, y_pos, 250, 50)
            self.draw_unit_slot(screen, unit, y_pos, small_font)
        
        # 드래그 중인 유닛은 마우스 위치에 그리기
        if self.dragging and self.drag_unit_index is not None:
            mouse_pos = pygame.mouse.get_pos()
            self.draw_unit_slot(screen, self.selected_units[self.drag_unit_index], 
                              mouse_pos[1] - 25, small_font, is_dragging=True)

        # 시작 버튼
        pygame.draw.rect(screen, (0, 200, 0), self.start_button)
        start_text = self.font.render("Start Battle", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button.center)
        screen.blit(start_text, text_rect)

        # 판매 영역 표시 (드래그 중일 때만)
        if self.dragging:
            if self.sell_zone_active:
                pygame.draw.rect(screen, (255, 200, 200), self.sell_zone)  # 활성화된 판매 영역
            else:
                pygame.draw.rect(screen, (240, 240, 240), self.sell_zone)  # 기본 판매 영역
            sell_text = self.font.render("Drag here to sell", True, (100, 100, 100))
            text_rect = sell_text.get_rect(center=(self.sell_zone.centerx, self.sell_zone.centery))
            screen.blit(sell_text, text_rect)

    def draw_unit_slot(self, screen, unit, y_pos, small_font, is_dragging=False):
        # 유닛 슬롯 그리기 함수
        sell_price = int(unit["cost"] * 0.8)
        
        # 배경 rect와 위치 계산
        if is_dragging:
            # 드래그 중일 때는 마우스 위치를 기준으로 그리기
            x_pos = pygame.mouse.get_pos()[0] - 125  # 마우스 x 위치 중심으로
            button_rect = pygame.Rect(x_pos, y_pos, 250, 50)
        else:
            x_pos = WIDTH - 280
            button_rect = pygame.Rect(x_pos, y_pos, 250, 50)

        if is_dragging:
            pygame.draw.rect(screen, (230, 230, 250), button_rect)  # 드래그 중일 때 다른 색상
        else:
            pygame.draw.rect(screen, (200, 200, 200), button_rect)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
        
        # 텍스트 정보
        unit_name = self.font.render(f"- {unit['name']}", True, (0, 0, 0))
        unit_price = small_font.render(f"Sell: {sell_price}G", True, (100, 100, 100))
        unit_stats = small_font.render(f"HP: {unit['health']} | ATK: {unit['attack']}", 
                                     True, (50, 50, 50))
        
        screen.blit(unit_name, (x_pos, y_pos))
        screen.blit(unit_price, (x_pos, y_pos + 25))
        screen.blit(unit_stats, (x_pos + 100, y_pos + 25))

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
                self.drag_current_pos = event.pos
                # 판매 영역 활성화 상태 업데이트
                self.sell_zone_active = self.sell_zone.collidepoint(event.pos)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                if self.sell_zone_active:  # 판매 영역에서 드롭한 경우
                    sold_unit = self.selected_units[self.drag_unit_index]
                    sell_price = int(sold_unit["cost"] * 0.8)
                    self.gold += sell_price
                    self.selected_units.pop(self.drag_unit_index)
                    self.update_selected_unit_buttons()
                else:  # 다른 위치에서 드롭한 경우
                    drop_pos = event.pos
                    new_index = self.get_drop_index(drop_pos)
                    
                    if new_index is not None and new_index != self.drag_unit_index:
                        unit = self.selected_units.pop(self.drag_unit_index)
                        self.selected_units.insert(new_index, unit)
                        self.update_selected_unit_buttons()
                
                # 드래그 상태 초기화
                self.dragging = False
                self.drag_unit_index = None
                self.drag_start_pos = None
                self.drag_current_pos = None
                self.sell_zone_active = False

    def get_drop_index(self, pos):
        # 드롭 위치에 해당하는 인덱스 계산
        if len(self.selected_units) == 0:
            return None
            
        # 각 슬롯의 중심점과의 거리를 계산하여 가장 가까운 슬롯 찾기
        closest_index = 0
        min_distance = float('inf')
        
        for i in range(len(self.selected_units)):
            slot_x = WIDTH - 280 + 125  # 슬롯의 중심 x 좌표
            slot_y = 190 + i * 60 + 25  # 슬롯의 중심 y 좌표
            
            # 드롭 위치와 슬롯 중심점 사이의 거리 계산
            distance = math.sqrt((pos[0] - slot_x)**2 + (pos[1] - slot_y)**2)
            
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        # 최소 거리가 일정 범위 내에 있을 때만 인덱스 반환
        if min_distance < 100:  # 적절한 거리 임계값 설정
            return closest_index
            
        return None

