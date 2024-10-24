import pygame
from constants import screen, WIDTH, HEIGHT, WHITE, BLACK, RED, BLUE
from game_state import game_state, reset_game_state
from game_logic import (
    reset_game, handle_initial_adjustment, handle_fading,
    handle_position_adjustment, select_units_for_attack,
    handle_attack, update_units, check_game_over
)

def main():
    print("Game state:", game_state)
    player_units, enemy_units = reset_game()
    reset_game_state()

    # 디버그: 유닛 생성 확인

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and game_state["game_over"]:
                if event.key == pygame.K_SPACE:
                    player_units, enemy_units = reset_game()
                    reset_game_state()
        #print(game_state["attacking_unit"], game_state["target_unit"])
        print("game_over:", game_state["game_over"], "waiting_for_fade:", game_state["waiting_for_fade"],\
             "adjusting_positions:", game_state["adjusting_positions"], "initial_adjustment:", game_state["initial_adjustment"],\
                "attacking_unit:", game_state["attacking_unit"], "target_unit:", game_state["target_unit"])

    
        if not game_state["game_over"]:
            if game_state["initial_adjustment"]:
                handle_initial_adjustment(player_units, enemy_units)
            elif game_state["waiting_for_fade"]:
                player_units, enemy_units = handle_fading(player_units, enemy_units)
            elif game_state["adjusting_positions"]:
                handle_position_adjustment(player_units, enemy_units)
            elif game_state["attacking_unit"] is None:
                select_units_for_attack(player_units, enemy_units)
            else:
                print("handle attack!")
                handle_attack(player_units, enemy_units)


            update_units(player_units, enemy_units)

        check_game_over(player_units, enemy_units)

        screen.fill(WHITE)

        # 공격 중이 아닌 유닛들을 먼저 그립니다
        for unit in player_units + enemy_units:
            if not unit.dead and unit != game_state["attacking_unit"]:
                unit.draw(screen)

        # 공격 중인 유닛을 마지막에 그립니다
        if game_state["attacking_unit"] and not game_state["attacking_unit"].dead:
            game_state["attacking_unit"].draw(screen)

        if game_state["game_over"]:
            font = pygame.font.Font(None, 74)
            if not player_units:
                text = font.render("Enemy Win!", True, RED)
            else:
                text = font.render("Player Win!", True, BLUE)
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            screen.blit(text, text_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press SPACE to restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
