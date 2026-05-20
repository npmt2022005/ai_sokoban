import pygame
import sys
import os
from backend.core_logic import SokobanGame
from backend.solver_1 import bfs_solver, a_star_solver
from frontend.renderer import Renderer
from constants import *

def get_all_maps(map_dir):
    """Quét và lấy danh sách tất cả các file .txt có trong thư mục data/maps"""
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
    return [f for f in os.listdir(map_dir) if f.endswith('.txt')]

def main():
    pygame.init()
    
    MAP_DIR = 'data/maps'
    maps_list = get_all_maps(MAP_DIR)
    
    # Nếu không tìm thấy map nào, thông báo lỗi và thoát
    if not maps_list:
        print(f"Không tìm thấy bản đồ nào trong thư mục '{MAP_DIR}'. Vui lòng thêm file .txt vào!")
        pygame.quit()
        sys.exit()

    renderer = Renderer(10, 8)
    
    selecting_map = True
    selected_index = 0
    
    while selecting_map:
        renderer.draw_map_selection_menu(maps_list, selected_index)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # Di chuyển lựa chọn lên trên
                    selected_index = (selected_index - 1) % len(maps_list)
                elif event.key == pygame.K_DOWN:
                    # Di chuyển lựa chọn xuống dưới
                    selected_index = (selected_index + 1) % len(maps_list)
                elif event.key == pygame.K_RETURN: # Phím ENTER
                    # Xác nhận chọn map và chuyển sang chơi game
                    selecting_map = False

    # Lấy đường dẫn map hoàn chỉnh đã được chọn
    chosen_map_path = os.path.join(MAP_DIR, maps_list[selected_index])
    print(f"Đang tải bản đồ: {chosen_map_path}")
    
    game = SokobanGame(chosen_map_path)
    
    # Cập nhật lại kích thước hiển thị của màn hình theo đúng kích thước map thực tế
    renderer.update_screen_size(game.width, game.height)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
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
                elif event.key == pygame.K_SPACE: 
                    print("AI đang tìm đường...")
                    solution = a_star_solver(game)
                    if solution:
                        print(f"Tìm thấy lời giải sau {len(solution)} bước!")
                        for step in solution:
                            if step == 'U': game.move(UP)
                            elif step == 'D': game.move(DOWN)
                            elif step == 'L': game.move(LEFT)
                            elif step == 'R': game.move(RIGHT)
                            renderer.draw(game) 
                            pygame.time.delay(200) # Nghỉ 200ms để người xem kịp nhìn
                    else:
                        print("AI không tìm thấy đường!")
            
        renderer.draw(game)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()