import unittest
from src.game.gamemap import GameMap


class TestGameMap(unittest.TestCase):

    def test_constructor(self):
        """ Test default constructor
        """
        game_map = GameMap()

        self.assertEqual(game_map.width, 5)
        self.assertEqual(game_map.height, 5)
        self.assertEqual(game_map.walls, [(1,1),(3,1),(1,3),(3,3)])

    def test_is_inbounds(self):
        game_map = GameMap()

        for x in range(game_map.width):
            for y in range(game_map.height):
                if not (x, y) in game_map.walls:
                    self.assertTrue(game_map.is_inbounds((x, y)))

        self.assertFalse(game_map.is_inbounds((-1, 0)))
        self.assertFalse(game_map.is_inbounds((0, -1)))
        self.assertFalse(game_map.is_inbounds((game_map.width + 1, 0)))
        self.assertFalse(game_map.is_inbounds((0, game_map.height + 1)))

    def test_is_same_row(self):
        game_map = GameMap()

        self.assertTrue(game_map.is_same_row((0, 0), (5, 0)))
        self.assertFalse(game_map.is_same_row((0, 0), (5, 1)))
        self.assertFalse(game_map.is_same_row((0, 0), (0, 1)))

    def test_is_same_row(self):
        game_map = GameMap()

        self.assertTrue(game_map.is_same_col((0, 0), (0, 5)))
        self.assertFalse(game_map.is_same_col((0, 0), (5, 1)))
        self.assertFalse(game_map.is_same_col((0, 0), (1, 0)))

    def test_path_between(self):
        self.assertEqual(GameMap.path_between(0, 2), [0,1,2])
        self.assertEqual(GameMap.path_between(5, 2), [2,3,4,5])

    def test_in_vision_of(self):
        game_map = GameMap()

        # Same node
        self.assertTrue(game_map.in_vision_of((0, 0), (0, 0)))
        # Out of bounce
        self.assertFalse(game_map.in_vision_of((5, 0), (0, 0)))
        self.assertFalse(game_map.in_vision_of((0, 0), (0, 5)))
        # Main code
        self.assertTrue(game_map.in_vision_of((0, 0), (0, 4)))
        self.assertTrue(game_map.in_vision_of((0, 0), (4, 0)))
        # Walls
        self.assertFalse(game_map.in_vision_of((1, 0), (1, 3)))
        self.assertFalse(game_map.in_vision_of((0, 1), (3, 1)))
        # Not enough sight
        self.assertFalse(game_map.in_vision_of((0, 0), (5, 0), 3))

    def test_can_move_to(self):
        game_map = GameMap()

        self.assertTrue(game_map.can_move_to((0,0), (0,1)))
        self.assertFalse(game_map.can_move_to((0,0), (2,2), 2))
        self.assertFalse(game_map.can_move_to((0,0), (1,1)))

    def test_get_adjacent_pos(self):
        self.assertEqual(GameMap.get_adjacent_pos((0,0)), [(-1,0),(0,-1),(1,0),(0,1)])

    def test_bfs(self):
        game_map = GameMap()

        print(game_map.bfs((0,0), (0,1)))
        self.assertEqual(game_map.bfs((0,0), (0,1)), [(0,0),(0,1)])