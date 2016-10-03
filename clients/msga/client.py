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
teamName = "msga"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "FinalBrian",
                 "ClassId": "Assassin"},
                {"CharacterName": "FinalDuke",
                 "ClassId": "Assassin"},
                {"CharacterName": "FinalYash",
                 "ClassId": "Assassin"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    actions = []
    myteam = []
    enemyteam = []
    turn_count = serverResponse["TurnNumber"]
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

    am = []
    priority = {
        "Assassin" : 8,
        "Archer": 7,
        "Warrior": 6,
        "Sorcerer": 5, 
        "Wizard": 4,
        "Enchanter": 3,
        "Paladin": 2,
        "Druid": 1
    }
    burst = 0
    backstab = 11
    sprint = 12
    # Choose a better target
    enemytotalhealth = {x.id:x.attributes.get_attribute("Health") for x in enemyteam}
    target = max(enemyteam, key=lambda e: (not e.is_dead())*priority[e.classId])
    #print target.classId
    for character in myteam:
        if not character.is_dead():
            #print character.classId, 'not dead'
            if character.attributes.get_attribute("stunned"):
                #print 'stunned'
                actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": burst
                        })
            elif not character.in_range_of(target, gameMap) and turn_count < 3 and character.can_use_ability(sprint):
                #print 'sprint'
                actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": sprint
                        })
            elif not character.in_range_of(target, gameMap):
                actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
            elif character.can_use_ability(backstab) and enemytotalhealth[target.id] + target.attributes.get_attribute("Armor") > 110:
                #print 'backstab'
                enemytotalhealth[target.id] -= 200
                actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                            "AbilityId": backstab
                        })
            elif enemytotalhealth[target.id] < 0:
                if enemytotalhealth[target.id] < 0:
                    enemyteam.remove(target)
                    target = enemyteam[0]
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
            else:
                #print 'attack'
                enemytotalhealth[target.id] -= 110 - target.attributes.get_attribute("Armor")
                actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id
                        })
    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }


    # # Choose a target
    # target = None
    # for character in enemyteam:
    #     if not character.is_dead():
    #         target = character
    #         break
            
    # # If we found a target
    # if target:
    #     for character in myteam:
    #         # If I am in range, either move towards target
    #         if character.in_range_of(target, gameMap):
    #             # Am I already trying to cast something?
    #             if character.casting is None:
    #                 cast = False
    #                 for abilityId, cooldown in character.abilities.items():
    #                     # Do I have an ability not on cooldown
    #                     if cooldown == 0:
    #                         # If I can, then cast it
    #                         ability = game_consts.abilitiesList[int(abilityId)]
    #                         # Get ability
    #                         actions.append({
    #                             "Action": "Cast",
    #                             "CharacterId": character.id,
    #                             # Am I buffing or debuffing? If buffing, target myself
    #                             "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
    #                             "AbilityId": int(abilityId)
    #                         })
    #                         cast = True
    #                         break
    #                 # Was I able to cast something? Either wise attack
    #                 if not cast:
    #                     actions.append({
    #                         "Action": "Attack",
    #                         "CharacterId": character.id,
    #                         "TargetId": target.id,
    #                     })
    #         else: # Not in range, move towards
    #             actions.append({
    #                 "Action": "Move",
    #                 "CharacterId": character.id,
    #                 "TargetId": target.id,
    #             })

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
