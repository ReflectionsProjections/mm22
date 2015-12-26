import gameConstants

class Character:

    numCharacters = 0

    def __init__(classKey):
        """ Init a character class based on class key defined in game consts
        :param classKey: (string) class key
        """

        #Game related attributes
        self.positionX = 0.0
        self.positionY = 0.0
        self.characterId = numCharacters
        numCharacters += 1

        #Crowd controls
        self.stunned = False
        self.silenced = False


        classJson = gameConstants.classesJson[classKey]

        self.attributes = Attributes( classJson['Health'],
                            classJson['Damage'],
                            classJson['AbilityDamage'],
                            classJson['AttackRange'],
                            classJson['Armor'],
                            classJson['movementSpeed'])

        self.abilities = {}
        for ability in classJson['Abilities']:
            self.abilities[ability] = 0.0

        self.buffs = []
        self.debuffs = []

    def toJson():
        """ Returns information about character as a json
        """

        #TODO finish

        json = {}
        json['x'] = self.positionX
        json['y'] = self.positionY
        json['attributes'] = self.attributes.toJson()

        return json


class Attributes:

    def __init_(health, damage, abilityDamage, attackRange, armor, movementSpeed):
        """ Init attributes for a character
        :param health: (float) health
        :param damage: (float) damage per tick
        :param attackRange: (int) attackRange of auto attack
        :param armor: (float) damage removed from attacks
        :param movementSpeed: (int) movement per tick
        """

        self.health = health
        self.damage = damage
        self.abilityDamage = abilityDamage
        self.attackRange = attackRange
        self.armor = armor
        self.movementSpeed = movementSpeed

    def toJson():
        """ Return json of information containing all attribute information
        """

        json = {}
        json['Health'] = self.health
        json['Damage'] = self.damage
        json['AbilitiyDamage'] = self.abilityDamage
        json['AttackRange'] = self.attackRange
        json['Armor'] = self.armor
        json['MovementSpeed'] = self.movementSpeed

        return json
