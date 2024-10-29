from unit import Unit
import pygame

class Tank(Unit):
    def __init__(self, x, y, health, attack, color, game_state, cost=300):
        super().__init__(x, y, health, attack, color, game_state, cost)
        self.name = "Tank"
        self.taunt = True

