import gameConstants


class Character(object):

    def __init__(self, charId, name="AI", classId=0):
        """ Init a character class based on class key defined in game consts

        :param charId: (int) id of the character, based off of team
        :param name: (string) name of the character
        :param classId: (int) class key
        """

        #Game related attributes
        self.posX = 0.0
        self.posY = 0.0
        self.id = charId
        self.name = name
        self.classId = classId

        #Crowd controls
        self.stunned = False
        self.silenced = False

        classJson = gameConstants.classesJson[classId]

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


    def toJson(self):
        """ Returns information about character as a json
        """

        #TODO finish

        json = {}
        json['charId'] = self.id
        json['x'] = self.posX
        json['y'] = self.posY
        json['name'] = self.name
        json['class'] = self.classId
        json['attributes'] = self.attributes.toJson()

        return json


class Attributes(object):

    def __init_(self, health, damage, abilityDamage, attackRange, armor, movementSpeed):
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

    def toJson(self):
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
