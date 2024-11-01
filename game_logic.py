import math
import random
from constants import WIDTH, HEIGHT, BLUE, RED, PLAYER_Y, ENEMY_Y
from unit import Unit
from units.venom import Venom
from units.splash import Splash
from units.healer import Healer
from units.phoenix import Phoenix
from units.bomber import Bomber  # 파일 상단에 추가
from units.tank import Tank  # 파일 상단에 추가
from units.barracks import Barracks  # 상단에 추가
from game_state import game_state

def reset_game():

    game_state["player_units"] = [
        Healer(0, PLAYER_Y, random.randint(10, 50), random.randint(10, 20), BLUE, game_state),
        Tank(0, PLAYER_Y, random.randint(80, 120), random.randint(8, 15), BLUE, game_state),  # 체력이 높고 공격력이 낮은 Tank 추가
        Phoenix(0, PLAYER_Y, random.randint(25, 50), random.randint(15, 25), BLUE, game_state)
    ]
    game_state["enemy_units"] = [
        Splash(0, ENEMY_Y, random.randint(50, 100), random.randint(10, 10), RED, game_state) 
        for _ in range(4)
    ] + [Barracks(0, ENEMY_Y, random.randint(70, 100), random.randint(8, 15), RED, game_state)]
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
    player_adjusted = adjust_unit_positions(player_units, PLAYER_Y)
    enemy_adjusted = adjust_unit_positions(enemy_units, ENEMY_Y)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    if game_state["all_units_adjusted"]:
        game_state["initial_adjustment"] = False
        game_state["adjusting_positions"] = False
    # print("---handle_initial_adjustment:", player_adjusted, enemy_adjusted, game_state["all_units_adjusted"], game_state["initial_adjustment"], game_state["adjusting_positions"])

def handle_fading(player_units, enemy_units):
    fading_units = [unit for unit in player_units + enemy_units if unit.is_fading()]
    if not fading_units:
        game_state["waiting_for_fade"] = False
        game_state["adjusting_positions"] = True
        player_units, enemy_units = remove_dead_units(player_units, enemy_units)
    return player_units, enemy_units

def handle_position_adjustment(player_units, enemy_units):
    player_adjusted = adjust_unit_positions(player_units, PLAYER_Y)
    enemy_adjusted = adjust_unit_positions(enemy_units, ENEMY_Y)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    # print("---handle_position_adjustment:", player_adjusted, enemy_adjusted)
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
            
            # 도발 상태인 유닛이 있는지 확인
            taunting_units = [unit for unit in alive_target_units if hasattr(unit, 'taunt') and unit.taunt]
            
            # 도발 상태인 유닛이 있으면 그 중에서 선택, 없으면 일반적인 랜덤 선택
            if taunting_units:
                target_unit = random.choice(taunting_units)
            else:
                target_unit = random.choice(alive_target_units)
            
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
    
    if attacking_unit and target_unit:
        attack_status = handle_unit_combat(attacking_unit, target_unit, player_units, enemy_units)
        
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
        alive_player_units = [unit for unit in player_units if not unit.dead]
        alive_enemy_units = [unit for unit in enemy_units if not unit.dead]
        
        if not alive_player_units and not alive_enemy_units:
            game_state["game_over"] = True
            print("무승부!")
        elif not alive_player_units:
            game_state["game_over"] = True
            print("적팀 승리!")
        elif not alive_enemy_units:
            game_state["game_over"] = True
            print("플레이어팀 승리!")

def handle_unit_combat(attacking_unit, target_unit, player_units, enemy_units):
    move_status = attacking_unit.move_to_target()
    
    if move_status == "attack":
        # 모든 유닛에게 attack 이벤트를 broadcast
        for unit in player_units + enemy_units:
            unit.on_attack(attacking_unit, target_unit, player_units, enemy_units)
            
        attacking_unit.apply_damage(target_unit)
        target_unit.apply_damage(attacking_unit)
        attacking_unit.returning = True
        
        # Calculate collision direction and create particles
        collision_direction = math.atan2(
            target_unit.y - attacking_unit.original_y, 
            target_unit.x - attacking_unit.original_x
        )
        attacking_unit.create_collision_particles(
            collision_direction + random.uniform(-0.25, 0.25)
        )
        target_unit.create_collision_particles(
            collision_direction + math.pi + random.uniform(-0.25, 0.25)
        )
        
    elif move_status == "returned":
        handle_death(player_units + enemy_units)
        return "completed"
    
    return "in_progress"

def handle_death(units):
    for unit in units:
        if unit.health <= 0 and not unit.ready_to_fade:
            unit.prepare_to_fade()
            # 모든 유닛에게 death 이벤트를 broadcast
            for observer_unit in game_state["player_units"] + game_state["enemy_units"]:
                observer_unit.on_death(unit, game_state["player_units"], game_state["enemy_units"])
        if unit.should_create_particles:
            unit.create_particles()
            unit.should_create_particles = False
