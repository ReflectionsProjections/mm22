from src.game.gamemap import *
from src.game.team import Team

# Useful for debugging
import sys
import traceback


class InvalidPlayerException(Exception):
    pass


class Game(object):

    def __init__(self, totalTurns):
        """ Init the game object
        :param totalTurns: (int) max number of ticks in a game
        """

        self.totalTurns = totalTurns
        self.turnsExecuted = 0
        
        self.queuedTurns = {}
        self.turnResults = {}
        self.teams = []

        # Load map
        self.map = GameMap()

    def add_new_player(self, jsonObject):
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
            elif len(jsonObject["classes"]) == 0:
                error = "list of classes can not be empty"
            else:
                for characterJson in jsonObject['classes']:
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
        teamId = len(self.teams)
        self.teams.append(Team(teamId, jsonObject['teamName'], jsonObject['classes']))

        # Return response (as a JSON object)
        return (True, self.teams[teamId].toJson())

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
            for charater_actionJson in actions:
                action = actionJson.get("action", "").lower()
                playerId = actionJson.get("characterId", -1)
                targetId = actionJson.get("target", -1)
                actionResult = {"teamId": playerId, "action": action, "target": targetId}

                try:
                    # Get player character object
                    player = None
                    for team in self.teams:
                        player = team.get_character(id=playerId)
                        if player:
                            break
                    # Get target character object
                    target = None
                    for team in self.teams:
                        target = team.get_character(id=targetId)
                        if target:
                            break
                    # If there is no target, target is the player player
                    if not target:
                        target = player
                    if player:
                        if action == "move":
                            if self.map.can_move_to((player.posX, player.posY), targetId, max_distance=player.attributes.get_attribute("MovementSpeed")):
                                player.posX = targetId[0]
                                player.posY = targetId[1]
                            else:
                                actionResult["message"] = "Player " + playerId + " is unable to move there!"
                        elif action == "attack":
                            if player == target or target == None:
                                actionResult["message"] = "Invalid target to attack"
                                continue
                            distance = len(self.map.path_between((player.posX, player.posY), targetId))
                            if distance == 1 or (distance <= player.attribute.get_attribute("AttackRange") and self.map.in_vision_of((player.posX, player.posY), targetId)):
                                continue
                            else:
                                continue
                        elif action == "cast":
                            continue
                        else:
                            actionResult["message"] = "Invalid action type."
                    else:
                        actionResult["message"] = "Invalid character."
                except InsufficientPowerException as e:
                    actionResult["message"] = "Insufficient networking and/or processing."
                except IndexError:
                    actionResult["message"] = "Invalid playerID."
                except ValueError:
                    actionResult["message"] = "Type mismatch in parameter(s)."
                except (RepeatedActionException,
                        InsufficientPowerException,
                        ActionOwnershipException,
                        MultiplierMustBePositiveException,
                        NodeIsDDoSedException,
                        IpsPreventsActionException) as e:
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
        done = self.totalTurns > 0 and self.totalTurns <= self.turnsExecuted
        if done:
            total_teams = len(self.teams)
            for team in self.teams


        # Done!
        self.queuedTurns = {}
        self.turnsExecuted += 1
        return not done

    # Return the results of a turn ("server response") for a particular player
    def get_info(self, playerId):
        if playerId not in self.playerInfos:
            raise InvalidPlayerException("Player " + playerId + " doesn't exist.")

        return {
            "playerInfo": self.playerInfos[playerId],
            "turnResult": self.turnResults.get(playerId, [{"status": "fail", "message": "No turn executed."}]),
            "map":  [x.toPlayerDict(x.scanPending) for x in list(visibleNodes)]
        }

    # Return the entire state of the map
    def get_all_info(self):
        return {
            "playerInfos": self.playerInfos,
            "turnResults": [self.turnResults.get(pId, [{"status": "fail", "message": "No turn executed."}]) for pId in self.playerInfos],
            "map":  [x.toPlayerDict(True) for x in self.map.nodes.values()]
        }
