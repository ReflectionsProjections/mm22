import unittest
from src.game.game import Game


class TestCharacter(unittest.TestCase):

    def test_constructor(self):
        """ Test default constructor
        """
        game = Game(500)

        self.assertEqual(game.totalTurns, 500)

    def test_add_player(self):
        player_json = {
            "teamName": "Test",
            "classes": [
                {"characterName": "character1",
                "classId": "dummy_one"},
                {"characterName": "character2",
                "classId": "dummy_two"},
                {"characterName": "character3",
                "classId": "dummy_one"},

            ]
        }

        game = Game(500)
        response = game.add_new_player(player_json)
        print(response)

        self.assertEqual(response[0], True)
        self.assertEqual(game.teams[0].name, player_json['teamName'])
        self.assertEqual(len(game.teams[0].characters), 3)