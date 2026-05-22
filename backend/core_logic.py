from constants import *
from collections import deque
import os, glob
class SokobanGame :
    def __init__(self, map_path):
        self.map_path = map_path
        self.walls = set()
        self.targets = set()
        self.boxes = set()
        self.player_pos = None
        self.width = 0;
        self.height =0;
        self.load_map()
        self.simple_deadlocks = self.get_static_deadlock_location1()
        self.history = [] # Ngăn xếp lưu lịch sử [(pos, boxes), ...]
    

    def load_map(self):
        # QUAN TRỌNG: Xóa dữ liệu cũ trước khi nạp lại
        self.walls = set()
        self.targets = set()
        self.boxes = set()
        self.player_pos = None


        with open(self.map_path, "r") as f:
            lines = f.read().splitlines()
        
        self.height = len(lines)
        if self.height > 0:
            self.width = max(len(line) for line in lines)

        for r, line in enumerate(lines):
            for c, char in enumerate(line):
                pos = (r, c)
                if char == WALL:
                    self.walls.add(pos)
                elif char == TARGET:
                    self.targets.add(pos)
                elif char == BOX:
                    self.boxes.add(pos)
                elif char == PLAYER:
                    self.player_pos = pos
                elif char == BOX_ON_TARGET:
                    self.boxes.add(pos)
                    self.targets.add(pos)
                elif char == PLAYER_ON_TARGET:
                    self.player_pos = pos
                    self.targets.add(pos)
    def get_display_data(self):
        return {
            "width": self.width,
            "height": self.height,
            "walls": self.walls,      # set các tọa độ (r, c)
            "targets": self.targets,  # set các tọa độ (r, c)
            "boxes": self.boxes,      # set các tọa độ (r, c)
            "player": self.player_pos # tọa độ (r, c)
        }
    def get_current_state(self):
        return (self.player_pos, frozenset(self.boxes))
    def move(self, direction):
        # Trước khi thay đổi dữ liệu, hãy lưu trạng thái cũ vào history
        old_state = self.get_current_state()
        dr, dc = direction
        curr_r, curr_c = self.player_pos
        new_r, new_c = curr_r + dr, curr_c + dc
        new_pos = (new_r, new_c)
        # Chặn đi ra khỏi màn hình
        if not self.is_inside(new_r, new_c):
            return False
        # Kiem tra neu cham tuong
        if new_pos in self.walls:
            return False
        
        # 2. Kiểm tra nếu gặp hộp
        if new_pos in self.boxes:
            # Tính toán vị trí mới của hộp nếu bị đẩy
            box_new_r, box_new_c = new_r + dr, new_c + dc
            box_new_pos = (box_new_r, box_new_c)
            if not self.is_inside(box_new_r, box_new_c):
                return False 
                        
            # Hộp có thể đẩy nếu vị trí mới không phải tường và không có hộp khác
            if box_new_pos not in self.walls and box_new_pos not in self.boxes:
                # Cập nhật vị trí hộp
                self.history.append(self.get_current_state())
                self.boxes.remove(new_pos)
                self.boxes.add(box_new_pos)
                # Cập nhật vị trí người
                self.player_pos = new_pos
                return True
            else:
                # Không đẩy được hộp (vướng tường hoặc hộp khác)
                return False
        # 3. Nếu là ô trống hoặc ô đích (không có tường/hộp)
        self.history.append(self.get_current_state())
        self.player_pos = new_pos
        return True
    def reset(self):
        self.history = []
        self.load_map()
    def undo(self):
        """Quay lại trạng thái trước đó"""
        if self.history:
            prev_player_pos, prev_boxes = self.history.pop()
            self.player_pos = prev_player_pos
            self.boxes = set(prev_boxes) # Chuyển từ frozenset về set để có thể modify tiếp
            return True
        return False
    


    def get_next_state(self, state, direction):
        player_pos, boxes = state
        dr, dc = direction
        new_r, new_c = player_pos[0] + dr, player_pos[1] + dc
        new_pos = (new_r, new_c)

        if not self.is_inside(new_r, new_c) or new_pos in self.walls:
            return None

        new_boxes = set(boxes)
        if new_pos in boxes:
            box_new_r, box_new_c = new_r + dr, new_c + dc
            box_new_pos = (box_new_r, box_new_c)

            if (not self.is_inside(box_new_r, box_new_c) or 
                box_new_pos in self.walls or 
                box_new_pos in boxes):
                return None
            
            new_boxes.remove(new_pos)
            new_boxes.add(box_new_pos)

        return (new_pos, frozenset(new_boxes))
    def is_wall(self, pos):
        """
        Kiểm tra xem tọa độ pos = (x, y) có phải là tường không.
        """
        return pos in self.walls
    def is_win(self, current_boxes):
        # Đảm bảo targets là một set để dùng được issubset
        targets_set = set(self.targets)
        
        # Kiểm tra xem TẤT CẢ các ô đích đã có hộp đè lên chưa
        # (Nghĩa là targets phải là tập con của current_boxes)
        return targets_set.issubset(set(current_boxes))
    def get_initial_state(self):
        return (self.player_pos, frozenset(self.boxes)) # frozenset({(1,2), (3,4)}) == frozenset({(3,4), (1,2)})
    
    def is_inside(self, r, c):
        """Kiểm tra tọa độ (r, c) có nằm trong bản đồ không"""
        return 0 <= r < self.height and 0 <= c < self.width
    def get_static_deadlock_location(self):
        """
        Tìm tất cả ô dead square bằng reverse BFS từ các target.
        
        Ý tưởng: một ô là SAFE nếu tồn tại ít nhất 1 cách đẩy hộp
        từ ô đó về target. Ngược lại là dead square.
        
        Reverse BFS: thay vì đẩy hộp đi, ta kéo hộp về.
        Để "kéo" hộp từ box → prev_box theo hướng (dr, dc):
            - prev_box = box + (dr, dc)      ← hộp lùi 1 bước
            - push_pos = box - (dr, dc)      ← player đứng phía đối diện
            Điều kiện hợp lệ:
            1. prev_box trong bản đồ, không phải tường
            2. push_pos trong bản đồ, không phải tường
            3. player có thể đến push_pos (không bị chặn hoàn toàn)
        """
        UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
        DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

        def in_bounds(r, c):
            return 0 <= r < self.height and 0 <= c < self.width

        # ── STEP 1: Reverse BFS từ tất cả target ────────────────────────────
        safe_boxes = set(self.targets)
        queue = deque(self.targets)
        visited_boxes = set(self.targets)  # đổi tên rõ hơn

        while queue:
            box = queue.popleft()

            for dr, dc in DIRECTIONS:
                # Để kéo hộp từ prev_box về box theo hướng (dr,dc):
                prev_box = (box[0] + dr,      box[1] + dc)   # hộp lùi
                push_pos = (box[0] - dr,      box[1] - dc)   # player đứng đây

                # Điều kiện 1: tọa độ hợp lệ
                if not in_bounds(*prev_box) or not in_bounds(*push_pos):
                    continue

                # Điều kiện 2: không phải tường
                if prev_box in self.walls or push_pos in self.walls:
                    continue

                # Điều kiện 3: chưa thăm
                if prev_box in visited_boxes:
                    continue

                visited_boxes.add(prev_box)
                safe_boxes.add(prev_box)
                queue.append(prev_box)

        # ── STEP 2: Tìm dead squares ─────────────────────────────────────────
        dead_squares = set()
        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)
                if pos in self.walls or pos in self.targets:
                    continue
                if pos not in safe_boxes:
                    dead_squares.add(pos)

        return dead_squares
    def get_static_deadlock_location1(self):
        UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
        DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

        def in_bounds(r, c):
            return 0 <= r < self.height and 0 <= c < self.width

        def player_reachable(start, box):
            """Flood fill cho player tránh walls + box"""
            q = deque([start])
            visited = {start}

            while q:
                r, c = q.popleft()
                for dr, dc in DIRECTIONS:
                    nr, nc = r + dr, c + dc
                    if (in_bounds(nr, nc)
                        and (nr, nc) not in self.walls
                        and (nr, nc) != box
                        and (nr, nc) not in visited):
                        visited.add((nr, nc))
                        q.append((nr, nc))
            return visited

        # ===== STEP 1: reverse BFS từ goal (box-only state) =====
        safe_boxes = set(self.targets)
        queue = deque(self.targets)
        visited = set(self.targets)

        while queue:
            box = queue.popleft()

            for dr, dc in DIRECTIONS:
                prev_box = (box[0] + dr, box[1] + dc)
                push_pos = (box[0] + 2 * dr, box[1] + 2 * dc)

                if not in_bounds(*prev_box) or not in_bounds(*push_pos):
                    continue

                if prev_box in self.walls or push_pos in self.walls:
                    continue

                if prev_box in visited:
                    continue

                visited.add(prev_box)
                safe_boxes.add(prev_box)
                queue.append(prev_box)

        # ===== STEP 2: tìm dead squares =====
        dead_squares = set()

        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)

                if pos in self.walls or pos in self.targets:
                    continue

                if pos not in safe_boxes:
                    dead_squares.add(pos)
        # ---- ĐOẠN CODE DEBUG ----
        print(f"[DEBUG] Kích thước map: {self.height}x{self.width}")
        print(f"[DEBUG] Số lượng ô tường: {len(self.walls)}")
        print(f"[DEBUG] Số lượng ô đích: {len(self.targets)}")
        print(f"[DEBUG] Số ô an toàn tìm được: {len(safe_boxes)}")
        return dead_squares

    # ---------------------------------DEADLOCK ver CLAUDE --------------------------------
    def _is_blocked_on_axis(
        self,
        box_pos: tuple,
        boxes: frozenset,
        visited: set,
        check_horiz: bool,
    ) -> bool:
        """
        Kiểm tra đệ quy hộp tại box_pos có bị chặn theo trục đã chọn không.

        Quy tắc (áp dụng cho cả 2 trục, chỉ khác hướng):
        1. Có tường ở một trong hai phía → bị chặn
        2. Cả hai phía đều là simple deadlock → bị chặn  (dùng walls để xấp xỉ)
        3. Có hộp lân cận → đệ quy trên trục NGƯỢC LẠI

        Tránh vòng lặp: key (pos, axis) đã thăm → coi như tường (trả về True).
        """
        key = (box_pos, check_horiz)
        if key in visited:
            return True  # đã thăm → coi như tường, phá vòng lặp
        visited.add(key)

        r, c = box_pos

        if check_horiz: # truc ngang 
            left,  right  = (r, c - 1), (r, c + 1)
            side_a, side_b = left, right
        else:
            up,down   = (r - 1, c), (r + 1, c)
            side_a, side_b = up, down

        # Quy tắc 1: tường một phía
        if self._is_wall_or_outside(side_a) or self._is_wall_or_outside(side_b):
            return True

        # Quy tắc 2: cả 2 phía đều là simple deadlock
        if self._is_simple_deadlock(side_a) and self._is_simple_deadlock(side_b):
            return True

        # Quy tắc 3: hộp lân cận → đệ quy đổi trục
        for side in (side_a, side_b):
            if side in boxes:
                if self._is_blocked_on_axis(side, boxes, visited, not check_horiz):
                    return True

        return False
 
    def _is_wall_or_outside(self, pos: tuple) -> bool: #Trả về true nếu là tường hoặc nằm ngoài 
        r, c = pos
        return not self.is_inside(r, c) or pos in self.walls

    def _is_simple_deadlock(self, pos: tuple) -> bool:
        # if self._is_wall_or_outside(pos):
        #     return True
        return pos in self.simple_deadlocks
    def is_frozen(self, box_pos: tuple, boxes: frozenset) -> bool:
        """Hộp bị đóng băng khi bị chặn cả 2 trục."""
        blocked_h = self._is_blocked_on_axis(box_pos, boxes, set(), check_horiz=True)
        blocked_v = self._is_blocked_on_axis(box_pos, boxes, set(), check_horiz=False)
        return blocked_h and blocked_v
 
    def get_frozen_boxes(self, boxes: frozenset) -> list:
        """Trả về danh sách hộp bị đóng băng mà không nằm trên target."""
        return [
            pos for pos in boxes
            if pos not in self.targets and self.is_frozen(pos, boxes)
        ]
 
    def is_freeze_deadlock(self, boxes: frozenset | None = None) -> bool:
        """
        Kiểm tra trạng thái hiện tại (hoặc boxes truyền vào) có là freeze deadlock không.
        Dùng sau mỗi nước đi để phát hiện sớm.
        """
        if boxes is None:
            boxes = frozenset(self.boxes)
        return len(self.get_frozen_boxes(boxes)) > 0

    
    def print_deadlock_map(self, dead_squares):
        """ In bản đồ kết quả trực quan: Ô chết sẽ được đánh dấu bằng chữ 'X' """
        for r in range(self.height):
            row_str = ""
            for c in range(self.width):
                pos = (r, c)
                if pos in self.walls:
                    row_str += "#"
                elif pos in self.targets:
                    row_str += "."
                elif pos in dead_squares:
                    row_str += "X"  # Vùng bế tắc tĩnh
                else:
                    row_str += " "  # Vùng di chuyển an toàn
            print(row_str)
# Test deadlock static 
# if __name__ == "__main__":
#     # Đường dẫn đến thư mục chứa các file map của bạn
#     # Sẽ quét tất cả các file có đuôi .txt trong thư mục data/maps/
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
#             print("=" * 50)
#             print(f"📂 ĐANG XỬ LÝ MAP: {file_name}")
#             print("=" * 50)
            
#             try:
#                 # Khởi tạo game với file map hiện tại
#                 game = SokobanGame(file_path)
                
#                 # Tính toán các ô bế tắc tĩnh bằng thuật toán Reverse-Pull
#                 deadlocks = game.get_static_deadlock_location()
                
#                 print("\n--- KẾT QUẢ PHÂN TÍCH (X là ô bế tắc tĩnh) ---")
#                 game.print_deadlock_map(deadlocks)
#                 print("\n" + "•" * 50 + "\n") # Dấu phân cách giữa các map
                
#             except Exception as e:
#                 print(f"❌ Có lỗi xảy ra khi xử lý file {file_name}: {e}")
#                 print("Hãy đảm bảo cấu trúc khởi tạo SokobanGame(file_path) hoạt động chính xác.")


def load_map_from_file(file_path):
    walls = set()
    boxes = set()
    targets = set()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for r, line in enumerate(lines):
        for c, char in enumerate(line.strip()):
            if char == '#':
                walls.add((r, c))
            elif char == '$':
                boxes.add((r, c))
            elif char == '.':
                targets.add((r, c))
            elif char == '*': # Hộp nằm sẵn trên đích
                boxes.add((r, c))
                targets.add((r, c))
                
    return boxes, walls, targets


#tesst freeze _ dealock
# if __name__ == "__main__":
#     # Đường dẫn đến thư mục chứa các file map của bạn
#     # Sẽ quét tất cả các file có đuôi .txt trong thư mục data/maps/
#     maps_dir = 'data/map_test'
#     map_files = glob.glob(os.path.join(maps_dir, '*.txt'))
#     for file_path in sorted(map_files):
#         file_name = os.path.basename(file_path)
#         print("=" * 50)
#         print(f"📂 ĐANG XỬ LÝ MAP: {file_name}")
#         print("=" * 50)
#         try:
#             # 1. Khởi tạo game với file map hiện tại
#             game = SokobanGame(file_path)
            
#             # Lấy tập hợp các hộp hiện tại từ game
#             current_boxes = frozenset(game.boxes)
            
#             print(f"📊 Thống kê sơ bộ map:")
#             print(f"   - Số lượng tường: {len(game.walls)}")
#             print(f"   - Số lượng hộp: {len(current_boxes)}")
#             print(f"   - Số lượng ô đích (target): {len(game.targets)}")
#             print(f"   - Số lượng bẫy tĩnh (simple deadlock): {len(game.simple_deadlocks)}")
#             print("-" * 30)

#             # 2. KIỂM THỬ 1: Kiểm tra trạng thái ban đầu của map
#             # Thường một map hợp lệ khi bắt đầu game sẽ KHÔNG được có freeze deadlock
#             initial_deadlock = game.is_freeze_deadlock(current_boxes)
#             print(f"❓ Trạng thái ban đầu có bị Freeze Deadlock không? -> {initial_deadlock}")
            
#             if initial_deadlock:
#                 # Nếu map vừa vào đã kẹt, ta tìm xem hộp nào đang bị đóng băng
#                 frozen_list = game.get_frozen_boxes(current_boxes)
#                 print(f"   ⚠️ Phát hiện các hộp bị kẹt ngay từ đầu tại: {frozen_list}")
#             else:
#                 print(f"   ✅ Trạng thái ban đầu sạch, không có hộp nào bị đóng băng.")

#             # 3. KIỂM THỬ 2 (Giả lập bẫy): Thử nghiệm độ nhạy của thuật toán
#             # Chúng ta sẽ tìm một ô thuộc diện bẫy tĩnh (simple_deadlocks) không chứa target, 
#             # cố tình nhét một chiếc hộp giả lập vào đó xem thuật toán có bắt được lỗi không.
#             test_trap_positions = [pos for pos in game.simple_deadlocks if pos not in game.targets]
            
#             if test_trap_positions:
#                 trap_pos = test_trap_positions[0] # Lấy thử một ô góc chết
                
#                 # Giả lập một tập hợp hộp mới: giữ nguyên các hộp cũ và nhét thêm 1 hộp vào góc chết
#                 simulated_boxes = frozenset(list(current_boxes) + [trap_pos])
                
#                 # Chạy kiểm tra đóng băng trên tập hộp giả lập này
#                 is_trap_detected = game.is_freeze_deadlock(simulated_boxes)
                
#                 print(f"🧪 Kiểm thử giả lập: Đặt thêm 1 hộp vào ô kẹt {trap_pos}")
#                 if is_trap_detected:
#                     print(f"   🎉 Thành công! Thuật toán đã phát hiện chính xác Freeze Deadlock (True).")
#                 else:
#                     print(f"   ❌ Thất bại! Thuật toán bỏ sót bẫy, báo không kẹt (False). Cần xem lại logic.")
#             else:
#                 print(f"🧪 Kiểm thử giả lập: Map này không có ô góc chết trống nào để thử nghiệm.")

#         except Exception as e:
#             print(f"❌ Có lỗi xảy ra khi xử lý file {file_name}: {e}")
#             import traceback
#             traceback.print_exc() # In chi tiết dòng lỗi nếu có sập code đệ quy
            
            