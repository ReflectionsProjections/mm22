
class GameMap:

    def __init__(self, width=0, height=0, walls=[]):

        # List of line segements that define walls in the game
        self.walls = walls
        self.width = width
        self.height = height

    def is_inbounds(self, pos):
        return pos[0] > 0 and pos[0] < self.width and pos[1] > 0 and pos[1] < self.height

    def is_same_row(self, pos1, pos2):
        return pos1.y == pos2.y

    def is_same_col(self, pos1, pos2):
        return pos1.x == pos2.x

    def path_between(self, value1, value2):
        return [i for i in range(min(value1, value2), max(value1, value2))]

    def in_vision_of(self, pos1, pos2):
        if pos1 is pos2:
            return True
        if self.is_same_row(pos1, pos2):
            for i in self.path_between(pos1[1], pos2[1]):
                if (pos1[0], i) in self.walls:
                    return False
        if self.is_same_col(pos1, pos2):
            for i in self.path_between(pos1[0], pos2[0]):
                if (i, pos1[1]) in self.walls:
                    return False
        return True

    def can_move_to(self, pos1, pos2, max_distance=None):
        if max_distance is None:
            max_distance = self.width*self.height

    def get_adjacent_pos(self, pos):
        adjacent_pos = []
        for i in [-1, 1]:
            adjacent_pos.append((pos[0] + i, pos[1]))
            adjacent_pos.append((pos[0], pos[1] + i))


    def bfs(self, pos1, pos2):
        search_pathes = []
        searched_nodes = []

        for new_node in self.get_adjacent_pos(pos1):
            search_pathes.append([new_node])
        new_path = search_pathes.pop()

        while new_path is not None:
            if new_path[-1] == pos2:
                return new_path

            for new_node in self.get_adjacent_pos(new_path[-1]):
                continue #TODO