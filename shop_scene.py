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
from units.warlord import Warlord
from units.buffer import Buffer

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
            {"type": Bomber, "name": "Bomber", "cost": 300, "health": 20, "attack": 15},
            {"type": Buffer, "name": "Buffer", "cost": 350, "health": 45, "attack": 15}
        ]
        
        # 버튼 위치 설정 (가로로 배치)
        self.unit_buttons = []
        button_y = 150  # 모든 버튼의 y 위치
        total_width = len(self.available_units) * 100  # 간격 수정
        start_x = (WIDTH - total_width) / 2  # 첫 번째 버튼의 x 위
        
        for i, unit in enumerate(self.available_units):
            button_rect = pygame.Rect(start_x + i * 100, button_y, 50, 100)  # 50x100으로 수정
            self.unit_buttons.append({"rect": button_rect, "unit": unit})
            
        # 시작 버튼 위치 조정
        self.start_button = pygame.Rect(WIDTH/2 - 100, HEIGHT - 100, 200, 60)



        # 드래그 앤 드롭 관련 변수 수정
        self.dragging = False
        self.drag_unit_index = None
        self.drag_start_pos = None
        self.drag_current_pos = None
        self.dragging_shop_unit = None  # 상점에서 드래그 중인 유닛
        self.mouse_moved = False

        # 판매 영역을 상단으로 이동
        self.sell_zone = pygame.Rect(WIDTH/2 - 75, 50, 150, 80)
        self.sell_zone_active = False

        # 각 유닛 타입별 미리보기 인스턴스 생성
        self.preview_units = {
            "Tank": Tank(0, 0, 100, 10, BLUE, game_state, cost=300),
            "Healer": Healer(0, 0, 50, 15, BLUE, game_state, cost=250),
            "Phoenix": Phoenix(0, 0, 60, 20, BLUE, game_state, cost=400),
            "Venom": Venom(0, 0, 40, 25, BLUE, game_state, cost=350),
            "Bomber": Bomber(0, 0, 20, 15, BLUE, game_state, cost=300),
            "Buffer": Buffer(0, 0, 45, 15, BLUE, game_state, cost=350)
        }
        
        # 선택된 유닛들의 미리보기 인스턴스 생성
        self.selected_preview_units = []
        self.selected_unit_buttons = []
        if previous_units:
            self.selected_preview_units = previous_units
        self.update_selected_unit_buttons()


    def update(self):
        # 상점 유닛들의 파티클 업데이트
        for unit_data in self.preview_units.values():
            for particle in unit_data.particles[:]:
                particle.update()

        
        # 선택된 유닛들의 파티클 업데이트
        for preview_unit in self.selected_preview_units:
            for particle in preview_unit.particles[:]:
                particle.update()

    def update_selected_unit_buttons(self):
        # 선택된 유닛들의 버튼 위치 업데이트 (가로 중앙 정렬)
        self.selected_unit_buttons = []
        total_width = len(self.selected_preview_units) * 100  # 전체 너비 (유닛 간격 포함)
        start_x = (WIDTH - total_width) / 2  # 첫 번째 유닛의 x 좌표
        y_position = HEIGHT - 250  # 화면 중앙보다 약간 아래로 조정

        for i, unit in enumerate(self.selected_preview_units):
            button_rect = pygame.Rect(start_x + i * 100, y_position, 50, 100)
            self.selected_unit_buttons.append({"rect": button_rect, "unit": unit})

    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # 제목 그리기
        title = self.title_font.render("Shop", True, (0, 0, 0))
        screen.blit(title, (WIDTH/2 - title.get_rect().width/2, 10))
        
        # 골드 표시
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (50, 20))
        
        # 판매 영역 표시 (선택된 유닛 드래그 중일 때만)
        if self.dragging and self.drag_unit_index is not None:  # 수정된 조건
            if self.sell_zone_active:
                pygame.draw.rect(screen, (255, 200, 200), self.sell_zone)
            else:
                pygame.draw.rect(screen, (240, 240, 240), self.sell_zone)
            sell_text = self.font.render("Drag here to sell", True, (100, 100, 100))
            text_rect = sell_text.get_rect(center=self.sell_zone.center)
            screen.blit(sell_text, text_rect)

        # 상점 유닛 버튼 그리기
        shop_text = self.font.render("Available Units:", True, (0, 0, 0))
        screen.blit(shop_text, (50, 120))
        
        for button in self.unit_buttons:
            unit = button["unit"]
            rect = button["rect"]
            
            # 버튼 배경 (유닛에 가려질 것이므로 테두리만 표시)
            pygame.draw.rect(screen, (200, 200, 200), rect, 2)
            
            # 유닛 미리보기 그리기
            preview_unit = self.preview_units[unit['name']]
            preview_unit.x = rect.x
            preview_unit.y = rect.y
            preview_unit.draw(screen)
            
            # 가격 정보만 유닛 아래에 표시
            cost_text = self.font.render(f"{unit['cost']}G", True, (255, 215, 0))
            cost_rect = cost_text.get_rect(centerx=rect.centerx, top=rect.bottom + 5)
            screen.blit(cost_text, cost_rect)

        # 선택된 유닛 표시 텍스트 위 변경
        selected_text = self.font.render("Selected Units (drag to reorder):", True, (0, 0, 0))
        screen.blit(selected_text, (50, HEIGHT - 240))

        small_font = pygame.font.Font(None, 24)
        
        # 드래그 중이 아닌 유닛들 먼저 그리기
        for i, unit in enumerate(self.selected_preview_units):
            if self.dragging and i == self.drag_unit_index:
                continue
            self.draw_unit_slot(screen, unit, i, small_font)
        
        # 드래그 중인 유닛은 마우스 위치에 그리기
        if self.dragging and self.drag_unit_index is not None:
            self.draw_unit_slot(screen, self.selected_preview_units[self.drag_unit_index], 
                              self.drag_unit_index, small_font, is_dragging=True)

        # 시작 버튼
        pygame.draw.rect(screen, (0, 200, 0), self.start_button)
        start_text = self.font.render("Start Battle", True, (255, 255, 255))
        text_rect = start_text.get_rect(center=self.start_button.center)
        screen.blit(start_text, text_rect)

        # 각 유닛의 파티클 그리기
        for unit_data in self.preview_units.values():
            for particle in unit_data.particles:
                particle.draw(screen)

        # 드래그 중인 상점 유닛 그리기
        if self.dragging and self.dragging_shop_unit:
            mouse_pos = pygame.mouse.get_pos()
            preview_unit = self.preview_units[self.dragging_shop_unit["name"]]
            preview_unit.x = mouse_pos[0] - 25
            preview_unit.y = mouse_pos[1] - 50
            preview_unit.draw(screen)

    def draw_unit_slot(self, screen, unit, index, small_font, is_dragging=False):
        if is_dragging:
            mouse_pos = pygame.mouse.get_pos()
            x_pos = mouse_pos[0] - 25
            y_pos = mouse_pos[1] - 50
        else:
            total_width = len(self.selected_preview_units) * 100
            start_x = (WIDTH - total_width) / 2
            x_pos = start_x + index * 100
            y_pos = HEIGHT - 250

        button_rect = pygame.Rect(x_pos, y_pos, 50, 100)
        if is_dragging:
            pygame.draw.rect(screen, (230, 230, 250), button_rect)
            pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
        
        # 선택된 유닛의 실제 미리보기 그리기
        preview_unit = self.selected_preview_units[index]
        preview_unit.x = x_pos
        preview_unit.y = y_pos
        preview_unit.draw(screen)
        
        # 판매 가격 표시
        sell_price = int(unit.cost * 0.8)
        price_text = small_font.render(f"{sell_price}G", True, (255, 215, 0))
        price_rect = price_text.get_rect(centerx=button_rect.centerx, top=button_rect.bottom + 5)
        screen.blit(price_text, price_rect)

        # 더미 유닛은 반투명하게 표시
        if hasattr(unit, 'is_dummy'):
            s = pygame.Surface((50, 100))
            s.set_alpha(128)
            s.fill((200, 200, 200))
            screen.blit(s, (x_pos, y_pos))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 좌클릭
                # 선택된 유닛 드래그 체크
                for i, button in enumerate(self.selected_unit_buttons):
                    if button["rect"].collidepoint(event.pos):
                        self.dragging = True
                        self.drag_unit_index = i
                        self.drag_start_pos = event.pos
                        return
                
                # 상점 유닛 드래그 체크
                for button in self.unit_buttons:
                    if button["rect"].collidepoint(event.pos):
                        unit = button["unit"]
                        if self.gold >= unit["cost"] and len(self.selected_preview_units) < 7:
                            self.dragging = True
                            self.dragging_shop_unit = unit
                            self.drag_start_pos = event.pos
                            
                            # 임시 더미 유닛 추가
                            dummy_unit = unit["type"](0, PLAYER_Y, unit["health"], unit["attack"], (150, 150, 150), game_state)  # 회색으로 표시
                            dummy_unit.is_dummy = True  # 더미 유닛 표시를 위한 플래그
                            self.selected_preview_units.append(dummy_unit)
                            self.update_selected_unit_buttons()
                            return
                # 시작 버튼 클릭 처리
                if self.start_button.collidepoint(event.pos):
                    reset_game_state(game_state)
                    from battle_scene import BattleScene
                    # selected_preview_units를 직접 전달
                    self.scene_manager.set_scene(BattleScene(
                        self.scene_manager, 
                        self,
                        self.selected_preview_units
                    ))
                
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.drag_current_pos = event.pos
                # 판매 영역 활성화 상태 업데이트
                self.sell_zone_active = self.sell_zone.collidepoint(event.pos)
                
                # 드래그 중인 더미 유닛의 위치 업데이트
                if self.dragging_shop_unit:
                    # 더미 유닛 찾기
                    dummy_index = next((i for i, unit in enumerate(self.selected_preview_units) 
                                     if hasattr(unit, 'is_dummy')), None)
                    if dummy_index is not None:
                        # 현재 더미 유닛 제거
                        dummy_unit = self.selected_preview_units.pop(dummy_index)
                        
                        # 마우스 위치에 따른 새로운 위치 계산
                        mouse_x = event.pos[0]
                        total_width = len(self.selected_preview_units) * 100
                        start_x = (WIDTH - total_width) / 2
                        
                        target_index = 0
                        for i in range(len(self.selected_preview_units)):
                            slot_x = start_x + i * 100
                            if mouse_x > slot_x + 25:
                                target_index = i + 1
                        
                        # 더미 유닛을 새 위치에 삽입
                        self.selected_preview_units.insert(target_index, dummy_unit)
                        self.update_selected_unit_buttons()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                mouse_pos = event.pos
                selected_area_rect = pygame.Rect(0, HEIGHT - 300, WIDTH, 200)  # 선택된 유닛 영역

                # 더미 유닛 제거
                self.selected_preview_units = [unit for unit in self.selected_preview_units if not hasattr(unit, 'is_dummy')]

                if self.dragging_shop_unit:  # 상점 유닛을 드래그 중이었다면
                    if selected_area_rect.collidepoint(mouse_pos) and len(self.selected_preview_units) < 7:
                        # 구매 처리
                        unit = self.dragging_shop_unit
                        self.gold -= unit["cost"]
                        new_unit = unit["type"](0, PLAYER_Y, unit["health"], unit["attack"], BLUE, game_state)
                        
                        # 드롭 위치에 따라 삽입 위치 결정
                        mouse_x = mouse_pos[0]
                        total_width = len(self.selected_preview_units) * 100
                        start_x = (WIDTH - total_width) / 2
                        
                        target_index = 0
                        for i in range(len(self.selected_preview_units)):
                            slot_x = start_x + i * 100
                            if mouse_x > slot_x + 25:
                                target_index = i + 1
                        
                        self.selected_preview_units.insert(target_index, new_unit)
                        new_unit.on_spawn(new_unit, self.selected_preview_units, [])
                
                elif self.drag_unit_index is not None:  # 기존 유닛을 드래그 중이었다면
                    if self.sell_zone_active:
                        # 판매 처리
                        sold_unit = self.selected_preview_units[self.drag_unit_index]
                        sell_price = int(sold_unit.cost * 0.8)  # 80% 가격으로 판매
                        self.gold += sell_price
                        self.selected_preview_units.pop(self.drag_unit_index)
                    else:
                        # 유닛 순서 재정렬
                        mouse_x = mouse_pos[0]
                        total_width = len(self.selected_preview_units) * 100
                        start_x = (WIDTH - total_width) / 2
                        
                        # 드래그 중인 유닛을 임시로 제거
                        dragged_unit = self.selected_preview_units.pop(self.drag_unit_index)
                        
                        # 새로운 위치 계산
                        target_index = 0
                        for i in range(len(self.selected_preview_units)):
                            slot_x = start_x + i * 100
                            if mouse_x > slot_x + 25:
                                target_index = i + 1
                        
                        # 계산된 위치에 유닛 삽입
                        self.selected_preview_units.insert(target_index, dragged_unit)

                # 드래그 상태 초기화
                self.dragging = False
                self.drag_unit_index = None
                self.drag_start_pos = None
                self.drag_current_pos = None
                self.dragging_shop_unit = None
                self.sell_zone_active = False
                self.update_selected_unit_buttons()




