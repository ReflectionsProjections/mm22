from src.game.gamemap import *
from src.game.character import *
from src.game.team import Team
import src.game.game_constants as gameConst


class InvalidPlayerException(Exception):
    pass


class Game(object):

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
            if "teamName" not in jsonObject:
                error = "Missing 'teamName' parameter"
            elif len(jsonObject["teamName"]) == 0:
                error = "'teamName' cannot be an empty string"
            elif len(jsonObject["characters"]) == 0:
                error = "list of classes can not be empty"
            else:
                for characterJson in jsonObject['characters']:
                    if "characterName" not in characterJson:
                        error = "Missing 'characterName' for a character"
                    elif "classId" not in characterJson:
                        error = "Missing 'classId' for a character"
        except KeyError as e:
            error = "json response doesn't have the correct format"

        # If there is an error, return false and error
        if error:
            return (False, error)

        # Add player to game data
        new_team = Team(jsonObject['teamName'])
        for character in jsonObject['characters']:
            new_team.add_character(character)

        self.teams[new_team.id] = new_team

        self.playerInfos[playerId] = jsonObject
        self.playerInfos[playerId]["id"] = playerId
        self.playerInfos[playerId]["teamId"] = new_team.id

        # Return response (as a JSON object)
        return (True, new_team.toJson())

    # Add a player's actions to the turn queue
    def queue_turn(self, turnJson, playerId):
        self.queuedTurns[playerId] = turnJson

    # Execute everyone's actions for this turn
    # @returns True if the game is still running, False otherwise
    def execute_turn(self):

        # Execute turns
        self.turnResults = {}
        for playerId in self.queuedTurns:
            turn = self.queuedTurns[playerId]

            # Get actions
            actions = []
            try:
                actions = list(turn.get("actions", []))
            except:
                self.turnResults[playerId] = [{"status": "fail", "messages": "'Actions' parameter must be a list."}]
                continue  # Skip invalid turn

            # Execute actions
            self.turnResults[playerId] = []
            for actionJson in actions:
                action = actionJson.get("action", "").lower()
                teamId = self.playerInfos[playerId]["team"]
                characterId = actionJson.get("characterId", -1)
                targetId = actionJson.get("target", -1)
                actionResult = {"teamId": playerId, "action": action, "target": targetId}

                try:
                    # Get player character object
                    character = team[teamId].get_character(id=characterId)

                    # Get target character object
                    target = None
                    for teamId, team in self.teams:
                        target = team.get_character(id=targetId)
                        if target:
                            break
                    # If there is no target, target is the player player
                    if not target:
                        target = player
                    if character:
                        if action == "move":
                            if targetId != -1:
                                ret = character.move_to(targetId, self.map)
                                if ret is not None:
                                    actionResult["message"] = "Unable to move Character-" + characterId + ": " + ret
                        elif action == "attack":
                            if character == target or target is None:
                                actionResult["message"] = "Invalid target to attack"
                                continue
                            distance = len(self.map.path_between((character.posX, character.posY), targetId))
                            if distance == 1 or (distance <= character.attribute.get_attribute("AttackRange") and self.map.in_vision_of((character.posX, character.posY), targetId)):
                                continue
                            else:
                                continue
                        elif action == "cast":
                            continue
                            if target is None:
                                actionResult["message"] = "Invalid target to attack"
                                continue
                        else:
                            actionResult["message"] = "Invalid action type."
                    else:
                        actionResult["message"] = "Invalid character."
                except IndexError:
                    actionResult["message"] = "Invalid playerID."
                except ValueError:
                    actionResult["message"] = "Type mismatch in parameter(s)."
                except (RepeatedActionException) as e:
                    actionResult["message"] = str(e)
                except Exception as e:
                    raise  # Uncomment me to raise unhandled exceptions
                    actionResult["message"] = "Unknown exception: " + str(e)

                actionResult["status"] = "fail" if "message" in actionResult else "ok"
                if "message" not in actionResult:
                    actionResult["powerSources"] = powerSources

                # Record results
                self.turnResults[playerId].append(actionResult)

        # Determine winner if appropriate
        alive_teams = []
        for teamId, team in self.teams.items():
            alive_team = False
            for character in team.characters:
                if character.attributes.get_attribute("Health") != 0:
                    alive_team = True
            if alive_team:
                alive_teams.append(team.id)

        # Done!
        self.queuedTurns = {}
        self.turnsExecuted += 1
        # False if game is finished\
        return len(alive_teams) >= 2 and self.turnsExecuted <= self.totalTurns

    # Return the results of a turn ("server response") for a particular player
    def get_info(self, playerId):
        if playerId not in self.playerInfos:
            raise InvalidPlayerException("Player " + playerId + " doesn't exist.")

        return {
            "playerInfo": self.playerInfos[playerId],
            "turnResult": self.turnResults.get(playerId, [{"status": "fail", "message": "No turn executed."}]),
            "teamInfo": self.teams[self.playerInfos[playerId]['teamId']].toJson()
        }

    # Return the entire state of the map
    def get_all_info(self):
        return {
            "playerInfos": self.playerInfos,
            "turnResults": [self.turnResults.get(pId, [{"status": "fail", "message": "No turn executed."}]) for pId in self.playerInfos],
            "teams": [team.toJson() for teamId, team in self.teams.items()]
        }
