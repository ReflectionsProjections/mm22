#!/usr/bin/python2
import socket
import json
import os
import random
import sys
from socket import error as SocketError
import errno
sys.path.append("../..")
import src.game.game_constants as game_consts
from src.game.character import *
from src.game.gamemap import *

# Game map that you can use to query 
gameMap = GameMap()

# --------------------------- SET THIS IS UP -------------------------
teamName = "gtk"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Paladin",
                 "ClassId": "Paladin"},
                {"CharacterName": "Druid",
                 "ClassId": "Druid"},
                {"CharacterName": "Warrior",
                 "ClassId": "Warrior"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    actions = []
    myteam = []
    enemyteam = []
    # Find each team and serialize the objects
    for team in serverResponse["Teams"]:
        if team["Id"] == serverResponse["PlayerInfo"]["TeamId"]:
            for characterJson in team["Characters"]:
                character = Character()
                character.serialize(characterJson)
                myteam.append(character)
        else:
            for characterJson in team["Characters"]:
                character = Character()
                character.serialize(characterJson)
                enemyteam.append(character)
# ------------------ You shouldn't change above but you can ---------------

    # Choose a target
    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
            break

    # If we found a target
    if target:

        for character in myteam:
            # If I am in range, either move towards target
            if character.in_range_of(target, gameMap):
                if character.name == "Druid":
                    if character.casting is None:
                        cast = False
                        if (character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Silenced") or character.attributes.get_attribute("Rooted")) and character.can_use_ability(0):
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character.id,
                                    "AbilityId": int(0)
                                })
                                cast = True
                                break
                        if character.can_use_ability(3):
                            for character1 in myteam:

                              if character1.attributes.get_attribute("Health") < 800 and not character1.is_dead():
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character1.id,
                                    "AbilityId": int(3)
                                })

                                cast = True
                                break

                        if character.can_use_ability(4):
                            for character1 in myteam:
                                if character1.attributes.get_attribute("Health") < 800 and not character1.is_dead():
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": character1.id,
                                        "AbilityId": int(4)
                                    })
                                    cast = True
                                    break

                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })

                if character.name == "Assassin":
                    if character.casting is None:
                        cast = False
                        if (character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Silenced") or character.attributes.get_attribute("Rooted")) and character.can_use_ability(0):
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character.id,
                                    "AbilityId": int(0)
                                })
                                cast = True
                                break
                        if character.can_use_ability(11):

                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": target.id,
                                    "AbilityId": int(11)
                                })
                                cast = True
                                break

                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                if character.name == "Warrior":
                    if character.casting is None:
                        cast = False
                        if (character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Silenced") or character.attributes.get_attribute("Rooted")) and character.can_use_ability(0):
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character.id,
                                    "AbilityId": int(0)
                                })
                                cast = True
                                break
                        if character.can_use_ability(1):

                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": target.id,
                                    "AbilityId": int(1)
                                })
                                cast = True
                                break
                        if character.can_use_ability(15):

                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": character.id,
                                    "AbilityId": int(15)
                                })
                                cast = True
                                break

                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                #
                if character.name == "Archer":
                    if character.casting is None:
                        cast = False
                        if (character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Silenced") or character.attributes.get_attribute("Rooted")) and character.can_use_ability(0):
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character.id,
                                    "AbilityId": int(0)
                                })
                                cast = True
                                break
                        if character.can_use_ability(2):

                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": target.id,
                                    "AbilityId": int(2)
                                })
                                cast = True
                                break

                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                if character.name == "Paladin":
                    if character.casting is None:
                       cast = False
                       if (character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Silenced") or character.attributes.get_attribute("Rooted")) and character.can_use_ability(0):
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": character.id,
                                    "AbilityId": int(0)
                                })
                                cast = True
                                break
                       if character.can_use_ability(3):
                            for character1 in myteam:
                              if character1.attributes.get_attribute("Health") <800 and not character1.is_dead():
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": character1.id,
                                    "AbilityId": int(3)
                                })

                                cast = True
                                break
                       if character.can_use_ability(14):

                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": target.id,
                                    "AbilityId": int(14)
                                })
                                cast = True
                                break


                       if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })

            else: # Not in range, move towards
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })

    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------

# Main method
# @competitors DO NOT MODIFY
if __name__ == "__main__":
    # Config
    conn = ('localhost', 1337)
    if len(sys.argv) > 2:
        conn = (sys.argv[1], int(sys.argv[2]))

    # Handshake
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(conn)

    # Initial connection
    s.sendall(json.dumps(initialResponse()) + '\n')

    # Initialize test client
    game_running = True
    members = None

    # Run game
    try:
        data = s.recv(1024)
        while len(data) > 0 and game_running:
            value = None
            if "\n" in data:
                data = data.split('\n')
                if len(data) > 1 and data[1] != "":
                    data = data[1]
                    data += s.recv(1024)
                else:
                    value = json.loads(data[0])

                    # Check game status
                    if 'winner' in value:
                        game_running = False

                    # Send next turn (if appropriate)
                    else:
                        msg = processTurn(value) if "PlayerInfo" in value else initialResponse()
                        s.sendall(json.dumps(msg) + '\n')
                        data = s.recv(1024)
            else:
                data += s.recv(1024)
    except SocketError as e:
        if e.errno != errno.ECONNRESET:
            raise  # Not error we are looking for
        pass  # Handle error here.
    s.close()
