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
teamName = "SevenNationArmy"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "BestGirl",
                 "ClassId": "Enchanter"},
                {"CharacterName": "Sterling",
                 "ClassId": "Archer"},
                {"CharacterName": "Hanzo",
                 "ClassId": "Archer"},
            ]}
# -------------------------------------:--------------------------------

killPriority = ["Wizard", "Druid", "Enchanter", "Sorcerer", "Assassin", "Archer", "Warrior", "Paladin"]
midCastValues = {3:3, 10:3, 16:2, 15:1, 7:2}
availableValues = {1:1, 2:0, 3:2, 4:1, 5:1.5, 6:0, 7:1, 8:0, 9:1.5, 10:2, 11:1.5, 12:.5, 13:1, 14:1, 15:1, 16:1}


def inRangeOfWho(character, enemyteam):
    ret = []
    for e in enemyteam:
        if e.in_range_of(character, gameMap):
            ret.append(e)
    return ret

def killPriorities(enemyteam):
    ret = []
    for kp in killPriority:
        for e in enemyteam:
            if e.classId == kp and not e.is_dead():
                ret.append(e)
    return ret

def getArchers(myteam):
    ret = []
    for c in myteam:
        if c.classId == "Archer" and not c.is_dead():
            ret.append(c)
    return ret

def getEnchanters(myteam):
    ret = []
    for c in myteam:
        if c.classId == "Enchanter" and not c.is_dead():
            ret.append(c) 
    return ret

def castingTargets(enemyTeam):
    ret = []
    for e in enemyTeam:
        if e.casting is not None:
            ret.append(e)
    return ret

def cooldownTargets(enemyTeam):
    ret = []
    for e in enemyTeam:
        for ability, _ in e.abilities.items():
            if e.abilities[ability] == 1:
                ret.append((e,ability))
                continue
    return ret

def silenceTarget(enchanter, enemyTeam):
    inRange = []
    for enemy in enemyTeam:
        if enchanter.in_range_of(enemy, gameMap):
            inRange.append(enemy)
    casting = castingTargets(inRange)
    for i in casting:
        if i.classId in ["Wizard", "Sorcerer", "Druid", "Paladin"]:
            return i
    cooldown = cooldownTargets(inRange)
    for k in [11, 5, 3, 9, 14]:
        for (i, j) in cooldown:
            if j ==k:
                return i
    return None

def safetySquares(enemyTeam):
    positions = []
    for e in enemyTeam:
        if not e.is_dead():
            positions.append(e.position)
    safety = {}
    for i in range(5):
        for j in range(5):
            if not gameMap.is_inbounds((i,j)):
                safety[(i,j)] = 0
            else:
                total = 0
                for (k,l) in positions:
                    total = abs(l-j)+abs(k-i)
                safety[(i,j)] = total
    return safety

def bestMove(enchanter, enemyTeam):
    safety = safetySquares(enemyTeam)
    pos = enchanter.position
    bestSafety = 0
    bestPos = pos
    for i in [(-1,0),(1,0),(0,1),(0,-1),(0,0)]:
        newPos = (pos[0]-i[0], pos[1] -i[1])
        if gameMap.is_inbounds(newPos):
            if safety[newPos] > bestSafety:
                bestSafety = safety[newPos]
                bestPos = newPos
    return bestPos


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

    kp = killPriorities(enemyteam)
    if(len(kp)==0):
        return {
        'TeamName': teamName,
        'Actions': actions
    }
    target = kp[0]
    archers = getArchers(myteam)
    bothArchersInRange = 0
    for archer in archers:
        if archer.in_range_of(target, gameMap):
            bothArchersInRange+=1
    #chase down and kill
    for archer in archers:
        # Burst if stunned, or do nothing
        if archer.attributes.get_attribute("Stunned"):
            if archer.can_use_ability(0):
                actions.append({"Action": "Cast", "CharacterId": archer.id, "TargetId": archer.id, "AbilityId":0})
            else:
                continue
        # Pierce armor if archers are set up
        elif bothArchersInRange >= 2 and archer.can_use_ability(2):
            actions.append({"Action": "Cast", "CharacterId": archer.id, "TargetId": target.id, "AbilityId":2})
        # Attack if target in range
        elif archer.in_range_of(target, gameMap):
            actions.append({"Action": "Attack", "CharacterId": archer.id, "TargetId": target.id})
        # Get to target
        else:
            # Burst if rooted and you want to move
            if archer.attributes.get_attribute("Rooted") and archer.can_use_ability(0):
                actions.append({"Action": "Cast", "CharacterId": archer.id, "TargetId": archer.id, "AbilityId":0})
            # If no one in range and not on an odd tile, sprint
            elif archer.can_use_ability(12) and archer.position[0]%2== 0 and archer.position[1]%2==0 and len(inRangeOfWho(archer, enemyteam))==0:
                actions.append({"Action": "Cast", "CharacterId": archer.id, "TargetId": archer.id, "AbilityId":12})
            # move towards target if you can
            elif not archer.attributes.get_attribute("Rooted"):
                actions.append({"Action": "Move", "CharacterId": archer.id, "TargetId": target.id})
            # otherwise, just attack someone in range
            else:
                target2 = None
                for i in range(1,len(kp)):
                    if archer.in_range_of(kp[i], gameMap):
                        target2 = kp[i]
                        break
                if target2 != None:
                    actions.append({"Action": "Attack", "CharacterId": archer.id, "TargetId": target2.id})

    # enchanter
    enchanters = getEnchanters(myteam)
    if enchanters != []:
        sTarget = silenceTarget(enchanters[0], enemyteam)
    for enchanter in enchanters:
        if enchanter.attributes.get_attribute("Silenced") and enchanter.can_use_ability(0):
            actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": enchanter.id, "AbilityId":0})
            continue
        if enchanter.attributes.get_attribute("Stunned"):
            if enchanter.can_use_ability(0):
                actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": enchanter.id, "AbilityId":0})
            else:
                continue
        elif len(archers) == 0:
            if not enchanter.attributes.get_attribute("Rooted"):
                actions.append({"Action": "Move", "CharacterId": enchanter.id, "Location":bestMove(enchanter,enemyteam)})
            elif enchanter.attributes.get_attribute("Rooted") and enchanter.can_use_ability(0):
                actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": enchanter.id, "AbilityId":0})
            else:
                for i in kp:
                    if enchanter.in_range_of(i, gameMap):
                        actions.append({"Action": "Attack", "CharacterId": enchanter.id, "TargetId": i.id})
        elif silenceTarget(enchanter, enemyteam) is not None and enchanter.can_use_ability(5):
            actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": sTarget.id, "AbilityId":5})
        elif bothArchersInRange >= 2 and enchanter.can_use_ability(6) and enchanter.in_range_of(target, gameMap):
            actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": target.id, "AbilityId":2})
        elif enchanter.attributes.get_attribute("Health") < 250:
            if not enchanter.attributes.get_attribute("Rooted"):
                actions.append({"Action": "Move", "CharacterId": enchanter.id, "Location":bestMove(enchanter,enemyteam)})
            elif enchanter.attributes.get_attribute("Rooted") and enchanter.can_use_ability(0):
                actions.append({"Action": "Cast", "CharacterId": enchanter.id, "TargetId": enchanter.id, "AbilityId":0})
            else:
                for i in kp:
                    if enchanter.in_range_of(i, gameMap):
                        actions.append({"Action": "Attack", "CharacterId": enchanter.id, "TargetId": i.id})
        elif not enchanter.in_range_of(target, gameMap) and not enchanter.attributes.get_attribute("Rooted"):
            actions.append({"Action": "Move", "CharacterId": enchanter.id, "TargetId": target.id})
        else:
            for i in kp:
                if enchanter.in_range_of(i, gameMap):
                    actions.append({"Action": "Attack", "CharacterId": enchanter.id, "TargetId": i.id})





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
