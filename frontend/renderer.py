import pygame
from constants import *
from backend.core_logic import SokobanGame
import sys
# Kích thước mỗi ô vuông (pixel)
TILE_SIZE = 64
class Renderer:
    def __init__(self, screen_width = 1280 , screen_height = 720): 
        pygame.init()
        # 1. Cố định kích thước cửa sổ lớn ngay từ đầu để giữ layout ổn định
        self.screen_width = screen_width  # kích thước chiều cao và rộng của cửa sổ game
        self.screen_height = screen_height   # kích thước chiều cao và rộng của cửa sổ game
        pygame.display.set_caption("Sokoban AI Project - Evaluation Dashboard")
        
        self.map_area_width = int(self.screen_width * 0.75)  # Chiều rộng của của sổ game chiếm 75%
        self.sidebar_start_x = self.map_area_width   # tọa độ trục X bắt đầu của thánh SizeBar thông số 

        self.tile_size = 64  # kích thước ô vuông trên bản đồ 
        self.raw_images = {
            WALL: pygame.image.load('frontend/assets/wall.png'),
            BOX: pygame.image.load('frontend/assets/box.png'),
            TARGET: pygame.image.load('frontend/assets/target.png'),
            PLAYER: pygame.image.load('frontend/assets/player.png'),
            SPACE: pygame.image.load('frontend/assets/space.png')
        }
        self.images = self.raw_images.copy()

        self.font_sm = pygame.font.SysFont('Arial', 20)
        self.font_md = pygame.font.SysFont('Arial', 24, bold=True)
        self.font_lg = pygame.font.SysFont('Arial', 36, bold=True)
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            pygame.RESIZABLE
)

    def update_screen_size(self, width, height):
        """Cập nhật lại kích thước cửa sổ phù hợp với kích thước của Map mới"""
        # Tính toán kích thước ô tối đa có thể dựa trên số hàng/cột của map mới
        max_tile_w = self.map_area_width // width # width là số cột của map mới 
        max_tile_h = self.screen_height // height # height là số hàng của map mới 

        self.tile_size = max(32, min(max_tile_w, max_tile_h, 128))
        # Resize lại toàn bộ bộ ảnh theo kích thước mới
        for key, img in self.raw_images.items():
            self.images[key] = pygame.transform.scale(img, (self.tile_size, self.tile_size))

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
        
        start_y = 200
        for i, map_name in enumerate(maps):
            if i == selected_index:
                text_color = (0, 255, 0)
                display_text = f">  {map_name}  <"
            else:
                text_color = (255, 255, 255)
                display_text = f"   {map_name}"
                
            text_surface = self.font_md.render(display_text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, start_y + i * 55))
            self.screen.blit(text_surface, text_rect)
            
        pygame.display.flip()
    def draw(self, game_state, algo_name="BFS Solver", metrics=None, current_algo_idx=0,ai_step_index=0, current_level=1):
        self.screen.fill((20, 20, 20)) # Nền xám đen tổng thể hiện đại
        
        data = game_state.get_display_data()
    
        # 1. TÍNH TOÀN TỌA ĐỘ CĂN GIỮA MAP (Center Alignment)
        map_total_width = data["width"] * self.tile_size
        map_total_height = data["height"] * self.tile_size
        
        # Căn lề để map nằm chính giữa vùng quy định
        offset_x = (self.map_area_width - map_total_width) // 2
        offset_y = (self.screen_height - map_total_height) // 2

        # 2. VẼ BẢN ĐỒ GAME (Chiếm trọn không gian bên trái)
        for r in range(data["height"]):
            for c in range(data["width"]):
                pos = (r, c)
                screen_pos_x = offset_x + (c * self.tile_size)
                screen_pos_y = offset_y + (r * self.tile_size)
                
                # Vẽ sàn trống trước
                self.screen.blit(self.images[SPACE], (screen_pos_x, screen_pos_y))
                
                # Vẽ các vật thể đè lên
                if pos in data["walls"]:
                    self.screen.blit(self.images[WALL], (screen_pos_x, screen_pos_y))
                if pos in data["targets"]:
                    self.screen.blit(self.images[TARGET], (screen_pos_x, screen_pos_y))
                if pos in data["boxes"]:
                    self.screen.blit(self.images[BOX], (screen_pos_x, screen_pos_y))
                if pos == data["player"]:
                    self.screen.blit(self.images[PLAYER], (screen_pos_x, screen_pos_y))

        # 3. VẼ SIDEBAR THÔNG SỐ (Dành riêng 25% màn hình bên phải cho báo cáo)
        # Khung nền Sidebar
        sidebar_rect = pygame.Rect(self.sidebar_start_x, 0, self.screen_width - self.sidebar_start_x, self.screen_height)
        pygame.draw.rect(self.screen, (40, 40, 40), sidebar_rect)
        pygame.draw.line(self.screen, (70, 70, 70), (self.sidebar_start_x, 0), (self.sidebar_start_x, self.screen_height), 2)

        # --- THIẾT KẾ MENU NÚT BẤM CHỌN THUẬT TOÁN ---
        algo_title = self.font_md.render("SELECT ALGORITHM:", True, (200, 200, 200))
        self.screen.blit(algo_title, (self.sidebar_start_x + 20, 35))

        # Định nghĩa danh sách tên nút giống hệt bên main
        algo_names = ["BFS Solver", "A* Standard", "Push-based A*"]

        btn_x = self.sidebar_start_x + 15
        btn_w = self.screen_width - self.sidebar_start_x - 30
        btn_h = 40
        btn_y_start = 80

        for idx, name in enumerate(algo_names):
            current_btn_y = btn_y_start + idx * 50
            btn_rect = pygame.Rect(btn_x, current_btn_y, btn_w, btn_h)
            
            # Nếu nút này ĐANG ĐƯỢC CHỌN -> Tô màu xanh Cyan thẫm, ngược lại tô màu xám tối
            if idx == current_algo_idx :
                bg_color = (0, 80, 100)      # Xanh Cyan đặc trưng đang active
                border_color = (0, 255, 255)  # Viền sáng rực
                text_color = (0, 255, 255)
            else:
                bg_color = (45, 45, 45)       # Màu nút bình thường
                border_color = (70, 70, 70)   # Viền mờ
                text_color = (160, 160, 160)

            # Vẽ nền nút bấm bo góc nhẹ cho đẹp
            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, btn_rect, width=1, border_radius=6)
            
            # Vẽ chữ tên thuật toán căn giữa vào trong nút
            name_surf = self.font_sm.render(name, True, text_color)
            # Tính toán tọa độ để chữ nằm chính giữa nút bấm
            text_x = btn_rect.x + 15
            text_y = btn_rect.y + (btn_h - name_surf.get_height()) // 2
            self.screen.blit(name_surf, (text_x, text_y))

        if metrics is None:
            # Trạng thái 1: Chưa giải thuật toán (Mới mở game hoặc vừa click đổi nút)
            time_str = "Ready"
            nodes_str = "0"
            steps_str = "0"
        elif "status" in metrics and metrics["status"] == "No Solution Found!":
            # Trạng thái 2: Thuật toán chạy thất bại/Map lỗi không giải được
            time_str = "Failed"
            nodes_str = "Unsolvable"
            steps_str = "No Path!"
        else:
            # Trạng thái 3: Giải toán thành công, hiển thị số liệu thực tế từ AI
            time_str = f"{metrics.get('time_seconds', 0.0):.4f} s"
            nodes_str = f"{metrics.get('nodes_generated', 0):,}"


            # Tính toán độ dài chuỗi bước đi
            if "path" in metrics and metrics["path"] is not None:
                steps_str = f"{len(metrics['path'])} steps"
            else:
                steps_str = f"{metrics.get('steps', 0)} steps"
                
        is_failed = metrics and "status" in metrics and metrics["status"] == "No Solution Found!"
        metrics_labels = [
        (" EXECUTION TIME", time_str, (255, 100, 100) if is_failed else (144, 238, 144)),  # Đỏ lỗi / Xanh lá sáng
        (" NODES GENERATED", nodes_str, (255, 100, 100) if is_failed else (255, 218, 185)), # Đỏ lỗi / Màu đào
        (" SOLUTION LENGTH", steps_str, (255, 100, 100) if is_failed else (173, 216, 230))  # Đỏ lỗi / Xanh dương nhạt
    ]

            # Tịnh tiến tọa độ Y xuống vị trí 250 để không đè lên menu nút bấm
        card_y = 250
        for title, value, color in metrics_labels:
            card_rect = pygame.Rect(self.sidebar_start_x + 15, card_y, self.screen_width - self.sidebar_start_x - 30, 80)
            
            # Vẽ viền bo các ô thống kê nhìn cho chuyên nghiệp
            pygame.draw.rect(self.screen, (50, 50, 50), card_rect, border_radius=8)
            pygame.draw.rect(self.screen, (80, 80, 80), card_rect, width=1, border_radius=8)
            
            # Đổ chữ tiêu đề và giá trị vào thẻ thống kê
            lbl_surf = self.font_sm.render(title, True, (180, 180, 180))
            val_surf = self.font_md.render(value, True, color)
            self.screen.blit(lbl_surf, (card_rect.x + 15, card_rect.y + 15))
            self.screen.blit(val_surf, (card_rect.x + 15, card_rect.y + 42))
            
            card_y += 110
            # --- VẼ TIẾN ĐỘ CHẠY THỰC TẾ (Đặt ở dưới đáy Sidebar) ---
            # Tính toán vị trí Y nằm dưới Card cuối cùng (ví dụ card cuối ở khoảng Y=470)
        info_y = 590 
        
        level_surf = self.font_sm.render(f"📍 CURRENT MAP: Level {current_level}", True, (200, 200, 200))
        self.screen.blit(level_surf, (self.sidebar_start_x + 20, info_y))
        
        # Nếu AI đang chạy tự động, tính toán in ra số bước đi động
        if metrics and "status" in metrics and metrics["status"] == "Success":
            path_data = metrics.get("path", [])
            total_steps = len(path_data) if path_data else 0
            
            if total_steps > 0:
                # Kiểm tra nếu nhân vật đã đi hết danh sách bước giải của AI
                if ai_step_index >= total_steps:
                    progress_text = f"PROGRESS: Completed! ({total_steps}/{total_steps})"
                    text_color = (144, 238, 144) # Màu xanh lá sáng báo hoàn thành
                else:
                    progress_text = f"PROGRESS: {ai_step_index} / {total_steps} steps"
                    text_color = (0, 255, 255)   # Màu xanh Cyan khi đang tự chạy bước đi
                    
                # Vẽ chuỗi tiến độ ra màn hình ngay phía dưới tên Map (tịnh tiến Y xuống 25px)
                progress_surf = self.font_sm.render(progress_text, True, text_color)
                self.screen.blit(progress_surf, (self.sidebar_start_x + 20, info_y + 25))
            
            
            
        pygame.display.flip()