from collections import deque
from constants import UP, DOWN, LEFT, RIGHT
import heapq
from backend.core_logic import SokobanGame
import os, glob
import pygame
import time
INF = float('inf')
def bfs_solver(game):
    start_time = time.time()
    nodes_generated = 0  # Đếm số trạng thái thuật toán đã sinh ra
    #Lấy trạng thái khởi 
    start_state = game.get_initial_state() # self.palyer_pos = (x, y)  self.boxes = [(x1, y1), (x2, y2)]
    simple_deadlocks = game.simple_deadlocks 

    # Queue lưu: (trạng thái hiện tại, danh sách các bước đi để đến đây)
    queue = deque([(start_state, [])])

    # Set lưu các trạng thái đã đi qua để tránh lặp vô hạn
    visited = {start_state}
    
    directions = [UP, DOWN, LEFT, RIGHT]
    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}

    while queue:
        current_state, path = queue.popleft()
        player_pos, boxes = current_state
        # Kiểm tra nếu trạng thái này đã thắng chưa
        if game.is_win(boxes):
            execution_time = time.time() - start_time
            return {
                "status": "Success",
                "path": path,
                "steps": len(path),
                "nodes_generated": nodes_generated,
                "time_seconds": execution_time
            }

        # Thử đi 4 hướng
        for d in directions:
            next_state = game.get_next_state(current_state, d)
            
            if next_state:
                nodes_generated += 1  # Ghi nhận sinh thêm 1 trạng thái hợp lệ
                if any(box in simple_deadlocks for box in next_state[1]):
                    continue
                if next_state not in visited:
                    visited.add(next_state)
                    queue.append((next_state, path + [dir_names[d]]))
    execution_time = time.time() - start_time
    return {
        "status": "Failed",
        "path": None,
        "steps": -1,
        "nodes_generated": nodes_generated,
        "time_seconds": execution_time
    }
def hungarian(cost_matrix: list[list[int | float]]) -> tuple[int | float, list[tuple[int, int]]]:
    """
    Thuật toán Hungarian chuẩn — O(n³)

    Parameters
    ----------
    cost_matrix : ma trận chi phí n×n
                cost_matrix[i][j] = chi phí gán hàng i cho cột j

    Returns
    -------
    (min_cost, assignment)
        min_cost   : tổng chi phí nhỏ nhất
        assignment : danh sách [(row, col), ...] — mỗi hàng được gán 1 cột
    """
    n = len(cost_matrix)
    matrix = [row[:] for row in cost_matrix]

    # ── BƯỚC 1: Trừ min từng hàng ────────────────────────────────────────
    for i in range(n):
        row_min = min(matrix[i])
        for j in range(n):
            matrix[i][j] -= row_min

    # ── BƯỚC 2: Trừ min từng cột ─────────────────────────────────────────
    for j in range(n):
        col_min = min(matrix[i][j] for i in range(n))
        for i in range(n):
            matrix[i][j] -= col_min

    # Vòng lặp chính
    while True:
        # ── BƯỚC 3: Tìm maximum matching trên các ô bằng 0 ───────────────
        # Dùng augmenting path (bipartite matching)
        match_row = [-1] * n  # match_row[i] = cột được gán cho hàng i
        match_col = [-1] * n  # match_col[j] = hàng được gán cho cột j

        def try_augment(row, visited_cols):
            for col in range(n):
                if matrix[row][col] == 0 and col not in visited_cols:
                    visited_cols.add(col)
                    if match_col[col] == -1 or try_augment(match_col[col], visited_cols):
                        match_row[row] = col
                        match_col[col] = row
                        return True
            return False

        for i in range(n):
            try_augment(i, set())

        assigned_count = sum(1 for a in match_row if a != -1)
        if assigned_count == n:
            break  # Tìm đủ n phân công → xong

        # ── BƯỚC 4: Tìm đường bao tối thiểu (König's theorem) ────────────
        # Đánh dấu hàng chưa được gán, lan sang cột/hàng liên quan
        marked_rows = set(i for i in range(n) if match_row[i] == -1)
        marked_cols = set()

        changed = True
        while changed:
            changed = False
            for i in list(marked_rows):
                for j in range(n):
                    if matrix[i][j] == 0 and j not in marked_cols:
                        marked_cols.add(j)
                        changed = True
            for j in list(marked_cols):
                i = match_col[j]
                if i != -1 and i not in marked_rows:
                    marked_rows.add(i)
                    changed = True

        # Cover = hàng KHÔNG đánh dấu + cột CÓ đánh dấu
        cover_rows = set(range(n)) - marked_rows
        cover_cols = marked_cols

        # ── BƯỚC 5: Tìm giá trị nhỏ nhất ngoài vùng cover ────────────────
        min_val = INF
        for i in range(n):
            for j in range(n):
                if i not in cover_rows and j not in cover_cols:
                    if matrix[i][j] < min_val:
                        min_val = matrix[i][j]

        # ── BƯỚC 6: Cập nhật ma trận ──────────────────────────────────────
        # Không cover → trừ min_val
        # Cover 2 lần  → cộng min_val
        # Cover 1 lần  → giữ nguyên
        for i in range(n):
            for j in range(n):
                row_cvr = i in cover_rows
                col_cvr = j in cover_cols
                if not row_cvr and not col_cvr:
                    matrix[i][j] -= min_val
                elif row_cvr and col_cvr:
                    matrix[i][j] += min_val

    # ── Tính kết quả ─────────────────────────────────────────────────────
    assignment = [(i, match_row[i]) for i in range(n)]
    min_cost   = sum(cost_matrix[i][j] for i, j in assignment)
    return min_cost, assignment
def heuristic_manhattan(state, targets):
    _, boxes = state
    targets = set(targets)

    # Chỉ tính hộp chưa ở đúng vị trí
    unmatched_boxes   = [b for b in boxes   if b not in targets]
    unmatched_targets = [t for t in targets if t not in boxes]

    if not unmatched_boxes:
        return 0

    cost_matrix = [
        [abs(b[0]-t[0]) + abs(b[1]-t[1]) for t in unmatched_targets]
        for b in unmatched_boxes
    ]

    min_cost, _ = hungarian(cost_matrix)
    return min_cost


from collections import deque
def get_reachable_zone(player_pos, boxes, walls):
    """
    BFS flood-fill: tìm tất cả ô player có thể đến được
    mà không cần đẩy thêm hộp nào.
    """
    reachable_paths = {player_pos: ""}
    queue = deque([player_pos])
    box_set = frozenset(boxes)
    dir_chars = {UP: "u", DOWN: "d", LEFT: "l", RIGHT: "r"}
    while queue:
        pos = queue.popleft()
        curr_path = reachable_paths[pos]
        x, y = pos
        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            neighbor = (x + dx, y + dy)
            if neighbor in walls or neighbor in box_set:
                continue
                

            if neighbor not in reachable_paths:
                # Đường đi đến ô hàng xóm = đường đến ô hiện tại + ký tự hướng đi mới
                direction_tuple = (dx, dy)
                reachable_paths[neighbor] = curr_path + dir_chars[direction_tuple]
                
                # Cho ô hàng xóm vào hàng đợi để quét tiếp xung quanh nó
                queue.append(neighbor)
    return reachable_paths


def get_canonical_player(reachable):
    """
    Dùng ô top-left nhất làm đại diện cho toàn vùng reachable.
    Mọi state có cùng vùng đi bộ → cùng canonical → không bị duplicate.
    """
    return min(reachable)  # min theo (row, col)

def get_all_pushes(reachable, boxes, walls):
    """
    Sinh tất cả các lần đẩy hộp hợp lệ:
    - Player phải đứng được ở ô phía sau hộp (trong reachable)
    - Ô phía trước hộp phải trống (không tường, không hộp)
    
    Yields: (box_pos, new_box_pos, direction, player_must_stand_at)
    """
    box_set = frozenset(boxes)
    
    for box in boxes:
        bx, by = box
        for dx, dy in [UP, DOWN, LEFT, RIGHT]:
            # Ô player phải đứng để đẩy = phía đối diện chiều đẩy
            player_required = (bx - dx, by - dy)
            # Ô hộp sẽ đến
            box_destination = (bx + dx, by + dy)

            if player_required not in reachable:
                continue  # player không đến được chỗ cần đứng
            if box_destination in walls:
                continue  # hộp bị chặn bởi tường
            if box_destination in box_set:
                continue  # hộp bị chặn bởi hộp khác
            
            #box: Vị trí hiện tại của hộp.
            #box_destination: Vị trí mới của hộp sau khi đẩy.
            # (dx, dy): Hướng đẩy (để lưu vào chuỗi đáp án path).
            # player_required: Ô mà player sẽ đứng để thực hiện cú đẩy (sau khi đẩy xong thì player cũng sẽ di chuyển vào ô box cũ).
            yield (box, box_destination, (dx, dy), player_required) 
            

def print_current_map_state(walls, boxes, player_pos, title="TRẠNG THÁI MAP"):
    # Tìm kích thước map tự động
    max_r = max(r for r, c in walls) + 1
    max_c = max(c for r, c in walls) + 1
    
    print(f"\n--- {title} ---")
    for r in range(max_r):
        row_str = ""
        for c in range(max_c):
            pos = (r, c)
            if pos in walls:
                row_str += "#"  # Tường
            elif pos == player_pos:
                row_str += "@"  # Người chơi
            elif pos in boxes:
                row_str += "$"  # Cái hộp
            else:
                row_str += "."  # Ô trống
        print(row_str)
    print("-" * (len(title) + 8))
def a_star_push_based(game):
    start_time = time.time() 
    walls = game.walls
    targets = game.targets
    heuristic_cache = {}
    start_player, start_boxes = game.get_initial_state() # vị trí bạn đầu của người , và tất cả các hộp
    start_boxes_fs = frozenset(start_boxes)  # vị trí tất cả các hộp 
    simple_deadlock_map = game.get_static_deadlock_location1()

    # Canonical player = top-left của vùng reachable ban đầu
    start_reachable = get_reachable_zone(start_player, start_boxes_fs, walls) # tất cả ô mà người đi bộ có thể đi 
    start_canonical = get_canonical_player(start_reachable.keys()) # ô đại diện cho tất cả các ô 
    start_state = (start_canonical, start_boxes_fs) # 
    walk_to_canonical = start_reachable[start_canonical]
    start_h = heuristic_manhattan(start_state, targets)
    priority_queue = [(start_h, 0, start_state, [])]
    visited = {start_state: 0}

    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}
    count = 0

    while priority_queue:
        f, g, current_state, path = heapq.heappop(priority_queue)
        canonical_player, boxes = current_state
        count += 1
        # Lazy deletion
        if visited.get(current_state, float('inf')) < g:
            continue

        if count % 500 == 0:
            print(f"[{count}] f={f} g={g} h={f-g} | boxes={len(boxes)} | queue={len(priority_queue)}")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 🛠️ SỬA TẠI ĐÂY: Trả về trạng thái thoát trước khi sập
                    return {"status": "No Solution Found!", "path": None}

        if game.is_win(set(boxes)):
            print(f"✅ AI ĐÃ GIẢI THÀNH CÔNG! Đang dựng lại chuỗi hành động...")
            full_action_string = ""
            curr_player = start_player  # start_player là vị trí ban đầu lúc mới vào game
            curr_boxes = set(start_boxes_fs)
            
            # Duyệt qua từng lịch sử cú đẩy thô để tính đường đi bộ thực tế tương ứng
            for player_required, direction, old_box_pos in path:
                # Quét tìm đường đi bộ từ vị trí THỰC TẾ đang đứng hiện tại
                reachable_now = get_reachable_zone(curr_player, frozenset(curr_boxes), walls)
                
                # Nối chuỗi đi bộ đến cạnh hộp
                full_action_string += reachable_now[player_required]
                
                # Nối ký tự đẩy hộp tương ứng
                dir_names_push = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}
                full_action_string += dir_names_push[direction]
                
                # Cập nhật cơ thể vật lý của người chơi và hộp để tính tiếp bước sau
                dx, dy = direction
                new_box_pos = (old_box_pos[0] + dx, old_box_pos[1] + dy)
                curr_player = old_box_pos  # Đẩy xong player đứng thế chỗ cũ của hộp
                curr_boxes.remove(old_box_pos)
                curr_boxes.add(new_box_pos)
            # 🛠️ SỬA TẠI ĐÂY: Tính toán thời gian và đóng gói kết quả đầu ra
            end_time = time.time()
            execution_time = end_time - start_time

            return {
                "status": "Success",
                "path": list(full_action_string), # Biến đổi chuỗi thành mảng các ký tự để main.py duyệt qua
                "steps": len(full_action_string),
                "nodes_generated": count,         # Biến count của bạn chính là số nút đã duyệt qua
                "time_seconds": execution_time
            }

        # Khôi phục vùng reachable từ canonical player
        # (cần 1 ô bất kỳ trong vùng — dùng canonical vì nó chắc chắn trong vùng)
        reachable_paths = get_reachable_zone(canonical_player, boxes, walls)

        new_g = g + 1  # Mỗi lần đẩy hộp = 1 bước
        reachable_set = reachable_paths.keys()
        for box, new_box, direction, player_required in get_all_pushes(reachable_set, boxes, walls):
            # Cập nhật tập hộp
            new_boxes = (boxes - {box}) | {new_box}
            new_boxes_fs = frozenset(new_boxes)

            # Pruning: static deadlock
            if new_box in simple_deadlock_map:
                continue

            # Pruning: freeze deadlock
            if game.is_freeze_deadlock(new_boxes_fs):
                continue
            
            # Sau khi đẩy, player đứng tại vị trí cũ của hộp
            new_player_pos = box
            
            
            # Đoạn C: Đường đi bộ từ vị trí sau khi đẩy (new_player_pos) về ô Canonical MỚI
            # Để đưa Player về trạng thái chuẩn hóa, chuẩn bị cho bước tiếp theo
            next_reachable_paths = get_reachable_zone(new_player_pos, new_boxes_fs, walls)
            new_canonical = min(next_reachable_paths.keys())
            new_path = path + [(player_required, direction, box)]

            # Tạo trạng thái mới để lưu vào visited và Queue
            new_state = (new_canonical, new_boxes_fs)
            
            if new_g >= visited.get(new_state, float('inf')):
                continue

            visited[new_state] = new_g
            if new_boxes_fs in heuristic_cache:
                h = heuristic_cache[new_boxes_fs] # Bốc kết quả có sẵn ra dùng luôn, tốn 0ms!
            else:
                # Nếu chưa có trong Cache, ta mới gọi hàm Hungarian để tính toán
                h = heuristic_manhattan(new_state, targets) 
                heuristic_cache[new_boxes_fs] = h # Lưu lại để hàng ngàn node sau dùng ké
            next_f = new_g + h
            heapq.heappush(priority_queue, (next_f, new_g, new_state, new_path))

    print(f"❌ Thất bại! Đã duyệt hết {count} push-states.")
    print(f"❌ Thất bại! Đã duyệt hết {count} push-states.")
    
    # 🛠️ SỬA TẠI ĐÂY: Thay thế return None bằng Dictionary lỗi
    end_time = time.time()
    return {
        "status": "No Solution Found!",
        "path": None,
        "steps": 0,
        "nodes_generated": count,
        "time_seconds": end_time - start_time
    }

def a_star_solver(game):
    
    start_state = game.get_initial_state() # self.palyer_pos = (x, y)  self.boxes = [(x1, y1), (x2, y2)]

    start_player, start_boxes = start_state
    start_time = time.time()
    start_boxes_fs = frozenset(start_boxes)
    normalized_start = (start_player, start_boxes_fs)

    simple_deadlock_map = game.get_static_deadlock_location1()
    
    start_h = heuristic_manhattan(normalized_start, game.targets)

    priority_queue = [(start_h, 0, normalized_start, [])]
    
    visited = {normalized_start: 0}  
    dir_names = {UP: "U", DOWN: "D", LEFT: "L", RIGHT: "R"}
    count = 0 # Biến đếm số trạng thái đã duyệt
    while priority_queue:
        
        f, g, current_state, path = heapq.heappop(priority_queue) # lấy ra phần tử có độ ưu tiên cao nhất fmin
        
        player_pos, box = current_state
        count += 1
        if count % 1000 == 0: # Cứ 1000 bước in ra 1 lần để check xem thuật toán có đang chạy không
            print(f"Đang duyệt... Bước thứ {count}, Kích thước Queue: {len(priority_queue)}")
            
            # 🛠️ Kiểm tra phím thoát [X] ngầm để không bị treo Pygame khi lỡ duyệt map quá rộng
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return {"status": "No Solution Found!", "path": None}
        if game.is_win(set(box)):
            end_time = time.time()
            execution_time = end_time - start_time
            
            return {
                "status": "Success",
                "path": path,                 # Trả về mảng các bước đi dạng ['U', 'D', 'L', 'R']
                "steps": len(path),           # Độ dài lời giải (Move Count)
                "nodes_generated": count,     # Tổng số nút thuật toán đã bóc tách khỏi Queue
                "time_seconds": execution_time # Thời gian chạy tính bằng giây
            }
        
        for d in [UP, DOWN, LEFT, RIGHT]:
            next_state = game.get_next_state(current_state, d)
            is_static_deadlock = False 
            
            if next_state:
                next_player_pos, next_boxes = next_state
                next_boxes_frozenset = frozenset(next_boxes)
                is_static_deadlock = False
                for box in next_boxes:
                    if box in simple_deadlock_map:  # Nếu simple_deadlock_map trả về set() các tọa độ chết
                        is_static_deadlock = True
                        break
                
                if is_static_deadlock:
                    continue  # Chặt nhánh tại đây,
                if game.is_freeze_deadlock(next_boxes_frozenset):
                    continue
                new_g = g + 1 # Chi phí thực tế tăng thêm 1
                
                # Nếu chưa đi qua hoặc tìm thấy đường đến state này ngắn hơn đường cũ
                if next_state not in visited or new_g < visited[next_state]: 
                    visited[next_state] = new_g
                    h = heuristic_manhattan(next_state, game.targets)
                    f = new_g + h
                    heapq.heappush(priority_queue, (f, new_g, next_state, path + [dir_names[d]]))
    print(f"❌ Thất bại! Đã duyệt hết {count} trạng thái nhưng không tìm thấy đường đi.")
    end_time = time.time()
    
    # 🛠️ 3. TRẢ VỀ DICTIONARY BÁO LỖI CHO MAIN.PY
    return {
        "status": "No Solution Found!",
        "path": None,
        "steps": 0,
        "nodes_generated": count,
        "time_seconds": end_time - start_time
    }


# if __name__ == "__main__":
#     # Hướng di chuyển tương ứng trong Sokoban
#     UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)

#     # Đường dẫn đến thư mục chứa các file map của bạn
#     maps_dir = 'data/maps'
#     map_files = glob.glob(os.path.join(maps_dir, '*.txt'))
    
#     if not map_files:
#         print(f"❌ Không tìm thấy file map (.txt) nào trong thư mục: {maps_dir}")
#         print("Vui lòng kiểm tra lại đường dẫn hoặc cấu trúc thư mục.")
#     else:
#         print(f"🔍 Tìm thấy {len(map_files)} file map để thử nghiệm.\n")
        
#         # Duyệt qua từng file map cụ thể
#         for file_path in sorted(map_files):
#             file_name = os.path.basename(file_path)
#             print("=" * 60)
#             print(f"📂 ĐANG XỬ LÝ MAP: {file_name}")
#             print("=" * 60)
            
#             try:
#                 # 1. Khởi tạo đối tượng game từ file map hiện tại
#                 # (Bạn hãy thay thế bằng class khởi tạo game thực tế của dự án bạn, ví dụ: SokobanGame(file_path))
#                 game = SokobanGame(file_path) 
                
#                 # 2. Trích xuất thông số map cơ bản để kiểm tra dữ liệu nạp vào
#                 walls_test = game.walls
#                 start_player_test, start_boxes_test = game.get_initial_state()
#                 boxes_test = frozenset(start_boxes_test)
                
#                 print(f"[Thông số xuất phát]: Player đứng tại {start_player_test}")
#                 print("-" * 50)
                
#                 # 2. CHẠY VÀ IN CHI TIẾT VÙNG ĐI BỘ (TEST 1)
#                 print("👉 [TEST 1/3] Quét và hiển thị CHI TIẾT vùng đi bộ:")
#                 reachable_dict = get_reachable_zone(start_player_test, boxes_test, walls_test)
                
#                 # Vòng lặp in tường tận cấu trúc Dictionary trả về
#                 print("  {")
#                 for o_den, chuoi_di in sorted(reachable_dict.items()):
#                     # Biểu diễn chuỗi rỗng trực quan hơn để dễ nhìn
#                     chuoi_hien_thi = '"" (Ô xuất phát)' if chuoi_di == "" else f'"{chuoi_di}"'
#                     print(f"     Tọa độ {o_den}: {chuoi_hien_thi},")
#                 print("  }")
#                 print(f"  => Tổng cộng Player có thể đi bộ tự do đến {len(reachable_dict)} ô trống.")
#                 print("-" * 50)
                
#                 # # 4. DEBUG PHẦN 2: Kiểm tra ô đại diện (Canonical)
#                 # print("👉 [TEST 2/3] Tìm ô đại diện chuẩn hóa...")
#                 all_positions = reachable_dict.keys()
#                 # canonical = get_canonical_player(all_positions)
#                 # print(f"  => Ô đại diện (Top-Left): {canonical}")
                
#                 # 5. DEBUG PHẦN 3: Kiểm tra các cú đẩy hộp khả thi đầu tiên
#                 print("👉 [TEST 3/3] Chi tiết các thông số cú đẩy hộp nước đầu:")
#                 pushes = list(get_all_pushes(all_positions, boxes_test, walls_test))
                
#                 print(f"  => AI tìm thấy {len(pushes)} cú đẩy hộp hợp lệ tại vị trí này.\n")
                
#                 # Bảng quy đổi vector hướng sang chữ tiếng Việt để dễ debug
#                 huong_tieng_viet = {UP: "LÊN (Up)", DOWN: "XUỐNG (Down)", LEFT: "SANG TRÁI (Left)", RIGHT: "SANG PHẢI (Right)"}
                
#                 for idx, push_item in enumerate(pushes, 1):
#                     # Bóc tách 4 thông số chuẩn từ tuple trả về
#                     box_pos, box_destination, direction, player_required = push_item
                    
#                     print(f"  [Cú đẩy #{idx}]:")
#                     print(f"    + 1. Vị trí hộp hiện tại (box_pos)         : {box_pos}")
#                     print(f"    + 2. Vị trí hộp sẽ đến (box_destination)  : {box_destination}")
#                     print(f"    + 3. Vector hướng đẩy (direction)         : {direction} -> Hành động: {huong_tieng_viet[direction]}")
#                     print(f"    + 4. Ô Player phải đứng để đẩy (player_req): {player_required}")
                    
#                     # Kiểm tra chéo độ chính xác của chuỗi đi bộ đến ô cần đứng này
#                     chuoi_di_bo = reachable_dict[player_required]
#                     chuoi_hien_thi = '"" (Đứng sẵn tại chỗ)' if chuoi_di_bo == "" else f'"{chuoi_di_bo}"'
#                     print(f"    ==> Chuỗi đi bộ của Player để mò đến ô đứng đẩy này là: {chuoi_hien_thi}")
#                     print("    " + "-" * 50)
                    
#                 print("-" * 50)
                
#                 # 6. GỌI AI GIẢI MAP NẾU CÁC BƯỚC KHỞI TẠO KHÔNG LỖI
#                 print(f"🚀 AI đang tìm đường giải map {file_name}...")
#                 solution = a_star_push_based(game)
                
#                 print("\n---------------- KẾT QUẢ GIẢI ----------------")
#                 if solution is not None:
#                     print(f"✅ GIẢI THÀNH CÔNG!")
#                     print(f"  - Tổng số bước di chuyển (Cả đi bộ + đẩy): {len(solution)} bước")
#                     print(f"  - Chuỗi đáp án hoàn chỉnh: {solution}")
#                 else:
#                     print(f"❌ THẤT BẠI: AI đã duyệt hết các nhánh nhưng map này KHÔNG CÓ NGHIỆM!")
#                 print("----------------------------------------------\n")
                
#             except MemoryError:
#                 print(f"🚨 LỖI: File {file_name} bị tràn bộ nhớ RAM (MemoryError)!")
#                 print("  => Vui lòng check lại file .txt xem tường bao quanh có bị hở lỗ nào không.\n")
#             except Exception as e:
#                 print(f"💥 LỖI HỆ THỐNG khi xử lý file {file_name}: {e}")
#                 print("  => Vui lòng kiểm tra lại cấu trúc class Game hoặc hàm khởi tạo.\n")
if __name__ == "__main__":
    # Hướng di chuyển tương ứng trong Sokoban
    UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)

    # Đường dẫn CHÍNH XÁC đến file map số 4 của bạn
    maps_dir = 'data/maps'
    file_path = os.path.join(maps_dir, 'level4.txt') # <-- Đổi 'level4.txt' thành tên file thực tế của bạn
    
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file map tại đường dẫn: {file_path}")
    else:
        file_name = os.path.basename(file_path)
        print("=" * 60)
        print(f"📂 ĐANG XỬ LÝ DUY NHẤT MAP: {file_name}")
        print("=" * 60)
        
        try:
            # 1. Khởi tạo đối tượng game từ file map
            game = SokobanGame(file_path)
            
            walls_test = game.walls
            start_player_test, start_boxes_test = game.get_initial_state()
            boxes_test = frozenset(start_boxes_test)
            
            print(f"[Thông số xuất phát]: Player đứng tại {start_player_test}")
            print("-" * 50)
            
            # 2. Lấy danh sách vùng đi bộ hiện tại để phục vụ test 3
            reachable_dict = get_reachable_zone(start_player_test, boxes_test, walls_test)
            all_positions = reachable_dict.keys()
            
            # 3. CHẠY VÀ IN CHI TIẾT CÁC CÚ ĐẨY KHẢ THI (TEST 3)
            print("👉 [TEST 3/3] Chi tiết các thông số cú đẩy hộp nước đầu:")
            pushes = list(get_all_pushes(all_positions, boxes_test, walls_test))
            
            print(f"  => AI tìm thấy {len(pushes)} cú đẩy hộp hợp lệ tại vị trí này.\n")
            huong_tieng_viet = {UP: "LÊN (Up)", DOWN: "XUỐNG (Down)", LEFT: "SANG TRÁI (Left)", RIGHT: "SANG PHẢI (Right)"}
            
            for idx, push_item in enumerate(pushes, 1):
                box_pos, box_destination, direction, player_required = push_item
                print(f"  [Cú đẩy #{idx}]:")
                print(f"    + 1. Vị trí hộp hiện tại (box_pos)         : {box_pos}")
                print(f"    + 2. Vị trí hộp sẽ đến (box_destination)  : {box_destination}")
                print(f"    + 3. Vector hướng đẩy (direction)         : {direction} -> Hành động: {huong_tieng_viet[direction]}")
                print(f"    + 4. Ô Player phải đứng để đẩy (player_req): {player_required}")
                
                chuoi_di_bo = reachable_dict[player_required]
                chuoi_hien_thi = '"" (Đứng sẵn tại chỗ)' if chuoi_di_bo == "" else f'"{chuoi_di_bo}"'
                print(f"    ==> Chuỗi đi bộ của Player để mò đến ô đứng đẩy này là: {chuoi_hien_thi}")
                print("    " + "-" * 50)
                
            print("-" * 50)
            
            # 4. TIẾN HÀNH GIẢI MAP
            print(f"🚀 AI đang chạy thuật toán A* để giải map {file_name}...")
            solution = a_star_push_based(game)
            
            print("\n---------------- KẾT QUẢ GIẢI ----------------")
            if solution is not None:
                if isinstance(solution, list):
                    solution_string = "".join(solution)
                else:
                    solution_string = str(solution)

                print(f"✅ GIẢI THÀNH CÔNG!")
                print(f"  - Chuỗi đáp án hoàn chỉnh: {solution_string}")
                print(f"  - Tổng số bước di chuyển (Cả đi bộ + đẩy): {len(solution_string)} bước")
            else:
                print(f"❌ THẤT BẠI: Map này không có đường giải!")
            print("----------------------------------------------\n")
            
        except Exception as e:
            print(f"💥 LỖI khi xử lý file {file_name}: {e}\n")
