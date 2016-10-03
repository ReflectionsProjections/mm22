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
teamName = "DADDY"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Sven",
                 "ClassId": "Warrior"},
                {"CharacterName": "Mortred",
                 "ClassId": "Assassin"},
                {"CharacterName": "Ursa",
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
    weightlist = ['Assassin','Archer','Wizard','Druid','Paladin','Sorcerer','Enchanter','Warrior']
    abilitylist = [10, 16, 3, 15, 7]
    hitlist = []
    stunlist = []
    # Choose a target
    target = None
    for character in weightlist:
        for enechara in enemyteam:
            if character == enechara.classId :
                hitlist.append(enechara)

    for character in hitlist:
        if not character.is_dead():
            target = character
            break

    # If we found a target
    if target:
        for character in myteam:
            #Warrior
            if character.classId == "Warrior":
                target_Warrior = target
                stg = 0

                if character.can_use_ability(0) and (character.attributes.get_attribute('Stunned') == True or character.attributes.get_attribute('Silenced') == True):
                    stg = 1

                if stg == 0:
                    for ability in abilitylist:
                        for enemy in enemyteam:
                            if enemy.casting != None and enemy.casting["AbilityId"] == ability and character.can_use_ability(1) and character.in_ability_range_of(enemy, gameMap, 1):
                                target_Warrior = enemy
                                stg = 2
                                break

                if stg == 0 and character.in_range_of(target_Warrior, gameMap):
                    stg = 3

                if stg == 1:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                        "AbilityId": 0
                    })
                elif stg == 2:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": target_Warrior.id,
                        "AbilityId": 1
                    })
                elif stg == 3:
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target_Warrior.id,
                    })
                else :
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target_Warrior.id,
                    })
            #Paladin
            if character.classId == "Paladin":
                #Default Strategy
                target_Paladin = target
                stg = 0

                for enemy in enemyteam:
                    if enemy.casting != None:
                        if character.can_use_ability(14) and character.in_ability_range_of(enemy, gameMap, 14):
                            target_Paladin = enemy
                            stg = 1
                            break

                if stg == 0:
                    for ally in myteam:
                        if not ally.is_dead():
                            if ally.attributes.get_attribute('Health') < ally.attributes.get_attribute('MaxHealth') - 250:
                                if character.can_use_ability(3) and character.in_ability_range_of(ally, gameMap, 3):
                                    if target_Paladin == target:
                                        target_Paladin = ally
                                    if ally.attributes.get_attribute('Health') < target_Paladin.attributes.get_attribute('Health'):
                                        target_Paladin = ally
                                    stg = 2

                if stg == 0 and character.in_range_of(target_Paladin, gameMap):
                    stg == 3

                #Strategy 1 : Stun casting enemy
                if stg == 1:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": target_Paladin.id,
                        "AbilityId": 14
                    })
                #Strategy 2 : Heal the weakest ally
                elif stg == 2:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": target_Paladin.id,
                        "AbilityId": 3
                    })
                #Strategy 3 : Attack
                elif stg == 3:
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target_Paladin.id,
                    })
                #Default Strategy : Move
                else :
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target_Paladin.id,
                    })
            #Assassin
            if character.classId == "Assassin":
                target_Assassin = target

                #Assasin Targetting most vulnerable
                # for enemy in enemyteam:
                #     if not enemy.is_dead():
                #         character_Damage = character.attributes.get_attribute('Damage')
                #
                #         target_Assassin_MaxHealth = target_Assassin.attributes.get_attribute('MaxHealth')
                #         target_Assassin_Armor = target_Assassin.attributes.get_attribute('Armor')
                #
                #         enemy_MaxHealth = enemy.attributes.get_attribute('MaxHealth')
                #         enemy_Armor = enemy.attributes.get_attribute('Armor')
                #
                #         target_Assassin_Vulnerability = target_Assassin_MaxHealth / (character_Damage - target_Assassin_Armor)
                #         enemy_Vulnerability = enemy_MaxHealth / (character_Damage - enemy_Armor)
                #         if enemy_Vulnerability < target_Assassin_Vulnerability:
                #             target_Assassin = enemy

                #Remove Debuff
                if character.can_use_ability(0) and (character.attributes.get_attribute('Stunned') == True or character.attributes.get_attribute('Silenced') == True):
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                        "AbilityId": 0
                    })
                #Backstab!
                elif character.can_use_ability(11) and character.in_ability_range_of(target_Assassin, gameMap, 11):
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": target_Assassin.id,
                        "AbilityId": 11
                    })
                #Backstab cooling down, attack
                elif character.in_range_of(target_Assassin, gameMap):
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target_Assassin.id,
                    })
                #No enemy in range, Move!
                else:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target_Assassin.id,
                    })

            else:
                if character.in_range_of(target, gameMap):
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
