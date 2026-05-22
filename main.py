from backend.core_logic import SokobanGame
# SOKOBAN_AI_PROJECT/main.py

import pygame
import sys
import os
from backend.core_logic import SokobanGame
from backend.solver_1 import bfs_solver, a_star_solver, a_star_push_based
from frontend.renderer import Renderer
from constants import *

def main():
    
    current_level = 1
    game = SokobanGame(f'data/maps/level{current_level}.txt')

    renderer = Renderer()
    clock = pygame.time.Clock()
    ALGORITHMS = [
        {"name": "BFS Solver", "func": bfs_solver},
        {"name": "A* Standard", "func": a_star_solver},
        {"name": "Push-based A*", "func": a_star_push_based}
    ]
    current_algo_idx = 0
    # --- CÁC BIẾN QUẢN LÝ TRẠNG THÁI AI CHẠY TỪNG BƯỚC ---
    ai_solution = []       # Lưu danh sách bước đi dạng mảng ['U', 'D', 'L', 'R']
    ai_step_index = 0      # Chỉ số bước hiện tại AI đang đi
    ai_move_delay = 0      # Thời gian phải chờ trước khi đi bước tiếp theo
    last_ai_move_time = 0  # Mốc thời gian (millisecond) của bước đi vừa rồi
    ai_metrics = None
    running = True
    while running:
        # Giới hạn game chạy chuẩn 60 FPS giúp giảm tải CPU
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    
                # Điều khiển thủ công bằng các phím mũi tên
                elif event.key == pygame.K_UP:    game.move(UP)
                elif event.key == pygame.K_DOWN:  game.move(DOWN)
                elif event.key == pygame.K_LEFT:  game.move(LEFT)
                elif event.key == pygame.K_RIGHT: game.move(RIGHT)
                elif event.key == pygame.K_u:     game.undo()
                elif event.key == pygame.K_r:     game.reset()

                elif event.key == pygame.K_n:
                    next_path = f'data/maps/level{current_level + 1}.txt'
                    if os.path.exists(next_path):
                        current_level += 1
                        game = SokobanGame(next_path)
                        renderer.update_screen_size(game.width, game.height)
                        ai_solution = [] 
                        ai_step_index = 0
                    else:
                        print("Map not found!")
                elif event.key == pygame.K_SPACE: 
                    solver_function = ALGORITHMS[current_algo_idx]["func"]
                    result = solver_function(game)
                    if result and isinstance(result, dict):
                        path = result.get("path", [])
                        if path is not None:
                            ai_solution = list(path) # Nạp chuỗi bước đi vào mảng tự chạy
                            ai_step_index = 0        # Bắt đầu đi từ bước đầu tiên
                            ai_move_delay = 0        # Chưa có delay ban đầu
                            last_ai_move_time = pygame.time.get_ticks() # Lấy mốc thời gian hiện tại
                            ai_metrics = result # Đổ dữ liệu (time, nodes) vào metrics
                        else:
                            ai_solution = []
                            ai_metrics = {"status": "No Solution Found!"}
                    else:
                        ai_solution = []
                        ai_metrics = {"status": "No Solution Found!"}
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # 1 nghĩa là click chuột trái
                    mouse_pos = event.pos # Lấy tọa độ (x, y) của chuột lúc click
                    # 🛠️ DÒNG DEBUG 1: In ra tọa độ chuột thực tế khi bạn click
                    
                    
                    # Tính toán vị trí các nút tương ứng với giao diện bên dưới
                    btn_x = renderer.sidebar_start_x + 15
                    btn_w = renderer.screen_width - renderer.sidebar_start_x - 30

                    btn_h = 40
                    
                    # Duyệt qua danh sách 3 nút để check va chạm tọa độ chuột
                    for idx in range(len(ALGORITHMS)):
                        btn_y = 80 + idx * 50 # Tọa độ y của từng nút
                        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
                        
                        if btn_rect.collidepoint(mouse_pos):
                            current_algo_idx = idx # Đổi thuật toán được chọn
                            game.reset()
                            ai_metrics = None      
                            ai_solution = []       
                
        if ai_solution and ai_step_index < len(ai_solution):
            current_time = pygame.time.get_ticks()
            # Chỉ cho phép đi bước tiếp theo nếu đã chờ đủ thời gian delay
            if current_time - last_ai_move_time > ai_move_delay:
                step = ai_solution[ai_step_index]
                
                # Nhân vật thực hiện ngầm đúng 1 bước di chuyển
                match step.upper():
                    case 'U': game.move(UP)
                    case 'D': game.move(DOWN)
                    case 'L': game.move(LEFT)
                    case 'R': game.move(RIGHT)
                
                ai_step_index += 1
                last_ai_move_time = current_time # Cập nhật lại mốc thời gian vừa bước đi
                
                # Thiết lập độ trễ động cho bước tiếp theo
                if step.isupper(): 
                    ai_move_delay = 100  # Nếu vừa ĐẨY HỘP (Chữ HOA) -> Đợi 100ms để người xem kịp nhìn
                else:
                    ai_move_delay = 0    # Nếu chỉ ĐI BỘ (Chữ thường) -> Khung hình sau đi luôn, lướt siêu nhanh
                
                # Check thắng game sau mỗi bước đi
                if game.is_win(set(game.boxes)):
                    ai_solution = [] # Dừng chạy khi đã thắng
                

        renderer.screen.fill((30, 30, 30))
        active_algo_name = ALGORITHMS[current_algo_idx]["name"]
        renderer.draw(
            game_state=game, 
            algo_name=active_algo_name, 
            metrics=ai_metrics, 
            current_algo_idx=current_algo_idx,
            ai_step_index=ai_step_index,
            current_level=current_level
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()