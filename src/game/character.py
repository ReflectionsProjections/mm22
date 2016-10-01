import copy
import src.game.game_constants as gameConstants

# Abilities
class InvalidAbilityIdException(Exception):
    pass
class AbilityOnCooldownException(Exception):
    pass
class OutOfRangeException(Exception):
    pass
class InvalidTargetException(Exception):
    pass
# Attributes
class RootedException(Exception):
    pass
class StunnedException(Exception):
    pass
class SilencedException(Exception):
    pass
# Movement
class NotEnoughMovementSpeedException(Exception):
    pass
class InvalidNewPositionException(Exception):
    pass


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
        # Game related attributes
        self.position = (0, 0)
        self.id = Character.get_new_character_id()

        # A json object if the character is casting an ability
        # {"abilityId": (int), "currentCastTime": (int)}
        self.casting = None

        self.buffs = []
        self.debuffs = []
        self.pending_stat_changes = []
        self.map = None
        self.target = None
        self.dead = False
        self.actioned = False

    def init(self, json, x, y):
        error = ""

        self.position = (x, y)

        if 'ClassId' not in json:
            error += "Could not find ClassId key in json. defaulting to Warrior."
            self.classId = "warrior"
        elif json['ClassId'] not in gameConstants.classesJson:
            error += "Invalid classId, defaulting to Warrior."
            self.classId = "Warrior"
        else:
            self.classId = json['ClassId']

        if 'CharacterName' not in json:
            error += "Could not find CharacterName key in json, defaulting to classId."
            self.name = self.classId
        elif not json['CharacterName'] or len(json['CharacterName']) >= 12:
            error += "Invalid CharacterName (empty or longer than 12 characters), defaulting to classId."
            self.name = self.classId
        else:
            self.name = json['CharacterName']

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

    def update(self):
        if self.dead:
            return

        if self.casting is not None:
            if self.casting["CurrentCastTime"] == 0:
                self.cast_ability(self.casting["AbilityId"], self.target, self.map)
            else:
                self.casting["CurrentCastTime"] -= 1

        # Update ability cooldowns
        for ability, _ in self.abilities.items():
            if self.abilities[ability] > 0:
                self.abilities[ability] -= 1

        # Update buffs
        for buff in self.buffs:
            if buff['Time'] == 0:
                self.apply_stat_change(buff, True)
                self.buffs.remove(buff)
            else:
                buff['Time'] -= 1
        # Update debuffs
        for debuff in self.debuffs:
            if debuff['Time'] == 0:
                self.apply_stat_change(debuff, True)
                self.debuffs.remove(debuff)
            else:
                debuff['Time'] -= 1

        # Apply buffs and debuffs
        self.apply_pending_stat_changes()
        self.attributes.update()

        self.actioned = False

    def update_dead(self):
        self.apply_pending_stat_changes()
        self.attributes.update()
        if self.is_dead():
            self.dead = True

# ---------------------- Helper Functions -------------------
    def is_dead(self):
        return self.attributes.get_attribute("Health") <= 0

    def in_range_of(self, target, map, ret=False):
        if not map.in_vision_of(self.position,
                                target.position,
                                self.attributes.get_attribute("AttackRange")):
            if ret:
                raise OutOfRangeException
            else:
                return False
        return True

    def in_ability_range_of(self, target, map, ability_id, ret=False):
        if ability_id not in self.abilities:
            if ret:
                raise InvalidAbilityIdException
            else:
                return False

        if not map.in_vision_of(self.position,
                                target.position,
                                gameConstants.abilitiesList[ability_id]["Range"]):
            if ret:
                raise OutOfRangeException
            else:
                return False
        return True

    def can_use_ability(self, ability_id, ret=False):
        """ Checks if a character can use an ability (must have that ability)
        :param ability_id: id of the ability to check
        :return: True if yes, Exception if false
        """

        # Does this character actually have the ability?
        if ability_id not in self.abilities:
            if ret:
                raise InvalidAbilityIdException
            else:
                return False
        # Is the ability on cool down
        elif self.abilities[ability_id] != 0:
            if ret:
                raise AbilityOnCooldownException
            else:
                return False
        # Is it the burst ability?
        elif ability_id == 0:
            return True
        # Is the character stunned
        elif self.attributes.get_attribute("Stunned"):
            if ret:
                raise StunnedException
            else:
                return False
        # Is the character silenced
        elif self.attributes.get_attribute("Silenced"):
            if ret:
                raise SilencedException
            else:
                return False
        return True

# -------------------------------------------------------------

    def use_ability(self, ability_id, target, map):
        # Check if we can use the ability
        self.can_use_ability(ability_id, True)

        if not map.in_vision_of(self.position,
                                target.position,
                                gameConstants.abilitiesList[ability_id]["Range"]):
            raise OutOfRangeException

        if not target:
            raise InvalidTargetException
        if target.dead:
            raise InvalidTargetException

        ability = gameConstants.abilitiesList[ability_id]

        # Iterate through stat changes
        for stat_change in ability['StatChanges']:
            if stat_change['Target'] == 0 and not (target is self):
                raise InvalidTargetException

        # Reset casting
        self.casting = None

        cast_time = gameConstants.abilitiesList[ability_id]['CastTime']
        if cast_time > 0:
            self.map = map
            self.target = target
            self.casting = {"AbilityId": ability_id, "CurrentCastTime": cast_time, "TargetId": self.target.id}
        else:
            self.cast_ability(ability_id, target, map)

    def cast_ability(self, ability_id, target, map):
        """
        Casts a given ability by id, assumes that if it has a cast time it has waited that amount of time
        :param ability_id:
        :param character: Character object to cast on, if needed
        :return: None or string error
        """
        # Remove current casting
        self.casting = None

        if not target:
            raise InvalidTargetException
        elif target.dead:
            raise InvalidTargetException

        # Check if we can use the ability
        self.can_use_ability(ability_id, True)

        # Check if we are in range
        if not map.in_vision_of(self.position,
                                target.position,
                                gameConstants.abilitiesList[ability_id]["Range"]):
            raise OutOfRangeException

        # Get ability json
        ability = copy.deepcopy(gameConstants.abilitiesList[ability_id])

        # Apply cool down
        self.abilities[ability_id] = ability["Cooldown"]

        # Iterate through stat changes
        for stat_change in ability['StatChanges']:
            if stat_change['Attribute'] == 'Health':
                if stat_change['Change'] > 0:
                    stat_change['Change'] = stat_change['Change'] + self.attributes.get_attribute("SpellPower")
                elif stat_change['Change'] < 0:
                    stat_change['Change'] = stat_change['Change'] - self.attributes.get_attribute("SpellPower")
            if stat_change['Target'] == 0 and target is self:
                self.add_stat_change(stat_change)
            elif stat_change['Target'] == 1:
                target.add_stat_change(stat_change)
            else:
                raise InvalidTargetException

    def add_stat_change(self, stat_change):
        self.pending_stat_changes.append(stat_change)

    def apply_pending_stat_changes(self):
        self.pending_stat_changes = sorted(self.pending_stat_changes, key=lambda stat_change: stat_change["Change"])
        for stat_change in self.pending_stat_changes:
            self.apply_stat_change(stat_change)
        self.pending_stat_changes = []

    def apply_stat_change(self, stat_change, remove=False):
        change = stat_change['Change']

        # If we are getting attacked, reduce amount by armor
        if stat_change['Attribute'] == 'Health':
            if change < 0:  # damage
                change = min(0, change + self.attributes.get_attribute("Armor"))

        # This need to be checked after change so that we only remove if applying anti-cc not removing ccs
        # Are we breaking out of crowd control?
        if stat_change['Attribute'] in ['Rooted', 'Silenced', 'Stunned'] and change > 0:
            # If so remove debuffs with changes to crowd control
            for debuff in self.debuffs:
                if stat_change['Attribute'] in ['Rooted', 'Silenced', 'Stunned']:
                    self.debuffs.remove(debuff)

        # Are we applying or removing?
        stat_change['Change'] = change * (-1 if remove else 1)

        # Apply stat change
        self.attributes.change_attribute(
            stat_change['Attribute'],
            stat_change['Change'])

        # If the stat change is not on going then stop
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
        if self.attributes.get_attribute("Rooted"):
            raise RootedException
        elif self.attributes.get_attribute("Stunned"):
            raise StunnedException

    def move_towards_target(self, target, map):
        # Same position
        if self.position == target.position:
            return

        # Can we move?
        self.can_move()

        # Path should never be empty
        path = map.bfs(self.position, target.position)

        movement_speed = self.attributes.get_attribute("MovementSpeed")

        new_loc = None
        if movement_speed >= len(path) - 1:
            new_loc = path[-1]
        else:
            new_loc = path[movement_speed]

        self.position = new_loc
        self.casting = None

    def move_towards_position(self, new_pos, map):
        # Same position
        if self.position == new_pos:
            return

        # Can we move?
        self.can_move()

        path = map.bfs(self.position, new_pos)

        # could not find path because of invalid path
        if not path:
            raise InvalidNewPositionException

        movement_speed = self.attributes.get_attribute("MovementSpeed")

        new_loc = None
        if movement_speed >= len(path) - 1:
            new_loc = path[-1]
        else:
            new_loc = path[movement_speed]

        self.position = new_loc
        self.casting = None

    def deserialize(self):
        """ Returns information about character as a json
        """

        return {'Id': self.id,
                'Name': self.name,
                'Position': self.position,
                'ClassId': self.classId,
                'Attributes': self.attributes.deserialize(),
                'Abilities': self.abilities,
                'Buffs': self.buffs,
                'Debuffs': self.debuffs,
                'Casting': self.casting}

    def serialize(self, json):
        try:
            self.id = int(json['Id'])
            self.name = str(json['Name'])
            self.position = tuple(json['Position'])
            self.classId = str(json['ClassId'])
            self.abilities = {}
            for abilityId, cooldown in json['Abilities'].items():
                self.abilities[int(abilityId)] = int(cooldown)
            self.buffs = json['Buffs']
            self.debuffs = json['Debuffs']
            self.casting = None
            if json['Casting'] is not None:
                self.casting = {}
                for name, value in json['Casting'].items():
                    self.casting[str(name)] = int(value)
            self.attributes = Attributes()
            if not self.attributes.serialize(json['Attributes']):
                return False
        except KeyError as ex:

            ("Failed to serialize: " + str(ex))
            return False
        return True


class Attributes(object):
    def __init__(self,
                 health=0,
                 damage=0,
                 spellPower=0,
                 attackRange=0,
                 armor=0,
                 movementSpeed=0,
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
            self.stunned = max(min(self.stunned + change, 0), -1)
        if attribute_name == 'Silenced':
            self.silenced = max(min(self.silenced + change, 0), -1)
        if attribute_name == 'Rooted':
            self.rooted = max(min(self.rooted + change, 0), -1)

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

    def deserialize(self):
        """ Return json of information containing all attribute information
        """

        return {'MaxHealth': self.maxHealth,
                'Health': self.health,
                'Damage': self.damage,
                'SpellPower': self.spellPower,
                'AttackRange': self.attackRange,
                'Armor': self.armor,
                'MovementSpeed': self.movementSpeed,
                'Silenced': self.silenced,
                'Stunned': self.stunned,
                'Rooted': self.rooted}

    def serialize(self, json):
        try:
            self.maxHealth = int(json['MaxHealth'])
            self.health = int(json['Health'])
            self.damage = int(json['Damage'])
            self.spellPower = int(json['SpellPower'])
            self.attackRange = int(json['AttackRange'])
            self.armor = int(json['Armor'])
            self.movementSpeed = int(json['MovementSpeed'])
            self.silenced = int(json['Silenced'])
            self.stunned = int(json['Stunned'])
            self.rooted = int(json['Rooted'])
        except KeyError as ex:
            print("Failed to serialize: " + str(ex))
            return False
        return True
