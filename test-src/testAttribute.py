import unittest
import src.game.gameConstants as gameConstants
from src.game.character import Attributes


class TestCharacter(unittest.TestCase):

    def test_constructor(self):
        """ Test default constructor
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.maxHealth, 500)
        self.assertEqual(attributes.health, 500)
        self.assertEqual(attributes.attackRange, 0)
        self.assertEqual(attributes.attackSpeed, 5)
        self.assertEqual(attributes.armor, 50)
        self.assertEqual(attributes.movementSpeed, 5)
        self.assertEqual(attributes.stunned, 0)
        self.assertEqual(attributes.silenced, 0)
        self.assertEqual(attributes.rooted, 0)

    def test_change_attribute_health(self):
        """ Test that changing health works as intended
        - Can not be below 0
        - Can not be above maxHealth
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.health, 500)
        attributes.change_attribute("Health", -510)
        self.assertEqual(attributes.health, 0)
        attributes.change_attribute("Health", 600)
        self.assertEqual(attributes.health, 500)
        attributes.change_attribute("Health", -50)
        self.assertEqual(attributes.health, 450)

    def test_change_attribute_damage(self):
        """ Test that changing damage has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.damage, 100)
        attributes.change_attribute("Damage", -110)
        self.assertEqual(attributes.damage, -10)
        attributes.change_attribute("Damage", 20)
        self.assertEqual(attributes.damage, 10)

    def test_change_attribute_attackRange(self):
        """ Test that changing attackRange has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.attackRange, 0)
        attributes.change_attribute("AttackRange", -10)
        self.assertEqual(attributes.attackRange, -10)
        attributes.change_attribute("AttackRange", 20)
        self.assertEqual(attributes.attackRange, 10)

    def test_change_attribute_attackSpeed(self):
        """ Test that changing attackSpeed has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.attackSpeed, 5)
        attributes.change_attribute("AttackSpeed", -15)
        self.assertEqual(attributes.attackSpeed, -10)
        attributes.change_attribute("AttackSpeed", 20)
        self.assertEqual(attributes.attackSpeed, 10)

    def test_change_attribute_armor(self):
        """  Test that changing armor has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.armor, 50)
        attributes.change_attribute("Armor", -60)
        self.assertEqual(attributes.armor, -10)
        attributes.change_attribute("Armor", 20)
        self.assertEqual(attributes.armor, 10)

    def test_change_attribute_movementSpeed(self):
        """  Test that changing movementSpeed has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.movementSpeed, 5)
        attributes.change_attribute("MovementSpeed", -15)
        self.assertEqual(attributes.movementSpeed, -10)
        attributes.change_attribute("MovementSpeed", 20)
        self.assertEqual(attributes.movementSpeed, 10)

    def test_change_attribute_stunned(self):
        """  Test that changing stunned has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.stunned, 0)
        attributes.change_attribute("Stunned", -1)
        self.assertEqual(attributes.stunned, -1)
        attributes.change_attribute("Stunned", 2)
        self.assertEqual(attributes.stunned, 1)

    def test_change_attribute_silenced(self):
        """  Test that changing silenced has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.silenced, 0)
        attributes.change_attribute("Silenced", -1)
        self.assertEqual(attributes.silenced, -1)
        attributes.change_attribute("Silenced", 2)
        self.assertEqual(attributes.silenced, 1)

    def test_change_attribute_rooted(self):
        """  Test that changing rooted has no restrictions
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.rooted, 0)
        attributes.change_attribute("Rooted", -1)
        self.assertEqual(attributes.rooted, -1)
        attributes.change_attribute("Rooted", 2)
        self.assertEqual(attributes.rooted, 1)

    # Tests for get_attribute
    def test_get_attribute_health(self):
        """ Test that getting health works as intended
        - min: 0
        - max: Maxhealth
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Health"), 500)
        attributes.change_attribute("Health", -510)
        self.assertEqual(attributes.get_attribute("Health"), 0)
        attributes.change_attribute("Health", 600)
        self.assertEqual(attributes.get_attribute("Health"), 500)
        attributes.change_attribute("Health", -50)
        self.assertEqual(attributes.get_attribute("Health"), 450)


    def test_get_attribute_damage(self):
        """ Test that getting damage works as intended
        - min: 0
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Damage"), 100)
        attributes.change_attribute("Damage", -110)
        self.assertEqual(attributes.get_attribute("Damage"), 0)
        attributes.change_attribute("Damage", 20)
        self.assertEqual(attributes.get_attribute("Damage"), 10)

    def test_get_attribute_attackRange(self):
        """ Test that getting attackRange works as intended
        - min: 0
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("AttackRange"), 0)
        attributes.change_attribute("AttackRange", -10)
        self.assertEqual(attributes.get_attribute("AttackRange"), 0)
        attributes.change_attribute("AttackRange", 20)
        self.assertEqual(attributes.get_attribute("AttackRange"), 10)

    def test_get_attribute_attackSpeed(self):
        """ Test that getting attackSpeed works as intended
        - min: 0
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("AttackSpeed"), 5)
        attributes.change_attribute("AttackSpeed", -15)
        self.assertEqual(attributes.get_attribute("AttackSpeed"), 1)
        attributes.change_attribute("AttackSpeed", 20)
        self.assertEqual(attributes.get_attribute("AttackSpeed"), 10)

    def test_get_attribute_armor(self):
        """ Test that getting armor works as intended
        - min: 0
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Armor"), 50)
        attributes.change_attribute("Armor", -60)
        self.assertEqual(attributes.get_attribute("Armor"), 0)
        attributes.change_attribute("Armor", 20)
        self.assertEqual(attributes.get_attribute("Armor"), 10)

    def test_get_attribute_movementSpeed(self):
        """ Test that getting movementSpeed works as intended
        - min: 0
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("MovementSpeed"), 5)
        attributes.change_attribute("MovementSpeed", -15)
        self.assertEqual(attributes.get_attribute("MovementSpeed"), 0)
        attributes.change_attribute("MovementSpeed", 20)
        self.assertEqual(attributes.get_attribute("MovementSpeed"), 10)

    def test_get_attribute_stunned(self):
        """ Test that getting if stunned works as intended
        - below 0: True
        - else: False
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Stunned"), False)
        attributes.change_attribute("Stunned", -1)
        self.assertEqual(attributes.get_attribute("Stunned"), True)
        attributes.change_attribute("Stunned", 2)
        self.assertEqual(attributes.get_attribute("Stunned"), False)

    def test_get_attribute_silenced(self):
        """ Test that getting if silenced works as intended
        - below 0: True
        - else: False
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Silenced"), False)
        attributes.change_attribute("Silenced", -1)
        self.assertEqual(attributes.get_attribute("Silenced"), True)
        attributes.change_attribute("Silenced", 2)
        self.assertEqual(attributes.get_attribute("Silenced"), False)

    def test_get_attribute_rooted(self):
        """ Test that getting if rooted works as intended
        - below 0: True
        - else: False
        :return None:
        """
        class_json = gameConstants.classesJson['dummy_one']

        attributes = Attributes(class_json['Health'],
                                class_json['Damage'],
                                class_json['AttackRange'],
                                class_json['AttackSpeed'],
                                class_json['Armor'],
                                class_json['MovementSpeed'])

        self.assertEqual(attributes.get_attribute("Rooted"), False)
        attributes.change_attribute("Rooted", -1)
        self.assertEqual(attributes.get_attribute("Rooted"), True)
        attributes.change_attribute("Rooted", 2)
        self.assertEqual(attributes.get_attribute("Rooted"), False)