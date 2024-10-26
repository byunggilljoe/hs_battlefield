 


def reset_game_state():
    return {
        "game_over": False,
        "waiting_for_fade": False,
        "adjusting_positions": False,
        "all_units_adjusted": False,
        "initial_adjustment": True,
        "turn": 0,
        "current_team": "player",  # "player" 또는 "enemy"
        "player_attack_index": 0,
        "enemy_attack_index": 0,
        "attacking_unit": None,
        "target_unit": None,
        "player_units": [],
        "enemy_units": [],
    }

# Usage
game_state = reset_game_state()
