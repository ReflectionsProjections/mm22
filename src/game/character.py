import gameConstants as gameConstants


class Character(object):


    def __init__(self, classKey):
        """ Init a character class based on class key defined in game consts

        :param charId: (int) id of the character, based off of team
        :param name: (string) name of the character
        :param classId: (int) class key
        """

        #Game related attributes
        self.positionX = 0.0
        self.positionY = 0.0
        self.characterId = Character.numCharacters
        Character.numCharacters += 1

        #Crowd controls
        self.stunned = False
        self.silenced = False

        classJson = gameConstants.classesJson[classId]

        self.attributes = Attributes( classJson['Health'],
                            classJson['Damage'],
                            classJson['AbilityPower'],
                            classJson['AttackRange'],
                            classJson['AttackSpeed'],
                            classJson['Armor'],
                            classJson['MovementSpeed'])

        # A Json that contains abilities by id and their cooldown by id
        self.abilities = {}
        for ability in classJson['Abilities']:
            self.abilities[ability] = 0.0

	#Container for BuffDebuff Objects
        self.buffs_and_debuffs = []

    def addBuffDebuff(self, buffDebuff):
	"""Adds a buff or debuff to the Character object
	"""
	self.buffs_and_debuffs.append(buffDebuff)    
    
    def updateBuffs(self):
        """ Goes through all the buffs and debuffs within the
	    'buffs_and_debuffs' list and applies their
	     modifications to the Attributes of the Character.

	     Call this function in the game loop that loops for
		every tick of the game (probably before damage
		to the Character is resolved).

	     If the duration of any of the buffs or debuffs
	     reaches zero, it is removed from the list. 

	     If any more attributes are added on later, the if/else 
	     chains of this function will need to have additional
	     clauses for each of the added attributes
	"""

	#handle restoration of attributes when buffs 
   	#  run out of time
	for buff in self.buffs_and_debuffs:
	  
	  if buff.duration == 0 and (not buff.lasting):
	    attr = buff.attribute
	    if attr == "Health":
                self.attributes.health -= buff.restoreValue
	    elif attr == "Damage":
	        self.attributes.damage -= buff.restoreValue
	    elif attr == "AttackRange":
		self.attributes.attackRange -= buff.restoreValue
            elif attr == "AbilityDamage":
		self.attributes.abilityDamage -= buff.restoreValue
	    elif attr == "Armor":
		self.attributes.armor -= buff.restoreValue
	    elif attr == "MovementSpeed":
		self.attributes.movementSpeed -= buff.restoreValue
            else:
		raise NameError("Invalid Attribute Name")			

        #remove any buffs from the container if they are done,
	#  that being the duration has run out (equals 0)
	self.buffs_and_debuffs = [buff for buff in
	    self.buffs_and_debuffs if buff.duration > 0]

	#go through the buffs_and_debuffs container, applying
	#  modifications if necessary and decreasing the duration
	#  of the b/d	
	for buff in self.buffs_and_debuffs:
	    #apply the buff's modification
	    if buff.timesApplied > 0:
		attr = buff.attribute
		if attr == "Health":
		    self.attributes.health += buff.modification
		elif attr == "Damage":
		    self.attributes.damage += buff.modification
		elif attr == "AttackRange":
		    self.attributes.attackRange += buff.modification
		elif attr == "AbilityDamage":
		    self.attributes.abilityDamage += buff.modification
		elif attr == "Armor":
		    self.attributes.armor += buff.modification
		elif attr == "MovementSpeed":
		    self.attributes.movementSpeed += buff.modification
		else:
		    raise NameError("Invalid Attribute Name")			
		buff.timesApplied -= 1
		
	    buff.duration -= 1

	
	
    def toJson():
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

    def __init__(self, health, damage, abilityDamage, attackRange, armor, movementSpeed):
        """ Init attributes for a character
        :param health: (float) health
        :param damage: (float) damage per tick
        :param attackRange: (int) attackRange of auto attack
        :param attackSpeed: (int) attackSpeed of auto attacks
        :param armor: (float) damage removed from attacks
        :param movementSpeed: (int) movement per tick
        """

        self.maxHealth = health
        self.health = health
        self.damage = damage
        self.abilityPower= abilityPower
        self.attackRange = attackRange
        self.attackSpeed = attackSpeed
        self.armor = armor
        self.movementSpeed = movementSpeed

    def change_attribute(self, attribute_name, change):
        if attribute_name == 'Health':
            return self.change_health(change)
        if attribute_name == 'Damage':
            return self.change_damage(change)
        if attribute_name == 'AbilitiyDamage':
            return self.change_ability_damage(change)
        if attribute_name == 'AttackSpeed':
            return self.change_attack_speed(change)
        if attribute_name == 'AttackRange':
            return self.change_attack_range(change)
        if attribute_name == 'Armor':
            return self.change_armor(change)
        if attribute_name == 'MovementSpeed':
            return self.change_movement_speed(change)

    def change_health(self, change):
        if change < 0:
            self.health = max(0, self.health + max(0, change + self.armor))
        if change > 0:
            self.health = min(self.maxHealth, self.health + change)

    def change_damage(self, change):
        self.damage = max(0, self.damage + change)

    def change_ability_damage(self, change):
        self.abilityPower = max(0, self.abilityPower + change)

    def change_attack_speed(self, change):
        self.attackSpeed = max(0, self.attackSpeed + change)

    def change_attack_range(self, change):
        self.attackRange = max(1, self.attackRange + change)

    def change_armor(self, change):
        self.armor = max(0, self.armor + change)

    def change_movement_speed(self, change):
        new_change = change_in_Value()
        self.movementSpeed = max(0, self.movementSpeed + change)

    def change_in_value(self, value, change, max=None, min=None):
        """ Given a initial value and change to that value along with a min or max, it will return the required change up to min/max if needed
        :param value: (int) Original value
        :param change: (int) change to value
        :param max: (int)
        :param min: (int)
        :return:
        """
        if not value and not change:
            return 0

        new_value = value + change

        if min:
            return change + (min - new_value)
        if max:
            return change + (max - new_value)
        return change

    def toJson(self):
        """ Return json of information containing all attribute information
        """

        json = {}
        json['MaxHealth'] = self.maxHealth
        json['Health'] = self.health
        json['Damage'] = self.damage
        json['AbilityPower'] = self.abilityPower
        json['AttackSpeed'] = self.attackSpeed
        json['AttackRange'] = self.attackRange
        json['Armor'] = self.armor
        json['MovementSpeed'] = self.movementSpeed

        return json

class BuffDebuff:
    """ BuffDebuff objects are added to the buffs_and_debuffs
	    list of a Character and affect a Character's attributes.
	View the parameters of the constructor to see how to tailor
	    a buff/debuff accordingly.
    """
    def __init__(self, name, duration, attribute, modification,
	timesApplied, lasting):
	"""
	:param name (string) name of the buff/debuff
	:param duration: (int) how  many ticks the buff/debuff lasts,
		is decremented every turn until it reaches 0 (then the b/d
		 removed)
	:param attribute: (string) name of the attribute that is to be
		 affected. 
	:param modification (float) the amount that is added to the 
	 	targeted attribute.  If you want to decrease the value
		of an attribute, pass in a negative value 
	:param timesApplied: (int) the amount of times the b/d 
		is applied.  For example, a shield buff would 
		buff health once and thus would have this param
		set to 1.  A bleeding debuff would set this param
		to the same as 'duration' param to have the health
		parameter decreased multiple times.
	:param lasting (boolean) If False, the modification is 
		reverted once the duration of the buff runs out.
		For example, if a speed buff was added, the
		movementSpeed attribute will be reverted to what 
		its value was before the buff was applied. For
		most buffs and debuffs 'lasting' should be false.

	        If True, the modification lasts even after the
	        buff runs out out(i.e. a shield).
	"""
	self.name = name
	self.duration = duration
	self.attribute = attribute
	self.modification = modification
	self.timesApplied = timesApplied
	self.lasting = lasting	
	#used for restoring attributes when the buff is finished
	self.restoreValue = timesApplied * modification
  
    def toJson():
	""" Returns json of BuffDebuff's information
	    This is here b/c it seemed necessary, but delete if not :P
	"""

	json = {}
	json['Name'] = self.name
	json['Duration'] = self.duration
	json['Attribute'] = self.attribute
	json['Modification'] = self.modification
	json['TimesApplied'] = self.timesApplied
	json['Lasting'] = self.lasting
	json['RestoreValue'] = self.restoreValue
	return json


