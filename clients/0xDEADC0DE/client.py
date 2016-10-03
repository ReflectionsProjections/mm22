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
turn = 0
move = 0
good = None
stun = [-9,-9,-9,-9,-9,-9,-9]

# --------------------------- SET THIS IS UP -------------------------
teamName = "0xDEADC0DE"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "0xA55",
                 "ClassId": "Warrior"},
                {"CharacterName": "0x5A55",
                 "ClassId": "Warrior"},
                {"CharacterName": "0x14",
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
                if not character.is_dead():
                    myteam.append(character)
        else:
            for characterJson in team["Characters"]:
                character = Character()
                character.serialize(characterJson)
                enemyteam.append(character)
# ------------------ You shouldn't change above but you can ---------------

    global turn
    global stun
    global good
    global move
    turn = turn+1
    if turn == 1:
        for character in myteam:
            pos = character.position
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "Location": (0,1) if pos[0]<3 else (4,3)
            })
        return {
            'TeamName': teamName,
            'Actions': actions
        }
    if turn == 2:
        for character in myteam:
            pos = character.position
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "Location": (0,2) if pos[0]<3 else (4,2)
            })
        return {
            'TeamName': teamName,
            'Actions': actions
        }
    if turn == 3:
        for character in myteam:
            pos = character.position
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "Location": (0,3) if pos[0]<3 else (4,1)
            })
        return {
            'TeamName': teamName,
            'Actions': actions
        }

    # Choose a target
    targets = []
    for character in enemyteam:
        if not character.is_dead():
            targets.append(character)
            
    for character in myteam:
        pos = character.position
        if character.attributes.get_attribute("Stunned"):
            if (character.can_use_ability(0)):
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": character.id,
                    "AbilityId": 0
                })
            continue
        if character.can_use_ability(1):
            able = []
            for target in targets:
                if character.in_range_of(target, gameMap) and turn - stun[target.id]>2:
                    done = False
                    for act in actions:
                        if act["Action"] is "Cast" and act["AbilityId"] == 1 and act["TargetId"] == target.id:
                            done = True
                    for buff in target.debuffs:
                        if buff["Attribute"] is "Stunned":
                            done = True
                    if not done:
                        able.append(target)

            if able:
                target = min(able,key=lambda p: p.attributes.get_attribute("Health"))
                stun[target.id] = turn;
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": target.id, 
                    "AbilityId": 1
                })
                continue
        if character.abilities[1] < 2 and character.can_use_ability(0) and character.attributes.get_attribute("Slienced"):
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 0
            })
            continue
        able = []
        for target in targets:
            if character.in_range_of(target, gameMap):
                dam = target.attributes.get_attribute("Health")
                for act in actions:
                    if act["Action"] is "Attack" and act["TargetId"] == target.id:
                        dam = dam - 75 + target.attributes.get_attribute("Armor")
                if dam>0:
                    able.append(target)
        if able:
            target = min(able,key=lambda p: p.attributes.get_attribute("Health"))
            actions.append({
                "Action": "Attack",
                "CharacterId": character.id,
                "TargetId": target.id 
            })
            continue
        if (character.can_use_ability(0) and (character.attributes.get_attribute("Rooted") or
            character.attributes.get_attribute("Slienced"))):
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 0
            })
            continue
        if character.attributes.get_attribute("Rooted"):
            continue
        shortest = 10
        shortTarget = None
        for target in targets:
            dist = len(gameMap.bfs(character.position, target.position))
            if dist < shortest:
                shortest = dist
                shortTarget = target
        move = move + 1
        if(move == 10):
          badId = shortTarget.id
          if(len(targets)>1):
              for target in targets:
                  if(target.id != badId):
                      good = target
        finId = shortTarget.id if good == None else good.id
        actions.append({
            "Action": "Move",
            "CharacterId": character.id,
            "TargetId": finId
        })

    #nd actions to the server
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
