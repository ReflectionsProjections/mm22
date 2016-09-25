#!/usr/bin/python2
import socket
import json
import os
import random
import sys
from socket import error as SocketError
import errno
sys.path.append("../..")
from src.game.character import *
from src.game.gamemap import *

gameMap = GameMap()

# Set initial connection data
def initialResponse():
    # @competitors YOUR CODE HERE
    return {'TeamName':'Test',
            'Characters': [
                {"CharacterName": "Druid",
                 "ClassId": "Druid"},
                {"CharacterName": "Archer",
                 "ClassId": "Archer"},
                {"CharacterName": "Wizard",
                 "ClassId": "Wizard"},
            ]}

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    actions = []
    myId = serverResponse["PlayerInfo"]["Id"]
    myteam = []
    enemyteam = []
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

    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
    if target:
        for character in myteam:
            try:
                # Check if character is in range, throw exception if not
                character.in_range_of(target, gameMap)

                actions.append({
                    "Action": "Attack",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })
            except OutOfRangeException as e:
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })

    # Send actions to the server
    return {
        'TeamName': 'Test',
        'Actions': actions
    }

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
