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
teamName = "3Archer"
# ---------------------------------------------------------------------
turn = 0
guard = True
# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': '3Archers',
            'Characters': [
                {"CharacterName": "AD Archer1",
                 "ClassId": "Archer"},
                {"CharacterName": "AD Archer2",
                 "ClassId": "Archer"},
                {"CharacterName": "AD Archer3",
                 "ClassId": "Archer"},
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
    #TODO:moving forward only when ditance > 3 or Don't move OR move to (2,0) and wait until engage
    #TODO:When dealing with 0 attacking range enemy, move(sprint) and hit?
    #TODO:should I Flee with low blood?
    global turn
    turn +=1
    global guard
    if guard == True:
        for enemy in enemyteam:
            if myteam[0].in_range_of(enemy,gameMap):
                guard = False
    if turn > 20:
        guard = False
    if guard == True:
        return {
        'TeamName': teamName,
        'Actions': actions
        }  
    myLeft = 0
    enenyLeft = 0
    for character in myteam:
        if not character.is_dead():
            myLeft+=1
    # Choose a target
    # With Minimum Health
    # TODO select in range first ? (if target in range,that's fine, if not in range, select the one in range)
    # Done
    target = None
    secondTarget = None
    min_health = 2000 
    for character in enemyteam:
        health = character.attributes.health
        if not character.is_dead():
            enenyLeft+=1
            if target is None:
                target = character
                min_health = health
            elif not myteam[0].in_range_of(target, gameMap) and myteam[0].in_range_of(character,gameMap):
                secondTarget = target
                target = character
                min_health = health
            elif health <= min_health:
                secondTarget = target
                target  = character
                min_health = health

    # If we found a target
    if target:
        enemyRemainHealth = target.attributes.health
        for character in myteam:
            if character.is_dead():
                continue
            # If I am in range, either move towards target
            if character.in_range_of(target, gameMap):
                #if enemy is dead, change target
                if enemyRemainHealth <= 0:
                    target = secondTarget
                    if target is None:
                        break
                    enemyRemainHealth = target.attributes.health
                # Am I already trying to cast something?
                if character.casting is None:
                    cast = False
                    silenced =  False
                    for abilityId, cooldown in character.abilities.items():
                        # Do I have an ability not on cooldown
                        if cooldown == 0:
                            if abilityId == 0:
                                use_abili = False;
                                for debuff in character.debuffs:
                                    if debuff["Attribute"] == "Silenced":
                                        silenced = True
                                         
                                    if debuff["Attribute"] == "Stunned": 
                                    #if debuff["Attribute"] == "Stunned" or debuff["Attribute"] == "Silenced" or debuff["Attribute"] == "Rooted":
                                        use_abili = True
			             #if len(character.debuffs) == 0:#TODO:needs to be fixed for only three kind of debuffs (When to user burst)
				if silenced:
                                    cast = False
                                    break    
                                if not use_abili:
                                    continue
                            if abilityId == 12:#skip sprint now TODO:will sprint be better dealing with 0 range attack
                                continue
                            # If I can, then cast it
                            if abilityId == 2: #armor debuff, only cast when my team member are all alive TODO:is it necessary
                                if myLeft < 3:
                                    continue

                            ability = game_consts.abilitiesList[int(abilityId)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(abilityId)
                            })
                            cast = True
                            break
                    # Was I able to cast something? Either wise attack
                    if not cast:
                        actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
                        enemyRemainHealth -= (character.attributes.damage-target.attributes.armor)
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
