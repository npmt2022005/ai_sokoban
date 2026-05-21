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
        """Cập nhật lại kích thước cửa sổ phù hợp với cấu hình hiển thị"""
        self.screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE))

    def draw_main_menu(self, selected_button_index):
        """Vẽ giao diện Main Menu chính theo nguyên mẫu thiết kế"""
        # 1. Tô màu nền Tím đậm toàn màn hình
        self.screen.fill((120, 0, 120))
        
        # Tính toán tọa độ hộp thoại Menu xám sáng nằm chính giữa màn hình
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()
        menu_w, menu_h = 400, 300
        menu_x = (screen_w - menu_w) // 2
        menu_y = (screen_h - menu_h) // 2
        
        # 2. Vẽ thân hộp thoại màu xám sáng
        pygame.draw.rect(self.screen, (220, 220, 220), (menu_x, menu_y, menu_w, menu_h))
        
        # 3. Vẽ thanh tiêu đề hộp thoại màu xám tối
        title_bar_h = 50
        pygame.draw.rect(self.screen, (70, 70, 70), (menu_x, menu_y, menu_w, title_bar_h))
        
        # 4. Vẽ chữ tiêu đề "Main Menu"
        font_title = pygame.font.SysFont(None, 36, bold=True)
        title_surface = font_title.render("Main Menu", True, (255, 255, 255))
        self.screen.blit(title_surface, (menu_x + 15, menu_y + 12))
        
        # 5. Khởi tạo cấu hình cho 2 nút tính năng: Play và Quit
        font_button = pygame.font.SysFont(None, 42)
        buttons = ["Play", "Quit"]
        start_button_y = menu_y + 100
        
        for i, btn_text in enumerate(buttons):
            # Kết xuất chữ (màu xám đen mặc định)
            text_color = (60, 60, 60)
            text_surface = font_button.render(btn_text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen_w // 2, start_button_y + i * 70))
            
            # Nếu nút đang được trỏ tới, vẽ khung viền trắng bao quanh chữ chữ như ảnh mẫu
            if i == selected_button_index:
                padding_x, padding_y = 20, 8
                border_rect = pygame.Rect(
                    text_rect.x - padding_x, 
                    text_rect.y - padding_y, 
                    text_rect.width + (padding_x * 2), 
                    text_rect.height + (padding_y * 2)
                )
                pygame.draw.rect(self.screen, (255, 255, 255), border_rect, 2) # Độ dày viền = 2px
                
            self.screen.blit(text_surface, text_rect)
            
        pygame.display.flip()

    def draw_map_selection_menu(self, maps, selected_index):
        """Vẽ giao diện Menu chọn danh sách Map (Sử dụng chuỗi không dấu tránh lỗi font)"""
        self.screen.fill((30, 30, 30)) 
        
        font = pygame.font.SysFont(None, 34)
        title_font = pygame.font.SysFont(None, 42, bold=True)
        
        title_surface = title_font.render("CHON MAN CHOI (SELECT MAP)", True, (255, 215, 0)) 
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # Định nghĩa vùng hiển thị cuộn danh sách (Hiển thị tối đa 7 dòng cùng lúc)
        max_visible_items = 7
        start_index = max(0, selected_index - max_visible_items + 1) if selected_index >= max_visible_items else 0
        end_index = min(len(maps), start_index + max_visible_items)
        
        start_y = 130
        for i in range(start_index, end_index):
            map_name = maps[i]
            if i == selected_index:
                text_color = (0, 255, 0) 
                display_text = f">  {map_name}  <"
            else:
                text_color = (255, 255, 255) 
                display_text = f"   {map_name}"
                
            text_surface = font.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, start_y + (i - start_index) * 45))
            self.screen.blit(text_surface, text_rect)
            
        pygame.display.flip()

    def draw(self, game_state):
        """Vẽ trạng thái thực tế của màn chơi Sokoban"""
        self.screen.fill((0, 0, 0)) 
        
        data = game_state.get_display_data()
        for r in range(data["height"]):
            for c in range(data["width"]):
                pos = (r, c)
                self.screen.blit(self.images[SPACE], (c * TILE_SIZE, r * TILE_SIZE))
                
                if pos in data["walls"]:
                    self.screen.blit(self.images[WALL], (c * TILE_SIZE, r * TILE_SIZE))
                if pos in data["targets"]:
                    self.screen.blit(self.images[TARGET], (c * TILE_SIZE, r * TILE_SIZE))
                if pos in data["boxes"]:
                    self.screen.blit(self.images[BOX], (c * TILE_SIZE, r * TILE_SIZE))
                if pos == data["player"]:
                    self.screen.blit(self.images[PLAYER], (c * TILE_SIZE, r * TILE_SIZE))
        
        pygame.display.flip()