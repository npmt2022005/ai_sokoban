from backend.core_logic import SokobanGame
# SOKOBAN_AI_PROJECT/main.py

import pygame
import sys
from backend.core_logic import SokobanGame
from backend.solver_1 import bfs_solver, a_star_solver
from frontend.renderer import Renderer
from constants import *

def main():
  
    game = SokobanGame('data/maps/map_test.txt')
    
    renderer = Renderer(game.width, game.height)
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
                        # Kiểm tra xem sau bước đi này đã thắng chưa
                # if game.is_win(game.boxes):
                #     print("Chúc mừng! Bạn đã thắng!")
            
        renderer.draw(game)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()