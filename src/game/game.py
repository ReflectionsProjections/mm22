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
        except KeyError as e:
            error = "json response doesn't have the correct format"

        # If there is an error, return false and error
        if error:
            return False, error

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

        action_priority_order = ["attack", "cast", "move"]

        # Clear Turn results
        self.turnResults = {}
        for playerId in self.queuedTurns:
            self.turnResults[playerId] = []

        # Execute turns
        for action_type in action_priority_order:
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
                for actionJson in actions:
                    action = actionJson.get("action", "").lower()

                    if action != action_type:
                        continue

                    teamId = self.playerInfos[playerId]["teamId"]
                    characterId = actionJson.get("characterId", None)
                    targetId = actionJson.get("targetId", None)
                    location = actionJson.get("location", None)
                    abilityId = actionJson.get("abilityId", None)

                    actionResult = {"teamId": playerId, "action": action, "target": targetId}

                    try:
                        # Get player character object
                        if characterId:
                            character = self.teams[teamId].get_character(id=characterId)
                        else:
                            actionResult["message"] = "Invalid characterId: could not find characterId in json"
                            continue

                        # Did we find the character?
                        if not character:
                            actionResult["message"] = "Invalid characterId: could not find character on your team"
                            continue

                        # Is character dead?
                        if character.dead:
                            actionResult["message"] = "Invalid character: Character is dead"

                        # Get target character object
                        target = None
                        if targetId:
                            for teamId, team in self.teams.items():
                                target = team.get_character(id=targetId)
                                if target:
                                    break
                            if not target:
                                actionResult["message"] = "Unable to find target"
                                continue
                            if target.dead:
                                actionResult["message"] = "Invalid target: target is dead"
                                continue

                        if action == "move":
                            if target:
                                ret = character.move_towards(target, self.map)
                                if ret is not None:
                                    actionResult["message"] = "Unable to move Character-" + str(characterId) + ": " + ret
                            elif location:
                                ret = character.move_to(location, self.map)
                                if ret is not None:
                                    actionResult["message"] = "Unable to move Character-" + str(characterId) + ": " + ret
                            else:
                                actionResult["message"] = "Invalid target and couldn't find location"
                        elif action == "attack":
                            if character == target or target is None:
                                actionResult["message"] = "Invalid target to attack"
                                continue

                            if self.map.in_vision_of((character.posX, character.posY),
                                                     (target.posX, target.posY),
                                                     character.attributes.get_attribute("AttackRange")):
                                target.add_stat_change({
                                    "Target": 1,
                                    "Attribute": "Health",
                                    "Change": -1 * character.attributes.get_attribute("Damage"),
                                    "Time": 0
                                })
                            else:
                                actionResult["message"] = "Target is out of range or not in vision"
                        elif action == "cast":
                            if target is None:
                                actionResult["message"] = "Invalid target to attack"
                                continue

                            if abilityId == -1:
                                actionResult["message"] = "Could not find ability id"
                                continue

                            if self.map.in_vision_of((character.posX, character.posY),
                                                     targetId,
                                                     character.attributes.get_attribute("AttackRange")):
                                if not character.use_ability(abilityId, target):
                                    actionResult["message"] = "Character does not have that ability!"
                            else:
                                actionResult["message"] = "Target is out of range or not in vision"
                        else:
                            actionResult["message"] = "Invalid action type."
                    except Exception as e:
                        raise  # Uncomment me to raise unhandled exceptions
                        actionResult["message"] = "Unknown exception: " + str(e)

                    actionResult["status"] = "fail" if "message" in actionResult else "ok"

                    # Record results
                    self.turnResults[playerId].append(actionResult)

        # Update everyone
        for teamId, team in self.teams.items():
            for character in team.characters:
                character.update()

        # Determine winner if appropriate
        alive_teams = []
        for teamId, team in self.teams.items():
            alive_team = False
            for character in team.characters:
                if not character.dead:
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
            "teams": [team.toJson() for teamId, team in self.teams.items()]
        }

    # Return the entire state of the map
    def get_all_info(self):
        return {
            "playerInfos": self.playerInfos,
            "turnResults": [self.turnResults.get(pId, [{"status": "fail", "message": "No turn executed."}]) for pId in self.playerInfos],
            "teams": [team.toJson() for teamId, team in self.teams.items()]
        }
