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
def hungarian_algorithm(cost_matrix):
    """
    Triển khai thuật toán Hungarian thuần Python để tìm tổng chi phí nhỏ nhất.
    cost_matrix: Danh sách 2 chiều (n x n)
    """
    n = len(cost_matrix)
    if n == 0:
        return 0
        
    # Tạo bản sao để thao tác dữ liệu
    cost = [row[:] for row in cost_matrix]
    
    # Bước 1: Trừ giá trị nhỏ nhất của mỗi dòng cho chính dòng đó
    for i in range(n):
        min_val = min(cost[i])
        for j in range(n):
            cost[i][j] -= min_val
            
    # Bước 2: Trừ giá trị nhỏ nhất của mỗi cột cho chính cột đó
    for j in range(n):
        min_val = min(cost[i][j] for i in range(n))
        for i in range(n):
            cost[i][j] -= min_val
            
    # Khởi tạo mảng đánh dấu ghép cặp
    match_row = [-1] * n
    match_col = [-1] * n
    
    # Hàm tìm đường tăng luồng (Augmenting Path) bằng DFS
    def dfs(u, visited_nodes, u_walls, v_walls):
        visited_nodes[u] = True
        for v in range(n):
            if not v_walls[v] and cost[u][v] == u_walls[u] + v_walls[v]:
                if match_col[v] < 0 or (not visited_nodes[match_col[v]] and dfs(match_col[v], visited_nodes, u_walls, v_walls)):
                    match_row[u] = v
                    match_col[v] = u
                    return True
        return False

    # Tiền trình tối ưu hóa nhãn (Kuhn-Munkres)
    u_walls = [0] * n
    v_walls = [0] * n
    
    for i in range(n):
        while match_row[i] < 0:
            visited_nodes = [False] * n
            if dfs(i, visited_nodes, u_walls, v_walls):
                break
                
            # Cập nhật nhãn nếu chưa tìm thấy đường tăng luồng
            delta = float('inf')
            for u in range(n):
                if visited_nodes[u]:
                    for v in range(n):
                        if match_col[v] < 0 or not visited_nodes[match_col[v]]:
                            val = cost[u][v] - u_walls[u] - v_walls[v]
                            if val < delta:
                                delta = val
            
            for u in range(n):
                if visited_nodes[u]:
                    u_walls[u] += delta
            for v in range(n):
                if match_col[v] >= 0 and visited_nodes[match_col[v]]:
                    v_walls[v] -= delta

    # Tính tổng khoảng cách gốc dựa trên các cặp đã chọn
    total_cost = 0
    for u in range(n):
        v = match_row[u]
        total_cost += cost_matrix[u][v]
        
    return total_cost
def heuristic_mahhatan(state, targets):
    _, boxes = state
    boxes = list(boxes)
    targets = list(targets)

    # BƯỚC 1: Xây dựng Ma trận chi phí (Cost Matrix)
    # Hàng (i) đại diện cho Hộp, Cột (j) đại diện cho Đích
    cost_matrix = []
    for box in boxes:
        row = []
        for t in targets:
            # Chi phí chính là khoảng cách Manhattan giữa hộp và đích
            dist = abs(box[0] - t[0]) + abs(box[1] - t[1])
            row.append(dist)
        cost_matrix.append(row)
    # BƯỚC 2: Xử lý cân bằng ma trận vuông (Padding) nếu số Hộp < số Đích (ta sẽ cho hộp bằng đích)
    # (Thuật toán Hungarian yêu cầu ma trận kích thước n x n)

    total_h = hungarian_algorithm(cost_matrix)
    return total_h

def a_star_solver(game):
    
    start_state = game.get_initial_state() # self.palyer_pos = (x, y)  self.boxes = [(x1, y1), (x2, y2)]
    
    start_h = heuristic_mahhatan(start_state, game.targets) 
    priority_queue = [(start_h, 0, start_state, [])]
    
    visited = {start_state: 0}  
    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}
    count = 0 # Biến đếm số trạng thái đã duyệt
    while priority_queue:
        
        f, g, current_state, path = heapq.heappop(priority_queue) # lấy ra phần tử có độ ưu tiên cao nhất fmin
        
        player_pos, box = current_state
        count += 1
        if count % 1000 == 0: # Cứ 1000 bước in ra 1 lần để check xem thuật toán có đang chạy không
            print(f"Đang duyệt... Bước thứ {count}, Kích thước Queue: {len(priority_queue)}, Trạng thái hiện tại: {current_state}")
        if game.is_win(set(box)):
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
    print(f"❌ Thất bại! Đã duyệt hết {count} trạng thái nhưng không tìm thấy đường đi.")
    return None


