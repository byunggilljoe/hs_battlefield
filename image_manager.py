import pygame

class ImageManager:
    _instance = None
    _images = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ImageManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load_image(cls, image_path):
        # 이미 로드된 이미지가 있다면 그것을 반환
        if image_path in cls._images:
            return cls._images[image_path]

        try:
            # 이미지 로드
            original_image = pygame.image.load(image_path).convert_alpha()
            
            # 세로를 100픽셀로 맞추고 비율 유지
            original_height = original_image.get_height()
            original_width = original_image.get_width()
            
            # 세로 기준으로 스케일 계산
            scale_ratio = 100 / original_height
            new_width = int(original_width * scale_ratio)
            
            # 이미지 크기 조정
            scaled_image = pygame.transform.scale(original_image, (new_width, 100))
            
            # 가로가 50픽셀보다 크면 중앙 부분만 잘라내기
            if new_width > 50:
                crop_x = (new_width - 50) // 2
                final_image = scaled_image.subsurface((crop_x, 0, 50, 100))
            else:
                final_image = scaled_image

            # 캐시에 저장
            cls._images[image_path] = final_image
            return final_image
            
        except (pygame.error, FileNotFoundError):
            print(f"Could not load image: {image_path}")
            return None

    @classmethod
    def get_image(cls, image_path):
        return cls._images.get(image_path)

    @classmethod
    def clear(cls):
        cls._images.clear() 