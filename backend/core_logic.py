from constants import *
from collections import deque

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
        UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
        DIRECTIONS = [UP, DOWN, LEFT, RIGHT]


        visited_states = set()
        safe_boxes_squares = set()
        queue = deque()

        for goal in self.targets:
            safe_boxes_squares.add(goal)
            # Tại mỗi ô đích, giả định người có thể đứng ở cả 4 hướng xung quanh để bắt đầu kéo
            for dr, dc in DIRECTIONS:
                player_r = goal[0] + dr
                player_c = goal[1] + dc
                player_pos = (player_r, player_c)

                # Người chỉ được đứng ở ô trống, không được đứng vào tường
                if self.is_inside(player_r, player_c) and player_pos not in self.walls:
                    state = (goal, player_pos)
                    visited_states.add(state)
                    queue.append(state)
        
        # Bước B
        while queue:
            box , player = queue.popleft()

            # Thử kéo hộp lùi theo 4 hướng
            for dr, dc in DIRECTIONS:
                next_player = (player[0] - dr, player[1] - dc)
                # Hộp bị dịch chuyển: chiếm lấy ô người vừa đứng cũ
                next_box = player

                # ĐIỀU KIỆN KÉO HỢP LỆ: cả ô hộp mới và ô người mới đều phải là ô trống (không là tường)
                if (self.is_inside(next_box[0], next_box[1]) and next_box not in self.walls and
                self.is_inside(next_player[0], next_player[1]) and next_player not in self.walls):
                    
                    next_state = (box, next_player)

                    # Nếu trạng thái phối hợp này chưa từng được duyệt qua
                    if next_state not in visited_states:
                        visited_states.add(next_state)
                        safe_boxes_squares.add(next_box) # Khẳng định ô này Hộp có thể đến được -> AN TOÀN
                        queue.append(next_state)
        # BƯỚC C: Tìm phần bù (Lấy tất cả sàn nhà trừ đi các ô An toàn)

        dead_squares = set()
        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)
                # Nếu là ô trống nằm trong vùng chơi, không phải tường, không phải đích 
                # VÀ KHÔNG nằm trong danh sách an toàn -> ĐÍCH THỊ LÀ Ô CHẾT
                if (pos not in self.walls and 
                    pos not in self.targets and 
                    pos not in safe_boxes_squares):
                    dead_squares.add(pos)
        # ---- ĐOẠN CODE DEBUG NHANH ----
        print(f"[DEBUG] Kích thước map: {self.height}x{self.width}")
        print(f"[DEBUG] Số lượng ô tường: {len(self.walls)} - Kiểu dữ liệu mẫu: {type(list(self.walls)[0]) if self.walls else 'Rỗng'}")
        print(f"[DEBUG] Số lượng ô đích: {len(self.targets)}")
        print(f"[DEBUG] Số ô an toàn tìm được: {len(safe_boxes_squares)}")
        # -------------------------------
        return dead_squares

    def get_static_deadlock_location1(self):
        DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

        visited_states = set()
        safe_squares = set()
        queue = deque()

        # init từ goal
        for goal in self.targets:
            for dr, dc in DIRECTIONS:
                player = (goal[0] + dr, goal[1] + dc)

                if self.is_inside(*player) and player not in self.walls:
                    state = (goal, player)
                    visited_states.add(state)
                    queue.append(state)
                    safe_squares.add(goal)

        # BFS pull
        while queue:
            box, player = queue.popleft()

            for dr, dc in DIRECTIONS:
                prev_player = (player[0] - dr, player[1] - dc)
                prev_box = player

                if (self.is_inside(*prev_player) and prev_player not in self.walls and
                    self.is_inside(*prev_box) and prev_box not in self.walls):

                    next_state = (box, prev_player)

                    if next_state not in visited_states:
                        visited_states.add(next_state)
                        queue.append(next_state)
                        safe_squares.add(prev_box)

        # lấy dead squares
        dead_squares = set()
        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)
                if (pos not in self.walls and
                    pos not in self.targets and
                    pos not in safe_squares):
                    dead_squares.add(pos)

        return dead_squares
    def test_print_deadlocks(self,deadlocks):
        """
        Hàm in bản đồ trực quan bằng ký tự để test thuật toán.
        #: Tường, .: Ô đích, X: Ô chết, _: Ô trống an toàn
        """
        print("\n" + "="*10 + " BẢN ĐỒ PHÁT HIỆN GÓC/TƯỜNG CHẾT " + "="*10)
        for r in range(self.height):
            row_str = ""
            for c in range(self.width):
                pos = (r, c)
                if pos in self.walls:
                    row_str += "# "  # Tường
                elif pos in self.targets:
                    row_str += ". "  # Ô đích (Không bao giờ chết)
                elif pos in deadlocks:
                    row_str += "X "  # Ô chết phát hiện bởi thuật toán PULL
                else:
                    row_str += "_ "  # Ô trống an toàn (Dùng dấu gạch dưới cho dễ nhìn)
            print(row_str)
        print("=" * 52 + "\n")


    
    
    