
class GameMap:

    def __init__(self, width=5, height=5, walls=[(1,1),(3,1),(1,3),(3,3)]):
        self.walls = walls
        self.width = width
        self.height = height

    def is_inbounds(self, pos):
        return pos[0] >= 0 and pos[0] < self.width and pos[1] >= 0 and pos[1] < self.height and pos not in self.walls

    def is_same_row(self, pos1, pos2):
        return pos1[1] == pos2[1]

    def is_same_col(self, pos1, pos2):
        return pos1[0] == pos2[0]

    @staticmethod
    def path_between(value1, value2):
        return [i for i in range(min(value1, value2), max(value1, value2) + 1)]

    def in_vision_of(self, pos1, pos2, max_length = None):
        # Same Position
        if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
            return True

        # Out of bounce
        if not self.is_inbounds(pos1) or not self.is_inbounds(pos2):
            return False

        if max_length is None:
            max_length = max(self.width, self.height)

        if self.is_same_col(pos1, pos2):
            for i in GameMap.path_between(pos1[1], pos2[1]):
                if not self.is_inbounds((pos1[0], i)) or i >= max_length:
                    return False
        elif self.is_same_row(pos1, pos2):
            for i in GameMap.path_between(pos1[0], pos2[0]):
                if not self.is_inbounds((i, pos1[1])) or i >= max_length:
                    return False
        return True

    def can_move_to(self, pos1, pos2, max_distance=None):
        if max_distance is None:
            max_distance = self.width*self.height

        path = self.bfs(pos1, pos2)

        return not (path is None or len(path) >= max_distance + 1)

    @staticmethod
    def get_adjacent_pos(pos):
        adjacent_pos = []
        for i in [-1, 1]:
            adjacent_pos.append((pos[0] + i, pos[1]))
            adjacent_pos.append((pos[0], pos[1] + i))

        return adjacent_pos


    def bfs(self, pos1, pos2):
        if not self.is_inbounds(pos1) or not self.is_inbounds(pos2):
            return None

        search_pathes = [[pos1]]
        searched_nodes = []

        new_path = search_pathes.pop()

        while new_path is not None:
            if new_path[-1] == pos2:
                return new_path

            for new_node in GameMap.get_adjacent_pos(new_path[-1]):
                if self.is_inbounds(new_node) and not new_node in searched_nodes:
                    temp = new_path.copy()
                    temp.append(new_node)
                    search_pathes.append(temp)
                    searched_nodes.append(new_node)
            new_path = search_pathes.pop()

        return None