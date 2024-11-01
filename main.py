import pygame
from scene_manager import SceneManager
from menu_scene import MenuScene
from image_manager import ImageManager
def initialize_game():
    # 게임에서 사용할 모든 이미지 미리 로드
    ImageManager.load_image("images/units/splash.png")
    ImageManager.load_image("images/units/venom.png")
    ImageManager.load_image("images/units/warlord.png")
    ImageManager.load_image("images/units/barracks.png")
    ImageManager.load_image("images/units/bomber.png")
    ImageManager.load_image("images/units/tank.png")

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
