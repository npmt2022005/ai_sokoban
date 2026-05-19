import pygame
from constants import *

# Kích thước mỗi ô vuông (pixel)
TILE_SIZE = 64

class Renderer:
    def __init__(self, width, height):
        pygame.init()
        self.screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE))
        pygame.display.set_caption("Sokoban AI Project")
        
        # Tải hình ảnh
        self.images = {
            WALL: pygame.image.load('frontend/assets/wall.png'),
            BOX: pygame.image.load('frontend/assets/box.png'),
            TARGET: pygame.image.load('frontend/assets/target.png'),
            PLAYER: pygame.image.load('frontend/assets/player.png'),
            SPACE: pygame.image.load('frontend/assets/space.png')
        }

    def draw(self, game_state):
        """
        game_state là đối tượng SokobanGame từ Backend của bạn
        """
        self.screen.fill((0, 0, 0)) # Xóa màn hình bằng màu đen
        
        data = game_state.get_display_data();
        # Duyệt qua toàn bộ bản đồ để vẽ
        for r in range(data["height"]):
            for c in range(data["width"]):
                pos = (r, c)
                # Vẽ sàn trống 
                self.screen.blit(self.images[SPACE], (c * TILE_SIZE, r * TILE_SIZE))
                
                # Vẽ các vật thể tĩnh và động chồng lên
                if pos in data["walls"]:
                    self.screen.blit(self.images[WALL], (c * TILE_SIZE, r * TILE_SIZE))
                if pos in data["targets"]:
                    self.screen.blit(self.images[TARGET], (c * TILE_SIZE, r * TILE_SIZE))
                if pos in data["boxes"]:
                    self.screen.blit(self.images[BOX], (c * TILE_SIZE, r * TILE_SIZE))
                if pos == data["player"]:
                    self.screen.blit(self.images[PLAYER], (c * TILE_SIZE, r * TILE_SIZE))
        
        pygame.display.flip() # Cập nhật màn hình