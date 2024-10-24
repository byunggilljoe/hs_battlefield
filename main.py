import pygame
from scene_manager import SceneManager
from menu_scene import MenuScene

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    scene_manager = SceneManager()
    menu_scene = MenuScene(scene_manager)
    scene_manager.set_scene(menu_scene)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            scene_manager.handle_event(event)

        scene_manager.update()
        scene_manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
