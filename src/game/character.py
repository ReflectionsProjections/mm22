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
                            classJson['AttackSpeed'],
                            classJson['Armor'],
                            classJson['movementSpeed'])

        # A Json that contains abilities by id and their cooldown by id
        self.abilities = {}
        for ability in classJson['Abilities']:
            self.abilities[ability] = 0.0

        self.buffs = []
        self.debuffs = []

    def update(self):
        # Update ability cooldowns
        for ability in self.abilities:
            if self.abilities[ability] > 0:
                self.abilities[ability] -= 0

        # Update buffs
        for buff in self.buffs:
            if buff['Time'] == 0:
                self.apply_stat_change(buff['StatChange']['Attribute'], -buff['ActualChange'])
                self.buffs.remove(buff)
            else:
                buff['Time'] -= 0

        # Update debuffs
        for debuff in self.debuffs:
            if debuff['Time'] == 0:
                self.apply_stat_change(debuff['StatChange']['Attribute'], -debuff['ActualChange'])
                self.debuffs.remove(debuff)
            else:
                debuff['Time'] -= 0

    def can_use_ability(self, ability_id):
        """ Checks if a character can use an ability (must have that ability)
        :param ability_id: id of the ability to check
        :return: True if yes, False if no
        """
        # Does this character actually have the ability?
        if ability_id not in self.abilities:
            return False
        return self.abilities[ability_id] == 0

    def use_ability(self, ability_id, character):
        # Does this ability even exist?
        if ability_id < len(gameConstants.abilitiesList):
            return False
        # Is the ability on cooldown?
        if not self.can_use_ability(self, ability_id):
            return False

        # Apply Cooldown
        self.abilities[ability_id] = gameConstants.abilitiesList[ability_id]["Cooldown"]

        # Get ability json
        ability = gameConstants.abilitiesList[ability_id]

        # Iterate through stat changes
        for stat_change in ability['StatChanges']:
            if stat_change['Target'] == 0:
                self.apply_stat_change(stat_change, self.attributes.abilityPower)
            if stat_change['Target'] == 1:
                character.apply_stat_change(stat_change, -self.attributes.abilityPower)

    def apply_stat_change(self, stat_change, abilityPower):

        # Will hold the value the change for reverting after the buff/debuff fades (if it is one)
        actual_change = 0

        # Apply stat change
        if stat_change['Health']:
            actual_change = self.attributes.change_attribute(self, stat_change['Attribute'], stat_change['change'] + abilityPower)
        else:
            actual_change = self.attributes.change_attribute(self, stat_change['Attribute'], stat_change['change'])

        # If there a time on the buff/debuff, make note
        buff_json = {"StatChange": stat_change, "Time": stat_change['Time'], "ActualChange": actual_change}
        if actual_change < 0:
            self.debuffs.append(buff_json)
        else:
            self.buffs.append(buff_json)

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

    def __init_(self, health, damage, abilityPower, attackRange, attackSpeed, armor, movementSpeed):
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
        self.movementSpeed = max(0, self.movementSpeed)

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
