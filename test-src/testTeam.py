import unittest
from src.game.team import Team


class TestCharacter(unittest.TestCase):

    def test_constructor(self):
        """ Test default constructor
        """
        character_json = {"characterName": "Player1", "classId": "warrior"}
        team1 = Team("Team1")

        self.assertTrue(team1.add_character(character_json))
        self.assertEqual(team1.size(), 1)