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
teamName = "coffe"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Folgers",
                 "ClassId": "Assassin"},
                {"CharacterName": "Storbucks",
                 "ClassId": "Assassin"},
                {"CharacterName": "Caribo",
                 "ClassId": "Assassin"},
            ]}
# ---------------------------------------------------------------------

gs = {}
gs["stage"] = 0

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    global gs
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

    for character in myteam:
        cast = False
        targets = []
        for enemy in enemyteam:
            if character.in_range_of(enemy, gameMap) and not enemy.is_dead():
                targets.append(enemy)
        targets = sorted(targets, key=lambda x: (x.attributes.armor, x.attributes.health))

        if len(targets) > 0 and character.in_range_of(targets[0], gameMap):
            # Was I able to cast something? Either wise attack
            cast = False
            for abilityId, cooldown in character.abilities.items():
                if abilityId is 11 and cooldown is 0 and character.in_ability_range_of(targets[0], gameMap, 11):
                    print("Backstab!")
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": targets[0].id,
                        "AbilityId": 11
                    })
                    cast = True
                    break
            if not cast:
                actions.append({
                    "Action": "Attack",
                    "CharacterId": character.id,
                    "TargetId": targets[0].id,
                })
        else: # Not in range, move towards
            cast = False
            if serverResponse["TurnNumber"] > 4:
                for abilityId, cooldown in character.abilities.items():
                    if not character.attributes.movementSpeed is 2 and abilityId is 12 and cooldown is 0:
                        actions.append({
                            "Action": "Cast",
                            "TargetId": character.id,
                            "CharacterId": character.id,
                            "AbilityId": 12
                        })
                        cast = True
                        break
            if not cast:
                non_dead = [ enemy for enemy in enemyteam if not enemy.is_dead() ]
                if len(non_dead):
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": non_dead[0].id
                    })

    print(actions)
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
