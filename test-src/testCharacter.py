import unittest
from src.game.character import Character


class TestCharacter(unittest.TestCase):

    def testDefaultConstructor(self):
        """ Test default constructor
        """
        char = Character(0)

        self.assertEqual(char.id, 0)
        self.assertEqual(char.name, "AI")
        self.assertEqual(char.classId, "warrior")
        self.assertEqual(char.id, 0)

    def test