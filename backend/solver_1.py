from collections import deque
from constants import UP, DOWN, LEFT, RIGHT
import heapq
def bfs_solver(game):
    #Lấy trạng thái khởi 
    start_state = game.get_initial_state() # self.palyer_pos = (x, y)  self.boxes = [(x1, y1), (x2, y2)]
    

    # Queue lưu: (trạng thái hiện tại, danh sách các bước đi để đến đây)
    queue = deque([(start_state, [])])

    # Set lưu các trạng thái đã đi qua để tránh lặp vô hạn
    visited = {start_state}
    
    directions = [UP, DOWN, LEFT, RIGHT]
    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}

    while queue:
        current_state, path = queue.popleft()
        
        # Kiểm tra nếu trạng thái này đã thắng chưa
        player_pos, boxes = current_state
        if game.is_win(boxes):
            return path # Trả về chuỗi các bước giải: ['U', 'R', 'D'...]

        # Thử đi 4 hướng
        for d in directions:
            next_state = game.get_next_state(current_state, d)
            
            if next_state and next_state not in visited:
                visited.add(next_state)
                # Lưu bước đi mới vào path và đẩy vào hàng đợi
                queue.append((next_state, path + [dir_names[d]]))
        

    return None 

def heuristic_mahhatan(state, targets):
    #khoang cach mahhatan 
    player_pos, boxes = state
    total_dist = 0

    for box in boxes:
        dists = [abs(box[0] - t[0]) + abs(box[1] - t[1]) for t in targets]
        total_dist += min(dists)
    return total_dist

def a_star_solver(game):
    
    start_state = game.get_initial_state() # self.palyer_pos = (x, y)  self.boxes = [(x1, y1), (x2, y2)]
    
    start_h = heuristic_mahhatan(start_state, game.targets) 
    
    # f = start_h vì f = g + h mà g = 0 vì chưa đi được bước nào => f=h = start_h ước lượng khoảng cách tuqwf 
    priority_queue = [(start_h, 0, start_state, [])]
    
    visited = {start_state: 0}   # state → chi phí tốt nhất (g) để tới state đó
    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}

    while priority_queue:
        
        f, g, current_state, path = heapq.heappop(priority_queue) # lấy ra phần tử có độ ưu tiên cao nhất fmin
        
        player_pos, box = current_state
        
        if game.is_win(box):
            return path 
        
        for d in [UP, DOWN, LEFT, RIGHT]:
            next_state = game.get_next_state(current_state, d)
            
            if next_state:
                new_g = g + 1 # Chi phí thực tế tăng thêm 1
                
                # Nếu chưa đi qua hoặc tìm thấy đường đến state này ngắn hơn đường cũ
                if next_state not in visited or new_g < visited[next_state]: 
                    visited[next_state] = new_g
                    h = heuristic_mahhatan(next_state, game.targets)
                    f = new_g + h
                    heapq.heappush(priority_queue, (f, new_g, next_state, path + [dir_names[d]]))
    return None


