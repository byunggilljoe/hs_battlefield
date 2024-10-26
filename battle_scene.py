import pygame
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
from game_state import game_state

class BattleScene(Scene):
    def __init__(self):
        self.player_units, self.enemy_units = reset_game()
        self.game_state = game_state

    def update(self):
        if not self.game_state["game_over"]:
            if self.game_state["initial_adjustment"]:
                handle_initial_adjustment(self.player_units, self.enemy_units)
            elif self.game_state["waiting_for_fade"]:
                self.player_units, self.enemy_units = handle_fading(self.player_units, self.enemy_units)
            elif self.game_state["adjusting_positions"]:
                handle_position_adjustment(self.player_units, self.enemy_units)
            elif self.game_state["attacking_unit"] is None:
                select_units_for_attack(self.player_units, self.enemy_units)
            else:
                handle_attack(self.player_units, self.enemy_units)

            update_units(self.player_units, self.enemy_units)
        check_game_over(self.player_units, self.enemy_units)

    def draw(self, screen):
        screen.fill((255, 255, 255))  # Fill the screen with white

        # Draw non-attacking units first
        for unit in self.player_units + self.enemy_units:
            if not unit.dead and unit != self.game_state["attacking_unit"]:
                unit.draw(screen)

        # Draw attacking unit if exists
        if self.game_state["attacking_unit"] and not self.game_state["attacking_unit"].dead:
            self.game_state["attacking_unit"].draw(screen)

        # Draw all particles last (on top of everything)
        for unit in self.player_units + self.enemy_units:
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
            if not self.player_units:
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
        elif event.type == pygame.KEYDOWN and self.game_state["game_over"]:
            if event.key == pygame.K_SPACE:
                self.player_units, self.enemy_units = reset_game()
                self.game_state["game_over"] = False
