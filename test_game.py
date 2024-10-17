import pygame
import random
import math

# 초기화
pygame.init()

# 화면 설정
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Particle 클래스 추가
class Particle:
    def __init__(self, x, y, color, direction, speed_multiplier=1):
        self.x = x
        self.y = y
        self.color = color if len(color) == 4 else color + (255,)  # RGB를 RGBA로 변환
        self.radius = random.uniform(1, 3)
        self.speed = random.uniform(1, 3)*speed_multiplier
        self.angle = direction
        self.lifetime = random.randint(20, 40)
        self.alpha = 255  # 알파 값을 별도로 관리

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1
        self.radius = max(0, self.radius - 0.05)
        self.alpha = max(0, self.alpha - 5)  # 알파 값 감소

    def draw(self, screen):
        if self.alpha > 0:
            color_with_alpha = self.color[:3] + (self.alpha,)
            particle_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha, (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surface, (int(self.x - self.radius), int(self.y - self.radius)))

# 말(Unit) 클래스 정의
class Unit:
    def __init__(self, x, y, health, attack, color):
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.health = health
        self.attack = attack
        self.color = color
        self.moving = False
        self.returning = False
        self.target_unit = None
        self.health_animation = 0
        self.health_animation_time = 0
        self.alpha = 255
        self.fading = False
        self.dead = False
        self.attack_animation = 0
        self.attack_direction = 1
        self.particles = []
        self.should_create_particles = False  # 새로운 플래그 추가
        self.start_attack_x = None
        self.start_attack_y = None

        self.current_speed = 0.5  # 초기 속도
        self.acceleration = 0.3  # 가속도

    def draw(self):
        s = pygame.Surface((50, 100), pygame.SRCALPHA)
        s.fill((self.color[0], self.color[1], self.color[2], self.alpha))
        screen.blit(s, (self.x, self.y))

        font = pygame.font.Font(None, 24)
        
        # 체력 텍스트 (오른쪽 아래)
        health_size = 24 + self.health_animation
        health_font = pygame.font.Font(None, int(health_size))
        health_text = health_font.render(str(self.health), True, (0, 0, 0))
        health_text.set_alpha(self.alpha)
        health_rect = health_text.get_rect()
        health_rect.bottomright = (self.x + 50, self.y + 100)
        screen.blit(health_text, health_rect)

        # 공격력 텍스트 (왼쪽 아래)
        attack_text = font.render(str(self.attack), True, (255, 255, 255))
        attack_text.set_alpha(self.alpha)
        attack_rect = attack_text.get_rect()
        attack_rect.bottomleft = (self.x, self.y + 100)
        screen.blit(attack_text, attack_rect)

        # 체력 애니메이션 업데이트
        if self.health_animation > 0:
            self.health_animation_time += 1
            if self.health_animation_time > 10:
                self.health_animation = max(0, self.health_animation - 1)
                self.health_animation_time = 0

        # 페이딩 효과
        if self.fading:
            self.alpha = max(0, self.alpha - 5)
            if self.alpha == 0:
                self.dead = True

        # 파티클 리기
        for particle in self.particles:
            particle.draw(screen)

    def update_health(self, new_health):
        self.health = new_health
        self.health_animation = 10
        self.health_animation_time = 0
        if self.health <= 0:
            self.health = 0
            self.dead = True
            self.should_create_particles = True  # 파티클 생성 플래그 설정

    def move_to_target(self):
        if not self.moving:
            return "idle"

        if self.target_unit:
            if self.start_attack_x is None:
                self.start_attack_x = self.x
                self.start_attack_y = self.y

            target_x = self.target_unit.x if not self.returning else self.original_x
            target_y = self.target_unit.y if not self.returning else self.original_y

            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 5:
                # 속도 증가
                self.current_speed = min(self.current_speed + self.acceleration, 8)  # 최대 속도 제한
                
                self.x += self.current_speed * dx / distance
                self.y += self.current_speed * dy / distance
            else:
                self.x = target_x
                self.y = target_y
                if not self.returning:
                    return "attack"
                else:
                    self.moving = False
                    self.target_unit = None
                    self.returning = False
                    self.current_speed = 0.5  # 속도 초기화
                    if self.should_create_particles:  # 파티클 생성 조건 확인
                        self.create_particles()
                        self.should_create_particles = False
                    return "returned"
        else:
            self.moving = False
            self.current_speed = 0.5  # 속도 초기화
        return "moving"

    def is_fading(self):
        return self.fading and self.alpha > 0

    def create_particles(self):
        for _ in range(30):
            particle_x = self.x + 25 + random.uniform(-10, 10)
            particle_y = self.y + 50 + random.uniform(-10, 10)
            self.particles.append(Particle(particle_x, particle_y, self.color, random.uniform(0, 2*math.pi)))

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def create_collision_particles(self, direction):
        dust_color = (139, 69, 19)  # 갈색 (먼지 색상)
        for _ in range(20):
            particle_x = self.x + 25 + random.uniform(-10, 10)
            particle_y = self.y + 50 + random.uniform(-10, 10)
            self.particles.append(Particle(particle_x, particle_y, dust_color, direction, speed_multiplier=2))

    def reset_attack_start_position(self):
        self.start_attack_x = None
        self.start_attack_y = None

# 게임 상태 변수
game_state = {
    "game_over": False,
    "waiting_for_fade": False,
    "adjusting_positions": True,
    "all_units_adjusted": False,
    "initial_adjustment": True,
    "turn": 0,
    "player_attack_index": 0,
    "enemy_attack_index": 0,
    "attacking_unit": None,
    "target_unit": None,
    "attack_animation_frames": 0
}

def reset_game():
    global player_units, enemy_units
    player_units = [Unit(0, HEIGHT // 2 - 150, random.randint(50, 100), random.randint(10, 20), BLUE) for _ in range(4)]
    enemy_units = [Unit(0, HEIGHT // 2 + 50, random.randint(50, 100), random.randint(10, 20), RED) for _ in range(4)]
    
    for key in game_state:
        if key == "adjusting_positions" or key == "initial_adjustment":
            game_state[key] = True
        else:
            game_state[key] = False
    game_state["turn"] = 0
    game_state["player_attack_index"] = 0
    game_state["enemy_attack_index"] = 0

def adjust_unit_positions(units, y):
    alive_units = [unit for unit in units if not unit.dead]
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

def remove_dead_units():
    global player_units, enemy_units
    player_units = [unit for unit in player_units if not unit.dead]
    enemy_units = [unit for unit in enemy_units if not unit.dead]

def handle_initial_adjustment():
    player_adjusted = adjust_unit_positions(player_units, HEIGHT // 2 - 150)
    enemy_adjusted = adjust_unit_positions(enemy_units, HEIGHT // 2 + 50)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    
    if game_state["all_units_adjusted"]:
        game_state["initial_adjustment"] = False
        game_state["adjusting_positions"] = False

def handle_fading():
    fading_units = [unit for unit in player_units + enemy_units if unit.is_fading()]
    if not fading_units:
        game_state["waiting_for_fade"] = False
        game_state["adjusting_positions"] = True
        remove_dead_units()

def handle_position_adjustment():
    player_adjusted = adjust_unit_positions(player_units, HEIGHT // 2 - 150)
    enemy_adjusted = adjust_unit_positions(enemy_units, HEIGHT // 2 + 50)
    game_state["all_units_adjusted"] = player_adjusted and enemy_adjusted
    
    if game_state["all_units_adjusted"]:
        game_state["adjusting_positions"] = False
        game_state["turn"] += 1

def select_units_for_attack():
    global player_units, enemy_units

    if player_units and enemy_units:
        if game_state["turn"] % 2 == 0:  # 플레이어 턴
            while True:
                if game_state["player_attack_index"] >= len(player_units):
                    game_state["player_attack_index"] = 0  # 모든 유닛이 공격했으면 다시 처음부터

                attacking_unit = player_units[game_state["player_attack_index"]]
                game_state["player_attack_index"] += 1

                if not attacking_unit.dead:
                    break

            # 적 유닛 중 살아있는 가장 왼쪽 유닛 선택
            target_unit = next((unit for unit in enemy_units if not unit.dead), None)
        else:  # 적 턴
            while True:
                if game_state["enemy_attack_index"] >= len(enemy_units):
                    game_state["enemy_attack_index"] = 0  # 모든 유닛이 공격했으면 다시 처음부터

                attacking_unit = enemy_units[game_state["enemy_attack_index"]]
                game_state["enemy_attack_index"] += 1

                if not attacking_unit.dead:
                    break

            # 플레이어 유닛 중 살아있는 가장 왼쪽 유닛 선택
            target_unit = next((unit for unit in player_units if not unit.dead), None)

        if attacking_unit and target_unit:
            attacking_unit.moving = True
            attacking_unit.target_unit = target_unit
            game_state["attacking_unit"] = attacking_unit
            game_state["target_unit"] = target_unit
        else:
            game_state["game_over"] = True
    else:
        game_state["game_over"] = True

def handle_attack():
    attacking_unit = game_state["attacking_unit"]
    target_unit = game_state["target_unit"]
    
    if attacking_unit and target_unit:
        move_status = attacking_unit.move_to_target()
        if move_status == "attack":
            game_state["attack_animation_frames"] = 10
            
            # 공격 시작 위치에서 타겟까지의 방향 계산
            if attacking_unit.start_attack_x is not None:
                attack_direction = math.atan2(
                    target_unit.y - attacking_unit.start_attack_y,
                    target_unit.x - attacking_unit.start_attack_x
                )
            else:
                attack_direction = 0  # 기본값 설정

            attacking_unit.attack_direction = -1 if attacking_unit in player_units else 1
            
            # 충돌 파티클 생성 (공격 방향으로)
            attacking_unit.create_collision_particles(attack_direction)
            target_unit.create_collision_particles(attack_direction)  # 반대 방향
            
            new_target_health = max(0, target_unit.health - attacking_unit.attack)
            new_attacker_health = max(0, attacking_unit.health - target_unit.attack)
            
            target_unit.update_health(new_target_health)
            attacking_unit.update_health(new_attacker_health)
            
            attacking_unit.returning = True

            if target_unit.dead:
                target_unit.should_create_particles = True
            if attacking_unit.dead:
                attacking_unit.should_create_particles = True

            attacking_unit.reset_attack_start_position()
            # game_state["attacking_unit"] = None
            # game_state["target_unit"] = None
        elif move_status == "returned":
            if attacking_unit.dead:
                attacking_unit.fading = True
                if attacking_unit.should_create_particles:
                    attacking_unit.create_particles()
                    attacking_unit.should_create_particles = False
            if target_unit.dead:
                target_unit.fading = True
                if target_unit.should_create_particles:
                    target_unit.create_particles()
                    target_unit.should_create_particles = False
            game_state["waiting_for_fade"] = True
            attacking_unit.reset_attack_start_position()
            game_state["attacking_unit"] = None
            game_state["target_unit"] = None
    else:
        game_state["attacking_unit"] = None
        game_state["target_unit"] = None

def update_units():
    for unit in player_units + enemy_units:
        if unit.is_fading():
            unit.draw()
        unit.update_particles()

def check_game_over():
    if not game_state["game_over"]:
        if not player_units or not enemy_units:
            game_state["game_over"] = True
            if not player_units:
                print("적팀 승리!")
            else:
                print("플레이어팀 승리!")

# 게임 초기화
reset_game()

# 게임 루프
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_state["game_over"]:
            if event.key == pygame.K_SPACE:
                reset_game()

    if not game_state["game_over"]:
        if game_state["initial_adjustment"]:
            handle_initial_adjustment()
        elif game_state["waiting_for_fade"]:
            handle_fading()
        elif game_state["adjusting_positions"]:
            handle_position_adjustment()
        elif game_state["attacking_unit"] is None:
            select_units_for_attack()
        else:
            handle_attack()

        if game_state["attack_animation_frames"] > 0:
            game_state["attack_animation_frames"] -= 1

        update_units()

    check_game_over()

    # 화면 그리기
    screen.fill(WHITE)

    # 공격 중이 아닌 유닛들 먼저 그리기
    for unit in player_units + enemy_units:
        if unit != game_state["attacking_unit"]:
            unit.draw()

    # 공격 중인 유닛을 마지막에 그리기
    if game_state["attacking_unit"]:
        game_state["attacking_unit"].draw()

    # 게임 오버 메시지 표시
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
