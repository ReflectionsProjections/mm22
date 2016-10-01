from src.game.gamemap import *
from src.game.character import *
from src.game.team import Team
import src.game.game_constants as gameConst

class UnableToHealDueToTimeException(Exception):
    pass
class InvalidPlayerException(Exception):
    pass
class InvalidCharacterException(Exception):
    pass
class DeadCharacterException(Exception):
    pass
class DeadTargetException(Exception):
    pass
class MoreThanOneActionException(Exception):
    pass

class Game(object):

    action_priority_order = ["Attack", "Cast", "Move"]

    def __init__(self):
        """ Init the game object
        :param totalTurns: (int) max number of ticks in a game
        """

        self.totalTurns = gameConst.totalTurns
        self.turnsExecuted = 0
        
        self.queuedTurns = {}
        self.turnResults = {}
        self.teams = {}
        self.playerInfos = {}

        Character.remove_all_characters()
        Team.remove_all_teams()

        # Load map
        self.map = GameMap()

    def add_new_player(self, jsonObject, playerId):
        """ Add new player to the game
        :param jsonObject: (json) json response from player
        """

        # Validate jsonObject
        error = None
        try:
            if "TeamName" not in jsonObject:
                error = "Missing 'teamName' parameter"
            elif len(jsonObject["TeamName"]) == 0:
                error = "'TeamName' cannot be an empty string"
            elif len(jsonObject["Characters"]) == 0:
                error = "list of classes can not be empty"
        except KeyError as e:
            error = "json response doesn't have the correct format"

        # If there is an error, return false and error
        if error:
            return False, error
        # Add player to game data
        new_team = Team(jsonObject['TeamName'])
        for character in jsonObject['Characters']:
            error = new_team.add_character(character)

        self.teams[new_team.id] = new_team

        self.playerInfos[playerId] = jsonObject
        self.playerInfos[playerId]["Id"] = playerId
        self.playerInfos[playerId]["TeamId"] = new_team.id

        # Return response (as a JSON object)
        return (True, new_team.toJson())

    # Add a player's actions to the turn queue
    def queue_turn(self, turnJson, playerId):
        self.queuedTurns[playerId] = turnJson

    # Execute everyone's actions for this turn
    # @returns True if the game is still running, False otherwise
    def execute_turn(self):
        # Clear Turn results
        self.turnResults = {}
        for playerId in self.queuedTurns:
            self.turnResults[playerId] = []

        # Execute turns
        for action_type in Game.action_priority_order:
            for playerId in self.queuedTurns:
                turn = self.queuedTurns[playerId]

                # Get actions
                actions = []
                try:
                    actions = list(turn.get("Actions", []))
                except:
                    self.turnResults[playerId] = [{"Status": "fail", "messages": "'Actions' parameter must be a list."}]
                    continue  # Skip invalid turn

                # Execute actions
                for actionJson in actions:
                    action = actionJson.get("Action", "")

                    actionResult = actionJson

                    if not action in Game.action_priority_order:
                        actionResult["Message"] = "Invalid action: " + action
                        continue

                    if action != action_type:
                        continue

                    teamId = self.playerInfos[playerId]["TeamId"]
                    characterId = actionJson.get("CharacterId", None)
                    targetId = actionJson.get("TargetId", None)
                    location = actionJson.get("Location", None)
                    abilityId = actionJson.get("AbilityId", None)

                    try:
                        # Get player character object
                        if characterId:
                            character = self.teams[teamId].get_character(id=characterId)
                        else:
                            actionResult["Message"] = "Invalid characterId: could not find characterId in json"
                            continue

                        # Did we find the character?
                        if not character:
                            raise InvalidCharacterException

                        # Is character dead?
                        if character.dead:
                            raise DeadCharacterException

                        if character.actioned is False:
                            character.actioned = True
                        else:
                            raise MoreThanOneActionException

                        # Get target character object
                        target = None
                        if targetId:
                            for teamId, team in self.teams.items():
                                target = team.get_character(id=targetId)
                                if target:
                                    break
                            if not target:
                                raise InvalidTargetException
                            if target.dead:
                                raise DeadTargetException

                        # Check ability id
                        if abilityId is not None and type(abilityId) is not int:
                            raise InvalidAbilityIdException

                        if action == "Move":
                            if target:
                                character.move_towards_target(target, self.map)
                            elif location:
                                character.move_towards_position(tuple(location), self.map)
                            else:
                                actionResult["Message"] = "Invalid target and couldn't find location"
                        elif action == "Attack":
                            if character == target or target is None:
                                raise InvalidTargetException

                            character.in_range_of(target, self.map, True)

                            if character.attributes.get_attribute("Stunned"):
                                raise StunnedException

                            target.add_stat_change({
                                "Target": 1,
                                "Attribute": "Health",
                                "Change": -1 * character.attributes.get_attribute("Damage"),
                                "Time": 0
                            })
                        elif action == "Cast":
                            if target is None:
                                raise InvalidTargetException
                            if abilityId is None:
                                raise InvalidAbilityIdException

                            if not (self.turnsExecuted > 120 and abilityId == 3):
                                character.use_ability(abilityId, target, self.map)
                            else:
                                raise UnableToHealDueToTimeException
                        else:
                            actionResult["Message"] = "Invalid action type."
                    except UnableToHealDueToTimeException:
                        actionResult["Message"] = "Time limit on healing! Unable to heal!"
                    except InvalidCharacterException:
                        actionResult["Message"] = "Invalid Character"
                    except InvalidTargetException:
                        actionResult["Message"] = "Invalid Target"
                    except DeadCharacterException:
                        actionResult["Message"] = "Character is dead!"
                    except DeadTargetException:
                        actionResult["Message"] = "Target is dead!"
                    except InvalidAbilityIdException:
                        actionResult["Message"] = "Character does not have that ability"
                    except AbilityOnCooldownException:
                        actionResult["Message"] = "Ability is on cooldown"
                    except RootedException:
                        actionResult["Message"] = "Character is rooted"
                    except StunnedException:
                        actionResult["Message"] = "Character is stunned"
                    except SilencedException:
                        actionResult["Message"] = "Character is silenced"
                    except NotEnoughMovementSpeedException:
                        actionResult["Message"] = "Character doesn't have enough movement speed"
                    except InvalidNewPositionException:
                        actionResult["Message"] = "Invalid new position"
                    except OutOfRangeException:
                        actionResult["Message"] = "Character out of range"
                    except MoreThanOneActionException:
                        actionResult["Message"] = "Character has more than one action"
                    except Exception as e:
                        raise  # Uncomment me to raise unhandled exceptions
                        actionResult["Message"] = "Unknown exception: " + str(e)
                    actionResult["Status"] = "Fail" if "Message" in actionResult else "Ok"

                    # Record results
                    self.turnResults[playerId].append(actionResult)

        # Update everyone
        for teamId, team in self.teams.items():
            for character in team.characters:
                try:
                    character.update()
                except:
                    pass

        for teamId, team in self.teams.items():
            for character in team.characters:
                character.update_dead()

        # Determine winner if appropriate
        alive_teams = []
        for teamId, team in self.teams.items():
            alive_team = False
            for character in team.characters:
                if not character.dead:
                    alive_team = True
            if alive_team:
                alive_teams.append(team.name)

        print("Finished turn " + str(self.turnsExecuted))

        # Done!
        self.queuedTurns = {}
        self.turnsExecuted += 1
        # False if game is finished\
        gameDone = True
        if len(alive_teams) == 0:
            gameDone = False
            print("Both teams died. Tie!")
        elif len(alive_teams) == 1:
            gameDone = False
            print("Team " + str(alive_teams[0]) + " Won")
        if self.turnsExecuted > self.totalTurns:
            gameDone = False
            print("Game ran out of time. Tie!")
        return gameDone

    # Return the results of a turn ("server response") for a particular player
    def get_info(self, playerId):
        if playerId not in self.playerInfos:
            raise InvalidPlayerException("Player " + playerId + " doesn't exist.")

        return {
            "PlayerInfo": self.playerInfos[playerId],
            "TurnNumber": self.turnsExecuted,
            "TurnResult": self.turnResults.get(playerId, [{"Status": "Fail", "Message": "No turn executed."}]),
            "Teams": [team.toJson() for teamId, team in self.teams.items()]
        }

    # Return the entire state of the map
    def get_all_info(self):
        return {
            "PlayerInfos": self.playerInfos,
            "TurnNumber": self.turnsExecuted,
            "TurnResults": [self.turnResults.get(pId, [{"Status": "Fail", "Message": "No turn executed."}]) for pId in self.playerInfos],
            "Teams": [team.toJson() for teamId, team in self.teams.items()]
        }
