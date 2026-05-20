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

    def update_screen_size(self, width, height):
        """Cập nhật lại kích thước cửa sổ phù hợp với kích thước của Map mới"""
        self.screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE))

    def draw_map_selection_menu(self, maps, selected_index):
        """Vẽ giao diện Menu chọn Map"""
        self.screen.fill((30, 30, 30)) # Màu nền xám tối cho menu
        
        # Khởi tạo font chữ hệ thống
        font = pygame.font.SysFont('Arial', 32)
        title_font = pygame.font.SysFont('Arial', 40, bold=True)
        
        # 1. Vẽ tiêu đề menu
        title_surface = title_font.render("CHỌN MÀN CHƠI (SELECT MAP)", True, (255, 215, 0)) # Màu vàng gold
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 60))
        self.screen.blit(title_surface, title_rect)
        
        # 2. Duyệt qua danh sách các map để vẽ ra màn hình
        start_y = 160
        for i, map_name in enumerate(maps):
            if i == selected_index:
                text_color = (0, 255, 0) # Màu xanh lá
                display_text = f">  {map_name}  <"
            else:
                text_color = (255, 255, 255) # Màu trắng
                display_text = f"   {map_name}"
                
            text_surface = font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, start_y + i * 55))
            self.screen.blit(text_surface, text_rect)
            
        pygame.display.flip()

    def draw(self, game_state):
        """
        game_state là đối tượng SokobanGame từ Backend của bạn
        """
        self.screen.fill((0, 0, 0)) # Xóa màn hình bằng màu đen
        
        data = game_state.get_display_data()
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