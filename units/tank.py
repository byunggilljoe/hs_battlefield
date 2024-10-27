from unit import Unit
import pygame

class Tank(Unit):
    def __init__(self, x, y, health, attack, color, game_state):
        super().__init__(x, y, health, attack, color, game_state)
        self.name = "Tank"
        self.taunt = True

