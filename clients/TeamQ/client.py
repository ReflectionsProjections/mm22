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

initialMove = 0
try_for_draw = False
doom_to_win = False
enemy_type = 0
startPos = 0
current_turns = 1
battle_start = False
peace_times = 0
time_cycle_warrior = -1
exit_time_cycle_warrior = False
special_gift = False
special_num = 3
move_for_just_once = True

shoot_for_just_once = 3
# Game map that you can use to query
gameMap = GameMap()

# --------------------------- SET THIS IS UP -------------------------
teamName = "TeamQ"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Archer1",
                 "ClassId": "Archer"},
                {"CharacterName": "Archer2",
                 "ClassId": "Archer"},
                {"CharacterName": "Archer3",
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

    global initialMove
    global try_for_draw
    global enemy_type
    global startPos
    global current_turns
    global battle_start
    global time_cycle_warrior
    global doom_to_win
    global exit_time_cycle_warrior
    global peace_times
    global move_for_just_once
    global shoot_for_just_once
    global special_gift
    global special_num

    current_turns += 1

    if startPos == 0:
        if myteam[0].position[0] == 0:
            startPos = 1
        else:
            startPos = 2
    if enemy_type == 0:
        classID = []
        for characterEnemy in enemyteam:
            classID.append( characterEnemy.classId )
        print classID
        if classID[0] == "Warrior" and classID[1] == "Warrior" and classID[2] == "Warrior" :
            enemy_type = 3
        elif classID[0] == "Assassin" and classID[1] == "Assassin" and classID[2] == "Assassin" :
            enemy_type = 2
        elif classID[0] == "Archer" and classID[1] == "Archer" and classID[2] == "Archer" :
            enemy_type = 1
        else:
            enemy_type = -1
        if classID.__contains__("Archer") and classID.__contains__("Paladin"):
            special_gift = True

    if initialMove < 3:
        if initialMove == 0:
            for character in myteam:
                if enemy_type != 2:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                        "AbilityId": 12
                    })
                else:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                    })
            initialMove += 1
            return {
                'TeamName': teamName,
                'Actions': actions
            }
        if initialMove == 1:
            for character in myteam:
                if enemy_type!= 2:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "Location": (2, 2),

                    })
                else:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                    })
            initialMove += 1
            return {
                'TeamName': teamName,
                'Actions': actions
            }
        if initialMove == 2:
            for character in myteam:
                if enemy_type != 2:
                    desti = ()
                    if enemy_type == 3:
                        if startPos == 1:
                            desti = (2, 1)
                        else:
                            desti = (2, 3)
                    elif enemy_type == -1 or enemy_type == 1:
                        desti = (2, 2)
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "Location": desti,
                    })
                else:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                        "AbilityId": 12
                    })
            initialMove += 1
            return {
                'TeamName': teamName,
                'Actions': actions
            }

    alive = 0
    elive = 0
    for character in myteam:
        if not character.is_dead():
            alive += 1
    for characterEnemy in enemyteam:
        if not characterEnemy.is_dead():
            elive += 1

    if alive == 1 and alive == elive and try_for_draw == False and doom_to_win == False:
        life1 = 0
        att1 = 0
        def1 = 0
        for character in myteam:
            if not character.is_dead():
                life1 = character.attributes.health
                att1 = character.attributes.damage
                def1 = character.attributes.armor
        life2 = 0
        att2 = 0
        def2 = 0
        for characterEnemy in enemyteam:
            if not characterEnemy.is_dead():
                life2 = characterEnemy.attributes.health
                att2 = characterEnemy.attributes.damage
                def2 = characterEnemy.attributes.armor
        if ((0.0 + life1) / (att2 - def1)) < ((0.0 + life2) / (att1 - def2)):
            try_for_draw = True
        elif ((0.0 + life1) / (att2 - def1)) >= ((0.0 + life2) / (att1 - def2)):
            doom_to_win = True


    if try_for_draw:
        for character in myteam:
            if not character.is_dead():
                for debu in character.debuffs:
                    if ( debu['Attribute'] == 'Stunned' or debu['Attribute'] == 'Silenced' or debu['Attribute'] == 'Rooted' ) and \
                            ( character.abilities[0] == 0 ):
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": 0
                        })
                        return {
                            'TeamName': teamName,
                            'Actions': actions
                        }
        oppX = 0
        oppY = 0
        for characterEnemy in enemyteam:
            if not characterEnemy.is_dead():
                oppX = characterEnemy.position[0]
                oppY = characterEnemy.position[1]
        for character in myteam:
            if not character.is_dead():
                nX = character.position[0]
                nY = character.position[1]
                maxdis = 0
                maxX = nX
                maxY = nY
                obs = [(1, 3), (3, 3), (3, 1), (1, 1)]
                if nX + 1 <= 4 and (nX + 1, nY) not in obs:
                    if maxdis < abs(nX + 1 - oppX) + abs(nY - oppY):
                        maxdis = abs(nX + 1 - oppX) + abs(nY - oppY)
                        maxX = nX + 1
                        maxY = nY
                if nY + 1 <= 4 and (nX, nY + 1) not in obs:
                    if maxdis < abs(nX - oppX) + abs(nY + 1 - oppY):
                        maxdis = abs(nX - oppX) + abs(nY + 1 - oppY)
                        maxX = nX
                        maxY = nY + 1
                if nX - 1 >= 0 and (nX - 1, nY) not in obs:
                    if maxdis < abs(nX - 1 - oppX) + abs(nY - oppY):
                        maxdis = abs(nX - 1 - oppX) + abs(nY - oppY)
                        maxX = nX - 1
                        maxY = nY
                if nY - 1 >= 0 and (nX, nY - 1) not in obs:
                    if maxdis < abs(nX - oppX) + abs(nY - 1 - oppY):
                        maxdis = abs(nX - oppX) + abs(nY - 1 - oppY)
                        maxX = nX
                        maxY = nY - 1

                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "Location": (maxX, maxY),
                })
                return {
                    'TeamName': teamName,
                    'Actions': actions
                }
    if doom_to_win:
        for character in myteam:
            if not character.is_dead():
                for debu in character.debuffs:
                    if ( debu['Attribute'] == 'Stunned' or debu['Attribute'] == 'Silenced' or debu['Attribute'] == 'Rooted' ) and \
                            ( character.abilities[0] == 0 ):
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": 0
                        })
                        return {
                            'TeamName': teamName,
                            'Actions': actions
                        }
        for characterEnemy in enemyteam:
            if not characterEnemy.is_dead():
                for character in myteam:
                    if not character.is_dead():
                        if character.in_range_of(characterEnemy, gameMap):
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": characterEnemy.id,
                            })

                        elif character.abilities[12] == 0:
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 12
                            })
                        else:
                            actions.append({
                                "Action": "Move",
                                "CharacterId": character.id,
                                "TargetId": characterEnemy.id,
                            })
        return {
                'TeamName': teamName,
                'Actions': actions
            }

    if move_for_just_once and enemy_type == 2:
        oppX = enemyteam[0].position[0]
        oppY = enemyteam[0].position[1]
        nX = myteam[0].position[0]
        nY = myteam[0].position[1]
        maxdis = 2
        maxX = nX
        maxY = nY
        obs = [(1, 3), (3, 3), (3, 1), (1, 1)]
        if nX + 2 <= 4 and (nX + 2, nY) not in obs:
            if maxdis < abs(nX + 2 - oppX) + abs(nY - oppY):
                maxdis = abs(nX + 2 - oppX) + abs(nY - oppY)
                maxX = nX + 2
                maxY = nY
        if nY + 2 <= 4 and (nX, nY + 2) not in obs:
            if maxdis < abs(nX - oppX) + abs(nY + 2 - oppY):
                maxdis = abs(nX - oppX) + abs(nY + 2 - oppY)
                maxX = nX
                maxY = nY + 2
        if nX - 2 >= 0 and (nX - 2, nY) not in obs:
            if maxdis < abs(nX - 2 - oppX) + abs(nY - oppY):
                maxdis = abs(nX - 2 - oppX) + abs(nY - oppY)
                maxX = nX - 2
                maxY = nY
        if nY - 2 >= 0 and (nX, nY - 2) not in obs:
            if maxdis < abs(nX - oppX) + abs(nY - 2 - oppY):
                maxdis = abs(nX - oppX) + abs(nY - 2 - oppY)
                maxX = nX
                maxY = nY - 2
        for character in myteam:
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "Location": (maxX, maxY),
            })
        move_for_just_once = False


    if enemy_type == 3 and not exit_time_cycle_warrior:
        if elive== 1:
            time_cycle_warrior = -5
            exit_time_cycle_warrior = True
        if time_cycle_warrior >= 2:
            for characterEnemy in enemyteam:
                if not characterEnemy.is_dead() and characterEnemy.position == (2, 2):
                    time_cycle_warrior = -5
                    exit_time_cycle_warrior = True
                    break
        if time_cycle_warrior == 16:
            time_cycle_warrior = 0
        if time_cycle_warrior == -1 :
            if enemyteam[0].position == (2,1):
                for character in myteam:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "Location": (2,4),
                    })
                time_cycle_warrior += 1
            elif enemyteam[0].position == (2,3):
                for character in myteam:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "Location": (2,0),
                    })
                time_cycle_warrior += 1

        elif time_cycle_warrior == 4 or time_cycle_warrior == 12:
            for character in myteam:
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": character.id,
                    "AbilityId": 12
                })
            time_cycle_warrior += 1
        elif time_cycle_warrior == 6 or time_cycle_warrior == 14:

            charEnemyInArmor = []
            for characterEnemy in enemyteam:
                if not characterEnemy.is_dead():
                    charEnemyInArmor.append(characterEnemy)
            for i in xrange(len(charEnemyInArmor)):
                for j in xrange(i + 1, len(charEnemyInArmor)):
                    if (0.0+charEnemyInArmor[i].attributes.damage) / (charEnemyInArmor[i].attributes.get_attribute('Armor')+1) < \
                                    (0.0+charEnemyInArmor[j].attributes.damage) / (charEnemyInArmor[j].attributes.get_attribute('Armor')+1):
                        charEnemyInArmor[i], charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]
                    elif charEnemyInArmor[i].attributes.armor == charEnemyInArmor[j].attributes.armor:
                        if charEnemyInArmor[i].attributes.health > charEnemyInArmor[j].attributes.health:
                            charEnemyInArmor[i], charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]

            for character in myteam:
                for characterEnemy in charEnemyInArmor:
                    if character.in_range_of(characterEnemy, gameMap):
                        actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": characterEnemy.id,
                        })
                        break
                    else:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": character.position,
                        })
                        break
            time_cycle_warrior += 1
        elif time_cycle_warrior >= 0:
            for character in myteam:
                posX = character.position[0]
                posY = character.position[1]
                if posX == 0 and posY == 0:
                    posX = 4
                elif posX == 4 and posY == 4:
                    posX = 0
                elif posX == 2 and posY == 0:
                    posX = 3
                elif posX == 2 and posY == 4:
                    posX = 1
                elif posX == 0:
                    posY = 0
                elif posX == 4:
                    posY = 4
                elif posY == 0:
                    posX = 4
                elif posY == 4:
                    posX = 0
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "Location": (posX,posY),
                })
            time_cycle_warrior += 1
        if time_cycle_warrior >= 0:
            return {
                'TeamName': teamName,
                'Actions': actions
            }
##############33Be sure to change this 10 to 120~
    if current_turns <= 10 and peace_times <= 4:
        print peace_times
        a_done = {}
        a_done[0] = False
        a_done[1] = False
        a_done[2] = False
        for character in myteam:
            if not character.is_dead():
                for debu in character.debuffs:
                    if ( debu['Attribute'] == 'Stunned' or debu['Attribute'] == 'Silenced' or debu['Attribute'] == 'Rooted' ) and \
                            ( character.abilities[0] == 0 ):
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": 0
                        })
                        a_done[character.id % 3] = True
                        break
        for character in myteam:
            if ( not a_done[character.id % 3] ) and ( not character.is_dead() ):
                for characterEnemy in enemyteam:
                    if not characterEnemy.is_dead():
                        if characterEnemy.casting is not None and characterEnemy.casting['TargetId'] == character.id\
                                and (characterEnemy.position[0] != 2 or characterEnemy.position[1] != 2) and \
                                characterEnemy.casting['CurrentCastTime'] == 0:
                            hideX = 0
                            hideY = 0
                            if characterEnemy.casting['AbilityId'] == 16:
                                hideX = 4 - characterEnemy.position[1]
                                hideY = 4 - characterEnemy.position[0]
                            else:
                                hideX = 4 - characterEnemy.position[0]
                                hideY = 4 - characterEnemy.position[1]
                            actions.append({
                                "Action": "Move",
                                "CharacterId": character.id,
                                "Location": (hideX, hideY),
                            })
                            a_done[character.id % 3] = True
                            break
        medicalable = False
        charEnemyInArmor = []
        for characterEnemy in enemyteam:
            if not characterEnemy.is_dead():
                charEnemyInArmor.append(characterEnemy)
                ############# magic number!
                if characterEnemy.classId == 'Druid' or characterEnemy.classId == 'Paladin':
                    if characterEnemy.abilities[3] == 0:
                        medicalable = True
        for i in xrange(len(charEnemyInArmor)):
            for j in xrange(i + 1, len(charEnemyInArmor)):
                if (0.0 + charEnemyInArmor[i].attributes.damage) / (
                    charEnemyInArmor[i].attributes.get_attribute('Armor') + 1) < \
                                (0.0 + charEnemyInArmor[j].attributes.damage) / (
                            charEnemyInArmor[j].attributes.get_attribute('Armor') + 1):
                    charEnemyInArmor[i], charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]
                elif charEnemyInArmor[i].attributes.armor == charEnemyInArmor[j].attributes.armor:
                    if charEnemyInArmor[i].attributes.health > charEnemyInArmor[j].attributes.health:
                        charEnemyInArmor[i], charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]
        if not medicalable:
            for characterEnemy in charEnemyInArmor:
                curhealth = characterEnemy.attributes.health
                curdefence = characterEnemy.attributes.armor
                for character in myteam:
                    if not character.is_dead():
                        if not a_done[character.id % 3]:
                            if character.in_range_of(characterEnemy, gameMap):
                                curattack = character.attributes.damage
                                if curhealth <= 0:
                                    break
                                curhealth -= (curattack - curdefence)
                                if (enemy_type == 1 and character.abilities[2] == 0 and shoot_for_just_once > 0) or \
                                    (enemy_type == -1 and character.abilities[2] == 0 and special_gift and special_num > 0):
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": characterEnemy.id,
                                        "AbilityId": 2
                                    })
                                    if special_gift:
                                        special_num -= 1
                                    else:
                                        shoot_for_just_once -= 1
                                else:
                                    actions.append({
                                        "Action": "Attack",
                                        "CharacterId": character.id,
                                        "TargetId": characterEnemy.id,
                                    })
                                battle_start = True
                                a_done[character.id % 3] = True

        else:
            for characterEnemy in charEnemyInArmor:
                for character in myteam:
                    if not character.is_dead():
                        if not a_done[character.id % 3]:
                            if character.in_range_of(characterEnemy, gameMap):
                                actions.append({
                                    "Action": "Attack",
                                    "CharacterId": character.id,
                                    "TargetId": characterEnemy.id,
                                })
                                battle_start = True
                                a_done[character.id % 3] = True
        for character in myteam:
            if not character.is_dead():
                if not a_done[character.id % 3]:
                    if battle_start:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": (2, 2),
                        })
                        peace_times += 1
                        print peace_times
                    else:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": character.position,
                        })
                    a_done[character.id % 3] = True
        return {
            'TeamName': teamName,
            'Actions': actions
        }


    else:
        a_done = {}
        a_done[0] = False
        a_done[1] = False
        a_done[2] = False
        for character in myteam:
            if not character.is_dead():
                for debu in character.debuffs:
                    if (debu['Attribute'] == 'Stunned' or debu['Attribute'] == 'Silenced' or debu['Attribute'] == 'Rooted') and \
                            (character.abilities[0] == 0):
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": 0
                        })
                        a_done[character.id % 3] = True
                        break
        for character in myteam:
            if ( not a_done[character.id % 3] ) and ( not character.is_dead() ):
                for characterEnemy in enemyteam:
                    if not characterEnemy.is_dead():
                        if characterEnemy.casting is not None and characterEnemy.casting['TargetId'] == character.id\
                                and (characterEnemy.position[0] != 2 or characterEnemy.position[1] != 2) and \
                                characterEnemy.casting['CurrentCastTime'] == 0:
                            hideX = character.position[0]
                            hideY = character.position[1]
                            if characterEnemy.casting['AbilityId'] == 16:
                                if character.position[0] == 0:
                                    hideX = 1
                                elif character.position[0] == 4:
                                    hideX = 3
                                elif character.position[1] == 0:
                                    hideY = 1
                                elif character.position[1] == 4:
                                    hideY = 3
                            actions.append({
                                "Action": "Move",
                                "CharacterId": character.id,
                                "Location": (hideX, hideY),
                            })
                            a_done[character.id % 3] = True
                            break
        medicalable = False
        charEnemyInArmor = []
        for characterEnemy in enemyteam:
            if not characterEnemy.is_dead():
                charEnemyInArmor.append(characterEnemy)
                if characterEnemy.classId == 'Druid' or characterEnemy.classId == 'Paladin':
                    if characterEnemy.abilities[3] == 0:
                        medicalable = True
        for i in xrange(len(charEnemyInArmor)):
            for j in xrange(i+1,len(charEnemyInArmor)):
                if (0.0 + charEnemyInArmor[i].attributes.damage) / (charEnemyInArmor[i].attributes.armor+1) < \
                                (0.0 + charEnemyInArmor[j].attributes.damage) / (charEnemyInArmor[j].attributes.armor+1):
                    charEnemyInArmor[i],charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]
                elif charEnemyInArmor[i].attributes.armor == charEnemyInArmor[j].attributes.armor:
                    if charEnemyInArmor[i].attributes.health > charEnemyInArmor[j].attributes.health:
                        charEnemyInArmor[i], charEnemyInArmor[j] = charEnemyInArmor[j], charEnemyInArmor[i]
        if not medicalable:
            for characterEnemy in charEnemyInArmor:
                curhealth = characterEnemy.attributes.health
                curdefence = characterEnemy.attributes.armor
                for character in myteam:
                    if not character.is_dead():
                        if not a_done[character.id % 3]:
                            if character.in_range_of(characterEnemy, gameMap):
                                curattack = character.attributes.damage
                                if curhealth <= 0:
                                    break
                                curhealth -= (curattack - curdefence)
                                if (enemy_type == 1 and character.abilities[2] == 0 and shoot_for_just_once > 0) or \
                                    (enemy_type == -1 and character.abilities[2] == 0 and special_gift and special_num > 0):
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": characterEnemy.id,
                                        "AbilityId": 2
                                    })
                                    if special_gift:
                                        special_num -= 1
                                    else:
                                        shoot_for_just_once -= 1
                                else:
                                    actions.append({
                                        "Action": "Attack",
                                        "CharacterId": character.id,
                                        "TargetId": characterEnemy.id,
                                    })

        else:
            for characterEnemy in charEnemyInArmor:
                for character in myteam:
                    if not character.is_dead():
                        if not a_done[character.id % 3]:
                            if character.in_range_of(characterEnemy, gameMap):
                                actions.append({
                                    "Action": "Attack",
                                    "CharacterId": character.id,
                                    "TargetId": characterEnemy.id,
                                })
                                battle_start = True
                                a_done[character.id % 3] = True
        for character in myteam:
            if not character.is_dead():
                if not a_done[character.id % 3]:
                    for characterEnemy in charEnemyInArmor:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": characterEnemy.id,
                        })
                        break
                    a_done[character.id % 3] = True

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
