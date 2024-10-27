 


def reset_game_state(game_state = None):
    if game_state is None:
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
    else:
        game_state["game_over"] = False
        game_state["waiting_for_fade"] = False
        game_state["adjusting_positions"] = False
        game_state["all_units_adjusted"] = False
        game_state["initial_adjustment"] = True
        game_state["turn"] = 0
        game_state["current_team"] = "player"
        game_state["player_attack_index"] = 0
        game_state["enemy_attack_index"] = 0
        game_state["attacking_unit"] = None
        game_state["target_unit"] = None
        game_state["player_units"] = []
        game_state["enemy_units"] = []
        return game_state

# Usage
game_state = reset_game_state()
