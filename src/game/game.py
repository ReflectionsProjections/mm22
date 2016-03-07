from gamemap import *
from team import Team

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
        self.teams = {}

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
                for characterJson in jsonObject:
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
        self.teams[teamId] = Team(teamId, jsonObject['teamName'], jsonObject['classes'])

        # Return response (as a JSON object)
        return (True, {"id": teamId, 
                        "teamName": jsonObject["teamName"],
                        "teamInfo": self.teams[teamId].toJson()})

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

            # Sort actions by priority
            actions = sorted(actions, key=lambda x: x.get("id", 99999), reverse=True)

            # Execute actions
            self.turnResults[playerId] = []
            for actionJson in actions:
                action = actionJson.get("action", "").lower()
                targetId = actionJson.get("target", -1)
                actionResult = {"teamId": playerId, "action": action, "target": targetId}

                try:
                    target = self.map.nodes.get(int(targetId), None)
                    if target:
                        target.targeterId = playerId
                        target.supplierIds = supplierIds

                        powerSources = []
                        if action == "ddos":
                            powerSources = target.doDDoS()
                        elif action == "control":
                            powerSources = target.doControl(multiplier)
                        elif action == "upgrade":
                            powerSources = target.doUpgrade()
                        elif action == "clean":
                            powerSources = target.doClean()
                        elif action == "scan":
                            powerSources = target.doScan()
                        elif action == "rootkit":
                            powerSources = target.doRootkit()
                        elif action == "portscan":
                            powerSources = target.doPortScan()
                        elif action == "ips":
                            target.doIPS()
                        else:
                            actionResult["message"] = "Invalid action type."
                    else:
                        actionResult["message"] = "Invalid node."
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

        # Commit turn results (e.g. DDoSes)
        self.map.resetAfterTurn()

        # Determine winner if appropriate
        done = self.totalTurns > 0 and self.totalTurns <= self.turnsExecuted
        if done:

            # Determine total power amounts
            totalPowerAmounts = {}
            for playerId in self.playerInfos:
                totalPowerAmounts[playerId] = sum([x.totalPower for x in self.map.getPlayerNodes(playerId)])

            # Send results to players
            for result in self.turnResults.values():
                result.append({"totalPowerAmounts": totalPowerAmounts, "status": "gameOver"})

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
