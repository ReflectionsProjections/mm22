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
teamName = "RATZ"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    # global variable for turn counter
    global turnNumber
    turnNumber = 0
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Zac",
                 "ClassId": "Archer"},
                {"CharacterName": "TJ",
                 "ClassId": "Archer"},
                {"CharacterName": "Ray",
                 "ClassId": "Druid"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
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

    makeDecisions(actions, myteam, enemyteam)
    global turnNumber
    turnNumber += 1

    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }

# --------------------------- CHANGE THIS SECTION -------------------------
# All the decision making code.
def makeDecisions(actions, myteam, enemyteam):
    global castingRoot
    castingRoot = False
    # Druid decides first
    for character in myteam:
        if character.classId == "Druid":
            characterDecision(character, actions, myteam, enemyteam)
    # Then everyone else decides
    for character in myteam:
        if character.classId != "Druid":
            characterDecision(character, actions, myteam, enemyteam)
    
# The decision making process for each character
def characterDecision(character, actions, myteam, enemyteam):
    # if stunned and burst is off cooldown, use burst
    if character.attributes.stunned and character.can_use_ability(0):
        addCast(actions, character, character, 0)
        return
    
    if character.classId == "Druid":
        druidDecision(character, actions, myteam, enemyteam)
        
    elif character.classId == "Archer":
        archerDecision(character, actions, myteam, enemyteam)

def druidDecision(character, actions, myteam, enemyteam):
    if character.casting:
        # check if the intended target is still alive
        target = getById(character.casting["TargetId"], myteam, enemyteam)
        if not target.is_dead():
            return
    
    # if heal is off cooldown, use it on an ally
    if character.can_use_ability(3) and turnNumber <= 120:
        # heal target selection
        target = getLowestHealthExcludeSelf(character, myteam)
        if target and target.attributes.get_attribute("Health") < game_consts.classesJson["Archer"]["Health"]:
            if character.in_ability_range_of(target, gameMap, 3):
                addCast(actions, character, target, 3)
                return
            else:
                addMoveTarget(actions, character, target)
                return
    # use armor buff if off cooldown and allies are still alive to attack
    if character.can_use_ability(4) and inCombat(character, enemyteam):
        receiver = getLowestHealthInAbilityRange(character, myteam, 4)
        if receiver:
            addCast(actions, character, receiver, 4)
            return
    
    #if you are surrounded by the enemy, dont bother roooting
    if getBackUpLocation(character, enemyteam, actions, myteam):
        # use root if enemy is an Assassin
        for enemy in enemyteam:
            if character.can_use_ability(13) and character.in_ability_range_of(enemy, gameMap, 13) and not enemy.is_dead() and enemy.classId == "Assassin":
                global castingRoot
                castingRoot = True
                addCast(actions, character, enemy, 13)
                return
    
        
    # if below 50% health and healing is on and heal is off cooldown, heal self
    if character.can_use_ability(3) and turnNumber <= 120 and character.attributes.get_attribute("Health") < game_consts.classesJson["Druid"]["Health"]/2:
        addCast(actions, character, character, 3)
        return
    
    # otherwise, attack if enemy is within range
    if attack(character, actions, enemyteam):
        return
        
    # if no enemies in range, heal self if off cooldown and healing is on
    if character.can_use_ability(3) and turnNumber <= 120 and character.attributes.get_attribute("Health") < game_consts.classesJson["Druid"]["Health"]:
        addCast(actions, character, character, 3)
        return
    
    # if unable to do anything, move towards enemy if not turn 2
    target = getLowestHealth(enemyteam)
    if target and turnNumber != 2:
        addMoveTarget(actions, character, target)
        return
    
def archerDecision(character, actions, myteam, enemyteam):
    # If the Druid is casting root, try to back up
    if castingRoot:
        location = getBackUpLocation(character, actions, myteam, enemyteam)
        if location:
            addMoveLocation(actions, character, location)
            return
    
    # if enemy is within range, attack 
    if attack(character, actions, enemyteam):
        return
        
    # if none in range, move towards enemy unless it is turn 2
    target = getLowestHealth(enemyteam)
    if target and turnNumber != 2:
        addMoveTarget(actions, character, target)
        return
# if there is an adjacent cell nearby with no enemy in it, return that cell
def getBackUpLocation(character, actions, myteam, enemyteam):
    neighboringPositions = gameMap.get_valid_adjacent_pos(character.position)
    
    enemyPositions = []
    for enemy in enemyteam:
        if enemy.position not in enemyPositions:
            enemyPositions.append(enemy.position)
            
    for cell in neighboringPositions:
        if cell not in enemyPositions:
            return cell

# checks if in combat, i.e. if any enemies are in attack range

def getSurroundingPoints(point):
    pass

def inCombat(character, enemyteam):
    for enemy in enemyteam:
        if character.in_range_of(enemy, gameMap):
            return True
    return False

# attacks the enemy with the lowest health if possible
def attack(character, actions, enemyteam):
    target = getLowestHealthInRange(character, enemyteam)
    if target:
        addAttack(actions, character, target)
        return True
    return False

# Gets the lowest health character from a list
def getLowestHealth(team):
    lowestCharacter = None
    lowestHealth = 9999
    for char in team:
        if not char.is_dead() and char.attributes.get_attribute("Health") < lowestHealth:
            lowestCharacter = char
            lowestHealth = char.attributes.get_attribute("Health")
    return lowestCharacter

# Gets the lowest health character from a list excluding a given character
def getLowestHealthExcludeSelf(character, team):
    lowestCharacter = None
    lowestHealth = 9999
    for char in team:
        if not char.is_dead() and char.attributes.get_attribute("Health") < lowestHealth and char != character:
            lowestCharacter = char
            lowestHealth = char.attributes.get_attribute("Health")
    return lowestCharacter

# Gets the lowest health character in attack range of a given attacker
def getLowestHealthInRange(character, team):
    lowestCharacter = None
    lowestHealth = 9999
    for char in team:
        if not char.is_dead() and char.attributes.get_attribute("Health") < lowestHealth and character.in_range_of(char, gameMap):
            lowestCharacter = char
            lowestHealth = char.attributes.get_attribute("Health")
    return lowestCharacter

# Gets the lowest health character in cast range of a given caster and ability
def getLowestHealthInAbilityRange(character, team, abilityId):
    lowestCharacter = None
    lowestHealth = 9999
    for char in team:
        if not char.is_dead() and char.attributes.get_attribute("Health") < lowestHealth and character.in_ability_range_of(char, gameMap, abilityId):
            lowestCharacter = char
            lowestHealth = char.attributes.get_attribute("Health")
    return lowestCharacter

# Gets a character object by its ID
def getById(characterId, myteam, enemyteam):
    for ally in myteam:
        if ally.id == characterId:
            return ally
    for enemy in enemyteam:
        if enemy.id == characterId:
            return enemy

# Adds a move action with a location to the actions list
def addMoveLocation(actions, character, location):
    actions.append({
        "Action": "Move",
        "CharacterId": character.id,
        "Location": location
    })

# Adds a move action with a target character to the actions list
def addMoveTarget(actions, character, target):
    actions.append({
        "Action": "Move",
        "CharacterId": character.id,
        "TargetId": target.id
    })
    
# Adds an attack action to the actions list
def addAttack(actions, character, target):
    actions.append({
        "Action": "Attack",
        "CharacterId": character.id,
        "TargetId": target.id
    })
    
# Adds a cast action to the actions list
def addCast(actions, character, target, abilityId):
    actions.append({
        "Action": "Cast",
        "CharacterId": character.id,
        "TargetId": target.id,
        "AbilityId": int(abilityId)
    })

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
