import gameConstants

class Character:

    numCharacters = 0

    def __init__(self, classKey):
        """ Init a character class based on class key defined in game consts
        :param classKey: (string) class key
        """

        #Game related attributes
        self.positionX = 0.0
        self.positionY = 0.0
        self.characterId = Character.numCharacters
        Character.numCharacters += 1

        #Crowd controls
        self.stunned = False
        self.silenced = False


        classJson = gameConstants.classesJson[classKey]

        self.attributes = Attributes( classJson['Health'],
                            classJson['Damage'],
                            classJson['AbilityDamage'],
                            classJson['AttackRange'],
                            classJson['Armor'],
                            classJson['MovementSpeed'])

        self.abilities = {}
        for ability in classJson['Abilities']:
            self.abilities[ability] = 0.0

	#Container for BuffDebuff Objects
        self.buffs_and_debuffs = []

    def addBuffDebuff(self, buffDebuff):
	self.buffs_and_debuffs.append(buffDebuff)    

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

    def __init__(self, health, damage, abilityDamage, attackRange, armor, movementSpeed):
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

class BuffDebuff:

    def __init__(self, name, duration, attribute, modification,
	timesApplied):
	"""
	:param name (string) name of the buff/debuff
	:param duration: (int) how  many ticks the buff/debuff lasts,
		is decremented every turn until it reaches 0 (then the b/d
		 removed)
	:param attribute: (string) name of the attribute that is to be
		 affected
	:param modification (float) the amount that is added to the 
	 	targeted attribute.  If you want to decrease the amount,
	       	pass in a negative value 
	:param timesApplied: (int) the amount of times the b/d 
		is applied.  For example, a shield buff would 
		buff health once and thus would have this param
		set to 1.  A bleeding debuff would set this param
		to the same as 'duration' param to have the health
		parameter decreased multiple times.
	"""
	self.name = name
	self.duration = duration
	self.attribute = attribute
	self.modification = modification
	self.timesApplied = timesApplied
  
    def toJson():
	""" Returns json of BuffDebuff's information
	    This is here b/c it seemed necessary, but delete if not :P
	"""

	json = {}
	json['Name'] = self.name
	json['Duration'] = self.duration
	json['Attribute'] = self.attribute
	json['Modification'] = self.modification
	json['Constant'] = self.constant

	return json


