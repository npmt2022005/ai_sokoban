import pygame
import sys
import os
import re
from backend.core_logic import SokobanGame
from backend.solver_1 import bfs_solver, a_star_solver
from frontend.renderer import Renderer
from constants import *

# Định nghĩa các trạng thái hoạt động của Game bằng hằng số
STATE_MAIN_MENU = "MAIN_MENU"
STATE_MAP_SELECT = "MAP_SELECT"
STATE_GAMEPLAY = "GAMEPLAY"

def get_all_maps(map_dir):
    """Quét và sắp xếp các file map theo đúng thứ tự số đếm tự nhiên (1, 2, ..., 10, 11)"""
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
        
    files = [f for f in os.listdir(map_dir) if f.endswith('.txt')]
    
    # Hàm tách chuỗi ký tự và số nguyên để làm bộ khóa sắp xếp tự nhiên
    def natural_sort_key(filename):
        return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]
    
    files.sort(key=natural_sort_key)
    return files

def main():
    pygame.init()
    
    MAP_DIR = 'data/maps'
    maps_list = get_all_maps(MAP_DIR)
    
    if not maps_list:
        print(f"Khong tim thay ban do nao trong thu muc '{MAP_DIR}'!")
        pygame.quit()
        sys.exit()

    # Thiết lập kích thước cửa sổ Menu ban đầu là 10x8 ô tương đương 640x512 pixel
    renderer = Renderer(10, 8)
    
    # Khởi tạo các biến quản lý trạng thái trò chơi
    current_game_state = STATE_MAIN_MENU
    selected_button_index = 0  # 0: Play, 1: Quit
    selected_map_index = 0     # Chỉ mục map đang trỏ tới trong danh sách
    game = None                # Biến lưu trữ thực thể logic game sau khi chọn map

    running = True
    while running:
        
        # --- PHÂN ĐOẠN 1: XỬ LÝ VẼ GIAO DIỆN THEO TRẠNG THÁI CHUYỂN ĐỔI ---
        if current_game_state == STATE_MAIN_MENU:
            renderer.draw_main_menu(selected_button_index)
        elif current_game_state == STATE_MAP_SELECT:
            renderer.draw_map_selection_menu(maps_list, selected_map_index)
        elif current_game_state == STATE_GAMEPLAY:
            renderer.draw(game)

        # --- PHÂN ĐOẠN 2: LẮNG NGHE VÀ SỬ LÝ SỰ KIỆN PHÍM BẤM ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                
                # SỰ KIỆN CHO TRẠNG THÁI: MAIN MENU CHÍNH
                if current_game_state == STATE_MAIN_MENU:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        # Đảo lựa chọn giữa nút Play (0) và nút Quit (1)
                        selected_button_index = 1 - selected_button_index
                    elif event.key == pygame.K_RETURN:  # Phím ENTER
                        if selected_button_index == 0:  # Chọn nút PLAY
                            current_game_state = STATE_MAP_SELECT
                        elif selected_button_index == 1:  # Chọn nút QUIT
                            running = False

                # SỰ KIỆN CHO TRẠNG THÁI: MENU CHỌN MAP
                elif current_game_state == STATE_MAP_SELECT:
                    if event.key == pygame.K_UP:
                        selected_map_index = (selected_map_index - 1) % len(maps_list)
                    elif event.key == pygame.K_DOWN:
                        selected_map_index = (selected_map_index + 1) % len(maps_list)
                    elif event.key == pygame.K_ESCAPE:  # Ấn ESC để quay ngược lại Menu chính
                        current_game_state = STATE_MAIN_MENU
                    elif event.key == pygame.K_RETURN:  # Xác nhận chọn Map thành công
                        chosen_map_path = os.path.join(MAP_DIR, maps_list[selected_map_index])
                        print(f"Dang tai ban do: {chosen_map_path}")
                        
                        # Khởi tạo thực thể màn chơi mới và co giãn kích thước màn hình phù hợp
                        game = SokobanGame(chosen_map_path)
                        renderer.update_screen_size(game.width, game.height)
                        current_game_state = STATE_GAMEPLAY

                # LAO LÝ SỰ KIỆN CHO TRẠNG THÁI: ĐANG TRONG TRÒ CHƠI (GAMEPLAY)
                elif current_game_state == STATE_GAMEPLAY:
                    if event.key == pygame.K_UP:
                        game.move(UP)
                    elif event.key == pygame.K_DOWN:
                        game.move(DOWN)
                    elif event.key == pygame.K_LEFT:
                        game.move(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        game.move(RIGHT)
                    elif event.key == pygame.K_u:
                        game.undo()
                    elif event.key == pygame.K_r: 
                        game.reset()
                    elif event.key == pygame.K_ESCAPE:  # Ấn ESC khi đang chơi để thoát ra chọn Map lại
                        # Đặt lại kích thước cửa sổ mặc định cho Menu
                        renderer.update_screen_size(10, 8)
                        current_game_state = STATE_MAP_SELECT
                    elif event.key == pygame.K_SPACE: 
                        print("AI dang tim duong phat trien...")
                        solution = a_star_solver(game)
                        if solution:
                            print(f"Tim thay loi giai sau {len(solution)} buoc di!")
                            for step in solution:
                                if step == 'U': game.move(UP)
                                elif step == 'D': game.move(DOWN)
                                elif step == 'L': game.move(LEFT)
                                elif step == 'R': game.move(RIGHT)
                                renderer.draw(game) 
                                pygame.time.delay(200) 
                        else:
                            print("AI khong tim thay phuong an giai quyet!")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()