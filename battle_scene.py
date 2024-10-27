import pygame
import random
from constants import HEIGHT, RED, ENEMY_Y, PLAYER_Y
from scene import Scene
from game_logic import (
    reset_game,
    handle_initial_adjustment,
    handle_fading,
    handle_position_adjustment,
    select_units_for_attack,
    handle_attack,
    update_units,
    check_game_over
)

from units.tank import Tank
from units.healer import Healer
from units.phoenix import Phoenix
from units.venom import Venom
from units.bomber import Bomber
from units.splash import Splash
from game_state import reset_game_state
from game_state import game_state

class BattleScene(Scene):
    def __init__(self, scene_manager, previous_shop_scene, player_units):
        self.game_state = game_state
        self.scene_manager = scene_manager
        self.previous_shop_scene = previous_shop_scene
        self.game_state["player_units"] = player_units

        # 전투 시작 시 유닛 정보 저장
        self.initial_units = []
        for unit in self.game_state["player_units"]:
            unit_info = {
                "type": type(unit),
                "name": unit.name,
                "health": unit.health,
                "attack": unit.attack,
                "cost": next(u["cost"] for u in self.previous_shop_scene.available_units 
                           if u["name"] == unit.name)
            }
            self.initial_units.append(unit_info)
        
        self.initialize_enemy_units()
        
    def initialize_enemy_units(self):
        # 적 유닛 랜덤 생성 (4개)
        possible_units = [Tank] #[Bomber] #[Tank, Healer, Phoenix, Venom, Bomber, Splash]
        enemy_positions = [(700, ENEMY_Y), (600, ENEMY_Y), 
                         (500, ENEMY_Y), (400, ENEMY_Y)]
        
        for pos in enemy_positions:
            unit_class = random.choice(possible_units)
            unit = unit_class(
                x=pos[0],
                y=pos[1],
                health=random.randint(40, 100),
                attack=random.randint(10, 25),
                color=RED,
                game_state=self.game_state
            )
            self.game_state["enemy_units"].append(unit)
        
        # 유닛들의 위치 조정이 필요함을 표시
        # self.game_state["initial_adjustment"] = True

    def update(self):
        print("game_over:", self.game_state["game_over"],
         "initial_adjustment:", self.game_state["initial_adjustment"],
          "waiting_for_fade:", self.game_state["waiting_for_fade"],
           "adjusting_positions:", self.game_state["adjusting_positions"],
            "attacking_unit:", self.game_state["attacking_unit"])
            
        if not self.game_state["game_over"]:
            if self.game_state["initial_adjustment"]:
                handle_initial_adjustment(self.game_state["player_units"], self.game_state["enemy_units"])
            elif self.game_state["waiting_for_fade"]:
                handle_fading(self.game_state["player_units"], self.game_state["enemy_units"])
            elif self.game_state["adjusting_positions"]:
                handle_position_adjustment(self.game_state["player_units"], self.game_state["enemy_units"])
            elif self.game_state["attacking_unit"] is None:
                select_units_for_attack(self.game_state["player_units"], self.game_state["enemy_units"])
            else:
                handle_attack(self.game_state["player_units"], self.game_state["enemy_units"])

            update_units(self.game_state["player_units"], self.game_state["enemy_units"])
        check_game_over(self.game_state["player_units"], self.game_state["enemy_units"])

    def draw(self, screen):
        screen.fill((255, 255, 255))  # Fill the screen with white

        # Draw non-attacking units first
        for unit in self.game_state["player_units"] + self.game_state["enemy_units"]:
            if not unit.dead and unit != self.game_state["attacking_unit"]:
                unit.draw(screen)

        # Draw attacking unit if exists
        if self.game_state["attacking_unit"] and not self.game_state["attacking_unit"].dead:
            self.game_state["attacking_unit"].draw(screen)

        # Draw all particles last (on top of everything)
        for unit in self.game_state["player_units"] + self.game_state["enemy_units"]:
            for particle in unit.particles:
                particle.update()
                particle.draw(screen)
        
        if self.game_state["attacking_unit"]:
            for particle in self.game_state["attacking_unit"].particles:
                particle.update()
                particle.draw(screen)

        # Display game over message
        if self.game_state["game_over"]:
            font = pygame.font.Font(None, 74)
            if not self.game_state["player_units"] and not self.game_state["enemy_units"]:
                text = font.render("Draw!", True, (128, 128, 128))  # 회색으로 무승부 표시
            elif not self.game_state["player_units"]:
                text = font.render("Enemy Win!", True, (255, 0, 0))
            else:
                text = font.render("Player Win!", True, (0, 0, 255))
            text_rect = text.get_rect(center=(800/2, 600/2))
            screen.blit(text, text_rect)

            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press SPACE to restart", True, (0, 0, 0))
            restart_rect = restart_text.get_rect(center=(800/2, 600/2 + 50))
            screen.blit(restart_text, restart_rect)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.game_state["game_over"]:
                from shop_scene import ShopScene
                print("---initial_units:", self.initial_units)
                # 저장해둔 초기 유닛 정보를 사용
                shop_scene = ShopScene(
                    self.scene_manager,
                    previous_units=self.initial_units,
                    previous_gold=self.previous_shop_scene.gold
                )
                self.scene_manager.set_scene(shop_scene)
