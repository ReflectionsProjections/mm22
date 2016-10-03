#!/usr/bin/python2
import socket
import json
import os
import random
import sys
import math
from socket import error as SocketError
import errno
sys.path.append("../..")
import src.game.game_constants as game_consts
from src.game.character import *
from src.game.gamemap import *

# Game map that you can use to query 
gameMap = GameMap()

# --------------------------- SET THIS IS UP -------------------------
teamName = "OrbitalYak"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "MDPS0",
                 "ClassId": "Archer"},
                {"CharacterName": "MDPS1",
                 "ClassId": "Archer"},
                {"CharacterName": "MDPS2",
                 "ClassId": "Archer"},
            ]}
# ---------------------------------------------------------------------


def maxDistFromEnemy(targets):
    global onBottom
    global reachedBR
    print("Bottom Start " + str(onBottom))
    print("Reached BR " + str(reachedBR))
    if onBottom or reachedBR:
        maxDist = 0
        pos = [0,0]
        for i in range(gameMap.width):
            for j in range(gameMap.height):
                min = 9999999999
                for enemy in targets:
                    dist = math.fabs((i-enemy.position[0]))+math.fabs((j-enemy.position[1]))
                    if dist<min:
                        min = dist
                if maxDist < min:
                    maxDist = min
                    pos = [i,j]
        return pos
    else:
        return (4,4)

def minDistToEnemy(character, targets):
    i = character.position[0]
    j = character.position[1]
    min = 9999999
    for enemy in targets:
                dist = math.fabs((i-enemy.position[0]))+math.fabs((j-enemy.position[1]))
                if dist<min:
                    min = dist
    return min

def getCharByName(charName,team):
    for character in team:
        if character.name == charName:
            return character
    print "Character with given name does not exist"
    return None

def moveToPosition(charId, targetPos):
    return {"Action": "Move",
            "CharacterId": charId,
            "Location": targetPos, }

def spell(charId, targetId, spellId):
    return {"Action": "Cast",
            "CharacterId": charId,
            "TargetId": targetId,
            "AbilityId": spellId, }

def moveToEnemy(charId, targetId):
    return {"Action": "Move",
            "CharacterId": charId,
            "TargetId": targetId, }

def attack(charId, targetId):
    return {"Action": "Attack",
            "CharacterId": charId,
            "TargetId": targetId }

# Determine actions to take on a given turn, given the server response

turn = -1
onBottom = True
reachedBR = False

def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    global onBottom
    global turn
    global reachedBR
    turn = turn+1
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

    if turn == 0 and myteam[0].position[0] < 2:
        onBottom = False
    for char in myteam:
        if char.position[0] == 4 and char.position[1]==4:
            reachedBR=True
    for char in myteam:
        if char.position[0] == 0 and char.position[1]==0:
            reachedBR=False
    if turn==0 and onBottom:
        0

    print(onBottom)
    # Choose a target
    target = None
    targets = []
    maxDmg = -1
    for character in enemyteam:
        if not character.is_dead():
            targets.append(character)
            if not character.is_dead() and character.attributes.damage>maxDmg and myteam[0].in_ability_range_of(character,gameMap,11):
                maxDmg = character.attributes.damage
                target = character

    if not target:
        target=targets[0]
    # If we found a target
    if target:
        allowedToKite = True
        avgR = 0.0
        for enemy in enemyteam:
            avgR = enemy.attributes.attackRange+avgR
            avgR = 2*int(enemy.can_use_ability(1) or enemy.can_use_ability(9) or enemy.can_use_ability(14))+avgR

        for character in myteam:
            avgR = avgR+0.3*int(character.attributes.stunned==-1)

        avgR = avgR/len(enemyteam)
        if(avgR > 1.5):
            print("Kiting disabled, AKM " + str(avgR))
            
        else:
            print("Kiting enabled, AKM " + str(avgR))

        for character in myteam:
            if character.attributes.stunned == -1 and character.can_use_ability(0):
                print(character.name + " is stunned.  Attempting to breakout.")
                actions.append(spell(character.id, character.id, 0))
                continue
            elif not character.can_use_ability(0):
                print(character.name + " is stunned but cannot escape.")
                continue
            if minDistToEnemy(character, targets)<=1:
                print(character.name + " is kiting, as enemies are in "+str(minDistToEnemy(character, targets)))
                actions.append(moveToPosition(character.id, maxDistFromEnemy(targets)))
                continue
            elif minDistToEnemy(character, targets)<=3 and character.can_use_ability(12):
                    print(character.name + " is boosting in preparation to kite, as enemies are in "+str(minDistToEnemy(character, targets)))
                    actions.append(spell(character.id, character.id, 12))
                    continue
            else:
                    actions.append(attack(character.id,target.id))
                    print(character.name + " is waiting. Enemies are at distance "+str(minDistToEnemy(character, targets))+ ", boost is "+str(character.can_use_ability(12))+", and backstab is "+str(character.can_use_ability(11)))
        
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

