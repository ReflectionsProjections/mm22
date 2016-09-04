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

        # A json object if the character is casting an ability
        # {"abilityId": (int), "currentCastTime": (int)}
        self.casting = None

        self.buffs = []
        self.debuffs = []
        self.pending_stat_changes = []

    def init(self, json):
        try:
            self.name = json['characterName']

            if not self.name:
                print("Invalid character name:")
                print(json)
                return False

            self.classId = json['classId']

            self.classJson = gameConstants.classesJson[self.classId]

            self.attributes = Attributes(self.classJson['Health'],
                                         self.classJson['Damage'],
                                         self.classJson['AttackRange'],
                                         self.classJson['AttackSpeed'],
                                         self.classJson['Armor'],
                                         self.classJson['MovementSpeed'])

            # A Json that contains abilities by id and their cooldown by id
            self.abilities = {}
            for ability in self.classJson['Abilities']:
                self.abilities[ability] = 0.0

            return True

        except KeyError as err:
            print("Failed to find key when init'ing a character:")
            print(json)
            return False

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

    def can_use_ability(self, ability_id):
        """ Checks if a character can use an ability (must have that ability)
        :param ability_id: id of the ability to check
        :return: True if yes, False if no
        """
        # Does this character actually have the ability?
        if ability_id not in self.abilities:
            return False

        return self.abilities[ability_id] == 0
        
        # Is the character stunned?
        if (self.stunned):
            return False
        return self.abilities[ability_id] == 0
        
        # Is the character silenced?
        if (self.silenced):
            return False
        return self.abilities[ability_id] == 0

    def use_ability(self, ability_id, character):
        # Does this ability even exist?
        if 0 > ability_id or ability_id > len(gameConstants.abilitiesList):
            return False

        # Is the ability on cooldown?
        if not self.can_use_ability(self, ability_id):
            return False

        # Reset casting
        self.casting = None

        if gameConstants.abilitiesList[ability_id]['Casttime'] > 0:
            self.casting = {"abilityId": ability_id, "currentCastTime": 0}
        else:
            self.cast_ability(ability_id, character)

    def cast_ability(self, ability_id, character=None):
        """
        Casts a given ability by id, assumes that if it has a cast time it has waited that amount of time
        :param ability_id:
        :param character: Character object to cast on, if needed
        :return: None
        """
        # If the character is silenced or stunned, it is unable to cast a spell
        if self.attributes.get_attribute('Silenced') or self.attributes.get_attribute('Stunned'):
            return

        self.casting = None

        # Get ability json
        ability = gameConstants.abilitiesList[ability_id]

        # Apply Cooldown
        self.abilities[ability_id] = ability["Cooldown"]

        # Iterate through stat changes
        for stat_change in ability['StatChanges']:
            if stat_change['Target'] == 0:
                self.apply_stat_change(stat_change)
            elif stat_change['Target'] in [1,2,3] and character is not None:
                character.apply_stat_change(stat_change)

    def apply_stat_change(self, stat_change, remove=False):
        # Apply stat change
        self.attributes.change_attribute(stat_change['attribute'], stat_change['change'])

        # If there a time on the buff/debuff, make note and it is not the removal of a buff/debuffs
        if not remove:
            if stat_change['attribute'] is 'AttackSpeed':
                if stat_change['change'] > 0:
                    self.debuffs.append(stat_change)
                elif stat_change < 0:
                    self.buffs.append(stat_change)
            else:
                # Interrupt casting if silenced/stunned
                if (stat_change['attribute'] is 'Silenced' or stat_change['attribute'] is 'Stunned') and stat_change['change'] < 0:
                    self.casting = None
                if stat_change['change'] < 0:
                    self.debuffs.append(stat_change)
                elif stat_change['change'] > 0:
                    self.buffs.append(stat_change)

    def can_move(self):
        return not (self.attributes.get_attribute("Rooted") or self.attributes.get_attribute("Stunned"))

    def movement(self, new_pos, map):
        # Can we move?
        if not self.can_move():
            return "Unable to move currently"

        # Same position
        if (self.posX, self.posY) == new_pos:
            return "Same location"

        # Actually find path
        if not map.can_move_to((self.posY, self.posY),
                               new_pos,
                               self.attributes.get_attribute("MovementSpeed")):
            return "Unable to find path to new location"

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

    def __init__(self, health, damage, attackRange, attackSpeed, armor, movementSpeed, silenced=False, stunned=False, rooted=False):
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
        self.attackRange = attackRange
        self.attackSpeed = attackSpeed
        self.armor = armor
        self.movementSpeed = movementSpeed
        self.stunned = stunned
        self.silenced = silenced
        self.rooted = rooted

    def change_attribute(self, attribute_name, change):
        # Health is the only one that has a limit on it
        if attribute_name == 'Health':
            self.health = max(0, min(self.health + change, self.maxHealth))
        if attribute_name == 'Damage':
            self.damage += change
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
        if attribute_name == 'MaxHealth':
            return self.maxHealth
        if attribute_name == 'Health':
            return self.health
        if attribute_name == 'Damage':
            return max(0, self.damage)
        if attribute_name == 'AttackSpeed':
            return max(1, self.attackSpeed)
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
        json['Health'] = self.get_attribute('Health')
        json['Damage'] = self.get_attribute('Damage')
        json['AttackSpeed'] = self.get_attribute('AttackSpeed')
        json['AttackRange'] = self.get_attribute('AttackRange')
        json['Armor'] = self.get_attribute('Armor')
        json['MovementSpeed'] = self.get_attribute('MovementSpeed')
        json['Silenced'] = self.get_attribute('Silenced')
        json['Stunned'] = self.get_attribute('Stunned')
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

    def toJson(self):
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