import src.game.game_constants as gameConstants


class Character(object):

    total_characters = 0

    @staticmethod
    def get_new_character_id():
        Character.total_characters += 1
        return Character.total_characters

    @staticmethod
    def remove_all_characters():
        Character.total_teams = 0

    def __init__(self):
        #Game related attributes
        self.posX = 0
        self.posY = 0
        self.id = Character.get_new_character_id()
        self.dead = False

        # A json object if the character is casting an ability
        # {"abilityId": (int), "currentCastTime": (int)}
        self.casting = None

        self.buffs = []
        self.debuffs = []
        self.pending_stat_changes = []

    def init(self, json):
        error = ""

        if 'classId' not in json:
            error += "Could not find classId key in json. defaulting to Warrior."
            self.classId = "warrior"
        elif json['classId'] not in gameConstants.classesJson:
            error += "Invalid classId, defaulting to Warrior."
            self.classId = "warrior"
        else:
            self.classId = json['classId']

        if 'characterName' not in json:
            error += "Could not find characterName key in json, defaulting to classId."
            self.name = self.classId
        elif not json['characterName'] or len(json['characterName']) >= 12:
            error += "Invalid characterName (empty or longer than 12 characters), defaulting to classId."
            self.name = self.classId
        else:
            self.name = json['characterName']

        self.classJson = gameConstants.classesJson[self.classId]

        self.attributes = Attributes(self.classJson['Health'],
                                     self.classJson['Damage'],
                                     self.classJson['SpellPower'],
                                     self.classJson['AttackRange'],
                                     self.classJson['Armor'],
                                     self.classJson['MovementSpeed'])

        # A Json that contains abilities by id and their cooldown by id
        self.abilities = {}
        for ability in self.classJson['Abilities']:
            self.abilities[ability] = 0

        return error

    def apply_pending_stat_changes(self):
        for stat_change in self.pending_stat_changes:
            self.apply_stat_change(stat_change)

    def update(self):
        if self.casting:
            if self.casting["currentCastTime"] == 0:
                self.cast_ability(self.casting["abilityId"])
            self.casting["currentCastTime"] -= 1

        # Update ability cooldowns
        for ability in self.abilities:
            if self.abilities[ability] > 0:
                self.abilities[ability] -= 0

        # Update buffs
        for buff in self.buffs:
            if buff['time'] == 0:
                self.apply_stat_change(buff, remove=True)
                self.buffs.remove(buff)
            else:
                buff['time'] -= 0

        # Update debuffs
        for debuff in self.debuffs:
            if debuff['time'] == 0:
                self.apply_stat_change(debuff, remove=True)
                self.debuffs.remove(debuff)
            else:
                debuff['time'] -= 0

        # Apply buffs and debuffs
        self.apply_pending_stat_changes()
        self.attributes.update()

        if self.attributes.get_attribute("Health") <= 0:
            self.dead = True

    def can_use_ability(self, ability_id):
        """ Checks if a character can use an ability (must have that ability)
        :param ability_id: id of the ability to check
        :return: True if yes, False if no
        """
        # Does this character actually have the ability?
        if ability_id not in self.abilities:
            return False
        
        # Is the character stunned?
        if self.stunned:
            return False
        
        # Is the character silenced?
        if self.silenced:
            return False

        return self.abilities[ability_id] == 0

    def use_ability(self, ability_id, character):
        if not self.can_use_ability(self, ability_id):
            return False

        # Reset casting
        self.casting = None

        if gameConstants.abilitiesList[ability_id]['CastTime'] > 0:
            self.casting = {"abilityId": ability_id, "currentCastTime": 0}
        else:
            self.cast_ability(ability_id, character)

    def cast_ability(self, ability_id, character=None):
        """
        Casts a given ability by id, assumes that if it has a cast time it has waited that amount of time
        :param ability_id:
        :param character: Character object to cast on, if needed
        :return: None or string error
        """
        # If the character is silenced or stunned, it is unable to cast a spell
        if self.attributes.get_attribute('Silenced') or self.attributes.get_attribute('Stunned'):
            return "Character is silenced or stunned"

        self.casting = None

        # Get ability json
        ability = gameConstants.abilitiesList[ability_id].copy()

        # Apply Cooldown
        self.abilities[ability_id] = ability["Cooldown"]

        # Iterate through stat changes
        for stat_change in ability['StatChanges']:
            if stat_change['Attribute'] == 'Health':
                if stat_change['Change'] > 0:
                    stat_change['Change'] = stat_change['Change'] + self.attributes.get_attribute("SpellPower")
                elif stat_change['Change'] < 0:
                    stat_change['Change'] = stat_change['Change'] - self.attributes.get_attribute("SpellPower")
            if stat_change['Target'] == 0:
                self.add_stat_change(stat_change)
            elif stat_change['Target'] in [1,2,3] and character is not None:
                character.add_stat_change(stat_change)

    def add_stat_change(self, stat_change):
        self.pending_stat_changes.append(stat_change)

    def apply_stat_change(self, stat_change, remove=False):
        change = stat_change['Change']
        if stat_change['Attribute'] == 'Health':
            if change < 0: # damage
                change = min(0, change + self.attributes.get_attribute("Armor"))

        stat_change['Change'] = change * (-1 if remove else 1)

        # Apply stat change
        self.attributes.change_attribute(
            stat_change['Attribute'],
            stat_change['Change'])

        if stat_change['Time'] == 0:
            return

        # If there a time on the buff/debuff, make note and it is not the removal of a buff/debuffs
        if remove:
            if stat_change['Change'] < 0:
                self.debuffs.remove(stat_change)
            elif stat_change['Change'] > 0:
                self.buffs.remove(stat_change)
        else:
            # Interrupt casting if silenced/stunned
            if (stat_change['Attribute'] is 'Silenced' or stat_change['Attribute'] is 'Stunned') and stat_change['Change'] < 0:
                self.casting = None
            if stat_change['Change'] < 0:
                self.debuffs.append(stat_change)
            elif stat_change['Change'] > 0:
                self.buffs.append(stat_change)

    def can_move(self):
        return not (self.attributes.get_attribute("Rooted") or self.attributes.get_attribute("Stunned"))

    def movement(self, new_pos, map):
        # Can we move?
        if not self.can_move():
            return "Unable to move currently"

        # Same position
        if (self.posX, self.posY) == new_pos:
            return

        # Actually find path
        if not map.can_move_to((self.posY, self.posY),
                               new_pos,
                               self.attributes.get_attribute("MovementSpeed")):
            return "Not enough movement speed to reach target"

        self.posX = new_pos[0]
        self.posY = new_pos[1]
        self.casting = None

    def toJson(self):
        """ Returns information about character as a json
        """

        json = {}
        json['charId'] = self.id
        json['name'] = self.name
        json['x'] = self.posX
        json['y'] = self.posY
        json['name'] = self.name
        json['class'] = self.classId
        json['attributes'] = self.attributes.toJson()
        json['abilities'] = self.abilities
        json['buffs'] = self.buffs
        json['debuffs'] = self.debuffs
        json['casting'] = self.casting

        return json
		

class Attributes(object):

    def __init__(self,
                 health,
                 damage,
                 spellPower,
                 attackRange,
                 armor,
                 movementSpeed,
                 silenced=0,
                 stunned=0,
                 rooted=0):
        """ Init attributes for a character
        :param health: (float) health
        :param damage: (float) damage per tick
        :param attackRange: (int) attackRange of auto attack
        :param attackSpeed: (int) attackSpeed of auto attacks
        :param armor: (float) damage removed from attacks
        :param movementSpeed: (int) movement per tick
        :param stunned: (bool) stun status
        :param rooted: (bool) root status
        :param silenced: (bool) silence status
        """

        self.maxHealth = health
        self.health = health
        self.damage = damage
        self.spellPower = spellPower
        self.attackRange = attackRange
        self.armor = armor
        self.movementSpeed = movementSpeed
        self.stunned = stunned
        self.silenced = silenced
        self.rooted = rooted

    def update(self):
        self.health = max(0, min(self.health, self.maxHealth))

    def change_attribute(self, attribute_name, change):
        # Health is the only one that has a limit on it
        if attribute_name == 'Health':
            self.health += change
        if attribute_name == 'Damage':
            self.damage += change
        if attribute_name == 'SpellPower':
            self.spellPower += change
        if attribute_name == 'AttackSpeed':
            self.attackSpeed += change
        if attribute_name == 'AttackRange':
            self.attackRange += change
        if attribute_name == 'Armor':
            self.armor += change
        if attribute_name == 'MovementSpeed':
            self.movementSpeed += change
        if attribute_name == 'Stunned':
            self.stunned += change
        if attribute_name == 'Silenced':
            self.silenced += change
        if attribute_name == 'Rooted':
            self.rooted += change

    def get_attribute(self, attribute_name):
        """
        Get the game value of the attribute, should only be used when trying to modify other stat changes
        :param attribute_name: (string) attribute name
        :return: (int) stat change
        """
        if attribute_name == 'MaxHealth':
            return self.maxHealth
        if attribute_name == 'Health':
            return self.health
        if attribute_name == 'Damage':
            return max(0, self.damage)
        if attribute_name == 'SpellPower':
            return max(0, self.spellPower)
        if attribute_name == 'AttackRange':
            return max(0, self.attackRange)
        if attribute_name == 'Armor':
            return max(0, self.armor)
        if attribute_name == 'MovementSpeed':
            return max(0, self.movementSpeed)
        if attribute_name == 'Stunned':
            return self.stunned < 0
        if attribute_name == 'Silenced':
            return self.silenced < 0
        if attribute_name == 'Rooted':
            return self.rooted < 0

    def toJson(self):
        """ Return json of information containing all attribute information
        """

        json = {}
        json['MaxHealth'] = self.maxHealth
        json['Health'] = self.health
        json['Damage'] = self.damage
        json['SpellPower'] = self.spellPower
        json['AttackRange'] = self.attackRange
        json['Armor'] = self.armor
        json['MovementSpeed'] = self.movementSpeed
        json['Silenced'] = self.silenced
        json['Stunned'] = self.stunned
        json['Rooted'] = self.rooted
        return json