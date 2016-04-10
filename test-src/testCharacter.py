import unittest
from src.game.character import Character


class TestCharacter(unittest.TestCase):

    def test_constructor(self):
        """ Test default constructor
        """
        char = Character(0, name="AI", classId="dummy_one")

        self.assertEqual(char.id, 0)
        self.assertEqual(char.name, "AI")
        self.assertEqual(char.classId, "dummy_one")
        self.assertEqual(char.abilities, {0: 0.0, 5: 0.0})

    def test_attribute_setup(self):
        char = Character(0)

        self.assertEqual(char.attributes.maxHealth, 500)
        self.assertEqual(char.attributes.health, 500)
        self.assertEqual(char.attributes.damage, 100)
        self.assertEqual(char.attributes.attackRange, 0)
        self.assertEqual(char.attributes.attackSpeed, 5)
        self.assertEqual(char.attributes.armor, 50)
        self.assertEqual(char.attributes.movementSpeed, 5)
        self.assertEqual(char.attributes.stunned, 0)
        self.assertEqual(char.attributes.silenced, 0)

    def test_can_use_ability(self):
        char = Character(0)

        # Test ability that has 0 cooldown
        self.assertEqual(char.can_use_ability(1), True)

        # Test ability that has a cooldown
        char.abilities[1] = 1.0
        self.assertEqual(char.can_use_ability(1), False)

        # Test ability that doesn't exist or doesn't have
        self.assertEqual(char.can_use_ability(-1), False)
        self.assertEqual(char.can_use_ability(99), False)

    def test_can_move(self):
        char = Character(0)

        self.assertEqual(char.can_move(), True)

        char.apply_stat_change({'attribute': 'Rooted', 'change': -1})

        self.assertEqual(char.can_move(), False)

        char.apply_stat_change({'attribute': 'Rooted', 'change': 1})

        self.assertEqual(char.can_move(), True)

        char.apply_stat_change({'attribute': 'Stunned', 'change': -1})

        self.assertEqual(char.can_move(), False)

    def test_use_ability(self):
        char1 = Character(0)
        char2 = Character(1)