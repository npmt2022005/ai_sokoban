from constants import *
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
    def is_inside(self, r, c):
        """Kiểm tra tọa độ (r, c) có nằm trong bản đồ không"""
        return 0 <= r < self.height and 0 <= c < self.width

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
        return self.targets == current_boxes
    def get_initial_state(self):
        return (self.player_pos, frozenset(self.boxes)) # frozenset({(1,2), (3,4)}) == frozenset({(3,4), (1,2)})
        
    def get_deadlock_location(self):
        deadlocks = set()
        for r in range(self.height):
            for c in range(self.width):
                if (r, c) in self.walls or (r, c) in self.targets:
                    continue
                has_top = (r - 1, c) in self.walls
                has_bottom = (r + 1, c) in self.walls
                has_left = (r, c - 1) in self.walls
                has_right = (r, c + 1) in self.walls

                if (has_top and has_left) or (has_top and has_right) or (has_bottom and has_left) or (has_bottom and has_right):
                    deadlocks.add((r, c))
        
        return deadlocks
    
    
    