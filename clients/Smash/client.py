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
teamName = "Smash"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Gnarly",
                 "ClassId": "Warrior"},
                {"CharacterName": "Pmurder",
                 "ClassId": "Warrior"},
                {"CharacterName": "Jonny Boy",
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
            if character.deserialize()['ClassId'] == "Enchanter":
                target = character
                break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Assassin":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Archer":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Druid":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Sorcerer":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Paladin":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Wizard":
                    target = character
                    break
    if target == None:
        for character in enemyteam:
            if not character.is_dead():
                if character.deserialize()['ClassId'] == "Warrior":
                    target = character
                    break

    # If we found a target
    if target:
        stunning = []
        for character in myteam:
            possibleStun = False
            for play in enemyteam:
                if not play.is_dead():
                    if play not in stunning:
                        if play.attributes.stunned == 0:
                            possibleStun = True
            #if I am a paladin
            if character.deserialize()['ClassId'] == "Paladin":
                # If I am in range, either move towards target
                if character.in_range_of(target, gameMap):
                   # Am I already trying to cast something?
                    if character.casting is None:
                        cast = False
                        if (character.attributes.stunned < 0 or character.attributes.silenced != 0) and character.can_use_ability(0):
                            ability = game_consts.abilitiesList[int(0)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(0)
                            })
                            cast = True
                        elif character.can_use_ability(14) and possibleStun:
                            ability = game_consts.abilitiesList[int(14)]
                            # Get ability
                            enemy = target
                            if enemy in stunning:
                                for tar in enemyteam:
                                    if not tar.is_dead():
                                        if tar not in stunning:
                                            if character.in_range_of(tar, gameMap):
                                                if tar.attributes.stunned == 0:
                                                    enemy = tar
                            stunning.append(enemy)

                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": enemy.id,
                                "AbilityId": int(14)
                            })
                            cast = True
                        elif character.can_use_ability(3):
                            minHealth = 2000
                            healed = None
                            for chara in myteam:
                                if (not chara.is_dead()) and character.in_range_of(chara,
                                                                                   gameMap) and chara.attributes.health < chara.attributes.maxHealth:
                                    if chara.attributes.health < minHealth:
                                        healed = chara
                                        minHealth = chara.attributes.health
                            if healed != None:
                                cast = True
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": healed.id,
                                    "AbilityId": 3
                                })


                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                else:  # Not in range, move towards
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
            #For Warrior
            if character.deserialize()['ClassId'] == "Warrior":
                # If I am in range, either move towards target
                if character.in_range_of(target, gameMap):
                    # Am I already trying to cast something?
                    if character.casting is None:
                        cast = False
                        if (character.attributes.stunned < 0 or character.attributes.silenced != 0) and character.can_use_ability(0):
                            ability = game_consts.abilitiesList[int(0)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(0)
                            })
                            cast = True
                        elif character.can_use_ability(1) and possibleStun:
                            ability = game_consts.abilitiesList[int(1)]
                            enemy = target
                            if enemy in stunning:
                                for tar in enemyteam:
                                    if not tar.is_dead():
                                        if tar not in stunning:
                                            if character.in_range_of(tar, gameMap):
                                                if tar.attributes.stunned == 0:
                                                    enemy = tar
                            stunning.append(enemy)


                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": enemy.id,
                                "AbilityId": int(1)
                            })
                            cast = True
                        """elif character.attributes.health < 1000 and character.can_use_ability(15):
                            ability = game_consts.abilitiesList[int(15)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(15)
                            })
                            cast = True"""
                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                else:  # Not in range, move towards
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                        })
            #Assassin
            if character.deserialize()['ClassId'] == "Assassin":
                move = True
                # If I am in range, either move towards target
                if character.attributes.movementSpeed > 1:
                    if not character.in_range_of(target, gameMap):
                        move = False
                if character.in_range_of(target, gameMap) and move:
                    # Am I already trying to cast something?
                    if character.casting is None:
                        cast = False
                        if (character.attributes.stunned < 0 or character.attributes.silenced != 0) and character.can_use_ability(0):
                            ability = game_consts.abilitiesList[int(0)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(0)
                            })
                            cast = True
                        elif character.can_use_ability(11):
                            ability = game_consts.abilitiesList[int(11)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(11)
                            })
                            cast = True
                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                elif character.attributes.health < 500 and character.can_use_ability(12):
                    ability = game_consts.abilitiesList[int(12)]
                    # Get ability
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        # Am I buffing or debuffing? If buffing, target myself
                        "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                        "AbilityId": int(12)
                    })
                else:  # Not in range, move towards
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
            if character.deserialize()['ClassId'] == "Wizard":
                # If I am in range, either move towards target
                if character.in_range_of(target, gameMap):
                    # Am I already trying to cast something?
                    if character.casting is None:
                        cast = False
                        if (character.attributes.stunned < 0 or character.attributes.silenced != 0) and character.can_use_ability(0):
                            ability = game_consts.abilitiesList[int(0)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(0)
                            })
                            cast = True
                        elif character.can_use_ability(10) and possibleStun:
                            ability = game_consts.abilitiesList[int(10)]
                            enemy = target
                            if enemy in stunning:
                                for tar in enemyteam:
                                    if not tar.is_dead():
                                        if tar not in stunning:
                                            if character.in_range_of(tar, gameMap):
                                                if tar.attributes.stunned == 0:
                                                    enemy = tar
                            stunning.append(enemy)


                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": enemy.id,
                                "AbilityId": int(10)
                            })
                            cast = True
                        elif character.can_use_ability(9):
                            ability = game_consts.abilitiesList[int(9)]
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                "AbilityId": int(9)
                            })
                            cast = True
                        if not cast:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                else:  # Not in range, move towards
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                        })








            # If I am in range, either move towards target
            """elif character.in_range_of(target, gameMap):
                # Am I already trying to cast something?
                if character.casting is None:
                    cast = False
                    for abilityId, cooldown in character.abilities.items():
                        # Do I have an ability not on cooldown
                        if cooldown == 0:
                            # If I can, then cast it
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
            else: # Not in range, move towards
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })"""

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
