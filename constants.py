import pygame

# 화면 설정
WIDTH = 800
HEIGHT = 600

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 초기화
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Turn-Based Battle Game")

PLAYER_Y = HEIGHT // 2 + 50
ENEMY_Y = HEIGHT // 2 - 150