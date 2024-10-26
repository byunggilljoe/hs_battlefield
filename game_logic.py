import math
import random
from constants import WIDTH, HEIGHT, BLUE, RED
from unit import Unit
from units.venom import Venom
from units.splash import Splash
from units.healer import Healer
from units.phoenix import Phoenix
from units.bomber import Bomber  # 파일 상단에 추가
from game_state import game_state

def reset_game():
    game_state["player_units"] = [
        Bomber(0, HEIGHT // 2 - 150, random.randint(5, 10), random.randint(15, 20), BLUE, game_state),  # Bomber 추가,
        Healer(0, HEIGHT // 2 - 150, random.randint(10, 50), random.randint(10, 20), BLUE, game_state),
        Phoenix(0, HEIGHT // 2 - 150, random.randint(25, 50), random.randint(15, 25), BLUE, game_state),

    ]
    game_state["enemy_units"] = [
        Splash(0, HEIGHT // 2 + 50, random.randint(50, 100), random.randint(10, 20), RED, game_state) 
        for _ in range(4)
    ]
    # print(f"Reset game - Player units: {len(game_state)}, Enemy units: {len(game_state['enemy_units'])}")  # 디버그 출력 추가

def adjust_unit_positions(units, y):
    alive_units = [unit for unit in units ] # if not unit.dead
    if not alive_units:
        return True

    unit_width = 50
    total_width = len(alive_units) * unit_width + (len(alive_units) - 1) * 50
    start_x = (WIDTH - total_width) / 2

    all_adjusted = True
    for i, unit in enumerate(alive_units):
        target_x = start_x + i * (unit_width + 50)
        unit.original_x = target_x
        unit.x += (target_x - unit.x) * 0.2
        if abs(unit.x - target_x) > 0.5:
            all_adjusted = False
        unit.y = y

    return all_adjusted

def remove_dead_units(player_units, enemy_units):
    return [unit for unit in player_units if not unit.dead], [unit for unit in enemy_units if not unit.dead]

def handle_initial_adjustment(player_units, enemy_units):
    player_adjusted = adjust_unit_positions(player_units, HEIGHT // 2 - 150)
    enemy_adjusted = adjust_unit_positions(enemy_units, HEIGHT // 2 + 50)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    
    if game_state["all_units_adjusted"]:
        game_state["initial_adjustment"] = False
        game_state["adjusting_positions"] = False

def handle_fading(player_units, enemy_units):
    fading_units = [unit for unit in player_units + enemy_units if unit.is_fading()]
    if not fading_units:
        game_state["waiting_for_fade"] = False
        game_state["adjusting_positions"] = True
        player_units, enemy_units = remove_dead_units(player_units, enemy_units)
    return player_units, enemy_units

def handle_position_adjustment(player_units, enemy_units):
    player_adjusted = adjust_unit_positions(player_units, HEIGHT // 2 - 150)
    enemy_adjusted = adjust_unit_positions(enemy_units, HEIGHT // 2 + 50)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    
    if game_state["all_units_adjusted"]:
        game_state["adjusting_positions"] = False
        game_state["turn"] += 1

def select_units_for_attack(player_units, enemy_units):
    if player_units and enemy_units:
        if game_state["current_team"] == "player":
            attacking_units = player_units
            target_units = enemy_units
            attack_index = "player_attack_index"
        else:
            attacking_units = enemy_units
            target_units = player_units
            attack_index = "enemy_attack_index"
        
        # 살아있는 유닛만 선택
        alive_attacking_units = [unit for unit in attacking_units if not unit.dead]
        alive_target_units = [unit for unit in target_units if not unit.dead]
        
        if alive_attacking_units and alive_target_units:
            # 현재 인덱스의 유닛이 죽었다면, 다음 살아있는 유닛을 찾음
            while game_state[attack_index] < len(attacking_units) and attacking_units[game_state[attack_index]].dead:
                game_state[attack_index] += 1
            
            # 모든 유닛을 확인했다면 인덱스를 초기화
            if game_state[attack_index] >= len(attacking_units):
                game_state[attack_index] = 0
            
            # 공격 유닛 선택
            attacking_unit = alive_attacking_units[game_state[attack_index] % len(alive_attacking_units)]
            target_unit = random.choice(alive_target_units)  # 랜덤으로 타겟 유닛 선택
            
            attacking_unit.moving = True
            attacking_unit.target_unit = target_unit
            game_state["attacking_unit"] = attacking_unit
            game_state["target_unit"] = target_unit
            
            # 다음 공격을 위해 인덱스 증가
            game_state[attack_index] += 1
            
            # 다음 턴을 위해 팀 전환
            game_state["current_team"] = "enemy" if game_state["current_team"] == "player" else "player"
        else:
            game_state["game_over"] = True
    else:
        game_state["game_over"] = True

def handle_attack(player_units, enemy_units):
    attacking_unit = game_state["attacking_unit"]
    target_unit = game_state["target_unit"]

    attack_status = attacking_unit.handle_combat(target_unit, player_units, enemy_units)
    
    if attack_status == "completed":
        game_state["waiting_for_fade"] = True
        game_state["attacking_unit"] = None
        game_state["target_unit"] = None


def update_units(player_units, enemy_units):
    for unit in player_units + enemy_units:
        unit.update()  # 유닛의 상태 업데이트 (페이딩 포함)
        unit.update_particles()
    
    # 완전히 사라진 유닛 제거
    player_units[:] = [unit for unit in player_units if not unit.is_completely_faded()]
    enemy_units[:] = [unit for unit in enemy_units if not unit.is_completely_faded()]
    
def check_game_over(player_units, enemy_units):
    if not game_state["game_over"]:
        if not player_units or not enemy_units:
            game_state["game_over"] = True
            if not player_units:
                print("적팀 승리!")
            else:
                print("플레이어팀 승리!")
