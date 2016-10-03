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
import team_ai
import team_agent

# Game map that you can use to query 
gameMap = GameMap()


# --------------------------- SET THIS IS UP -------------------------
teamName = "wizardcats"
agents = [
    team_agent.Agent('Rebecca', 'Assassin', team_ai.assassin),
    team_agent.Agent('Eric', 'Assassin', team_ai.assassin),
    team_agent.Agent('Amanda', 'Assassin', team_ai.assassin)
]
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": agents[0].name,
                 "ClassId": agents[0].classId},
                {"CharacterName": agents[1].name,
                 "ClassId": agents[1].classId},
                {"CharacterName": agents[2].name,
                 "ClassId": agents[2].classId},
            ]}
# ---------------------------------------------------------------------

turnNum = 1
import pprint

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    global gameMap, turnNum
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
    gameState = team_agent.GameState(myteam, enemyteam, gameMap)
# ------------------ You shouldn't change above but you can ---------------
    
    for agent in agents:
        act = agent.getAction(gameState)
        actions.append(act)
        
    #print "On Turn " + str(turnNum)
    turnNum += 1
    #pprint.pprint(actions)

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
