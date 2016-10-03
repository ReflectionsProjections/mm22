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
teamName = "NoEcho"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Golden Oreo",
                 "ClassId": "Archer"},
                {"CharacterName": "Clint Barton",
                 "ClassId": "Archer"},
                {"CharacterName": "Sean Bean",
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

    target = None
    lowest_health = 9999;
    which_tar = 99


    test_target1 = None
    test_target2 = None
    test_target3 = None

    for character in enemyteam:
        if not character.is_dead():
            if test_target1 is None:
                test_target1 = character
            elif test_target2 is None:
                test_target2 = character
            else:
                test_target3 = character
            if character.classId == "Assassin":
                which_tar = 0
                target = character
            if character.classId == "Sorcerer" and which_tar > 1:
                which_tar = 1
                target = character
            if character.classId == "Archer" and which_tar > 2:
                which_tar = 2
                target = character
            if character.classId == "Wizard" and which_tar > 3:
                which_tar = 3
                target = character
            if character.classId == "Druid" and which_tar > 4:
                which_tar = 4
                target = character
            if character.classId == "Enchanter" and which_tar > 5:
                which_tar = 5
                target = character
            if character.classId == "Paladin" and which_tar > 6:
                which_tar = 6
                target = character
            if character.classId == "Warrior" and which_tar > 7:
                which_tar = 7
                target = character

    # If we found a target
    if target:
        buffing_id = 99
        stun_target1 = None
        stun_target2 = None
        for character in myteam:
            if not character.attributes.get_attribute("Rooted") and not character.attributes.get_attribute("Stunned"):
                if target == test_target1:
                    if test_target2 is not None and character.in_range_of(test_target2, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target2, gameMap):
                            target = test_target2
                        character.move_towards_position(current_position, gameMap)
                    elif test_target3 is not None and character.in_range_of(test_target3, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target3, gameMap):
                            target = test_target3
                        character.move_towards_position(current_position, gameMap)
                if target == test_target2:
                    if test_target1 is not None and character.in_range_of(test_target1, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target1, gameMap):
                            target = test_target1
                        character.move_towards_position(current_position, gameMap)
                    elif test_target3 is not None and character.in_range_of(test_target3, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target3, gameMap):
                            target = test_target3
                        character.move_towards_position(current_position, gameMap)
                if target == test_target3:
                    if test_target1 is not None and character.in_range_of(test_target1, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target1, gameMap):
                            target = test_target2
                        character.move_towards_position(current_position, gameMap)
                    elif test_target2 is not None and character.in_range_of(test_target2, gameMap):
                        current_position = character.position
                        character.move_towards_target(target, gameMap)
                        if not character.in_range_of(test_target2, gameMap):
                            target = test_target1
                        character.move_towards_position(current_position, gameMap)

            #Enchantress
            if character.classId == 'Enchanter' and not character.is_dead():
                cc = False
                spelled = False
                sil_tar = target
                move_target = target
                debuff_target = target
                debuff_target1 = target
                debuff_target2 = target
                debuff_target3 = target
                for debuff in character.debuffs:
                    if debuff['Attribute'] == 'Silenced' or (debuff['Attribute'] == 'Rooted' and character.casting is None) or debuff['Attribute'] == 'Stunned':
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 0
                            })
                            cc = True
                if character.casting is None and not cc:
                    which_tar = 99
                    for abilityIds, cooldown in character.abilities.items():
                        if int(abilityIds) == 5 and cooldown == 0:
                            for sil_char in enemyteam:
                                if not sil_char.is_dead():
                                    if sil_char.classId == 'Wizard' and (sil_char.can_use_ability(9) or sil_char.can_use_ability(10)):
                                        sil_tar = sil_char
                                        which_tar = 0
                                    if sil_char.classId == 'Sorcerer' and which_tar > 1 and sil_char.can_use_ability(16):
                                        sil_tar = sil_char
                                        which_tar = 1
                                    if sil_char.classId == 'Paladin' and which_tar > 2 and (sil_char.can_use_ability(3) or sil_char.can_use_ability(14)):
                                        sil_tar = sil_char
                                        which_tar = 2
                                    if sil_char.classId == 'Druid' and which_tar > 3 and (sil_char.can_use_ability(3) or sil_char.can_use_ability(13)):
                                        sil_tar = sil_char
                                        which_tar = 3
                                    if sil_char.classId == 'Warrior' and which_tar > 4 and (sil_char.can_use_ability(1)):
                                        sil_tar = sil_char
                                        which_tar = 4
                                    if sil_char.classId == 'Enchanter' and which_tar > 5 and (sil_char.can_use_ability(7) or sil_char.can_use_ability(5)):
                                        sil_tar = sil_char
                                        which_tar = 5
                                    if sil_char.classId == 'Assassin' and which_tar > 6 and (sil_char.can_use_ability(11)):
                                        sil_tar = sil_char
                                        which_tar = 6
                                    if sil_char.classId == 'Archer':
                                        sil_tar = sil_char
                                        which_tar = 7
                        if int(abilityIds) == 6 and cooldown == 0:
                            for debuff_character in enemyteam:
                                if debuff_target1 == target:
                                    debuff_target1 = debuff_character
                                elif debuff_target2 == target:
                                    debuff_target2 = debuff_character
                                else:
                                    debuff_target3 = debuff_character
                            if character.in_ability_range_of(debuff_target1, gameMap, int(abilityIds)):
                                if character.in_ability_range_of(debuff_target2, gameMap, int(abilityIds)):
                                    if character.in_ability_range_of(debuff_target3, gameMap, int(abilityIds)):
                                        if debuff_target1.attributes.health >= debuff_target2.attributes.health and debuff_target1.attributes.health >= debuff_target3.attributes.health: #debuff1 is target
                                            debuff_target = debuff_target1
                                    elif debuff_target1.attributes.health >= debuff_target2.attributes.health:
                                        debuff_target = debuff_target1
                                elif character.in_ability_range_of(debuff_target3, gameMap, int(abilityIds)) and debuff_target1.attributes.health >= debuff_target3.attributes.health:
                                        debuff_target = debuff_target1
                                elif abs(character.position[0] - debuff_target2.position[0]) + abs(character.position[1] - debuff_target2.position[1]) < 4:
                                    move_target = debuff_target2
                                    spelled = True
                                elif abs(character.position[0] - debuff_target3.position[0]) + abs(character.position[1] - debuff_target3.position[1]) < 4:
                                    move_target = debuff_target3
                                    spelled = True
                            elif character.in_ability_range_of(debuff_target2, gameMap, int(abilityIds)):
                                if character.in_ability_range_of(debuff_target1, gameMap, int(abilityIds)):
                                    if character.in_ability_range_of(debuff_target3, gameMap, int(abilityIds)):
                                        if debuff_target2.attributes.health >= debuff_target1.attributes.health and debuff_target2.attributes.health >= debuff_target3.attributes.health: #debuff2 is target
                                            debuff_target = debuff_target2
                                    elif debuff_target2.attributes.health >= debuff_target1.attributes.health:
                                        debuff_target = debuff_target2
                                elif character.in_ability_range_of(debuff_target3, gameMap, int(abilityIds)) and debuff_target2.attributes.health >= debuff_target3.attributes.health:
                                        debuff_target = debuff_target2
                                elif abs(character.position[0] - debuff_target1.position[0]) + abs(character.position[1] - debuff_target1.position[1]) < 4:
                                    move_target = debuff_target1
                                    spelled = True
                                elif abs(character.position[0] - debuff_target3.position[0]) + abs(character.position[1] - debuff_target3.position[1]) < 4:
                                    move_target = debuff_target3
                                    spelled = True
                            elif character.in_ability_range_of(debuff_target3, gameMap, int(abilityIds)):
                                if character.in_ability_range_of(debuff_target2, gameMap, int(abilityIds)):
                                    if character.in_ability_range_of(debuff_target1, gameMap, int(abilityIds)):
                                        if debuff_target3.attributes.health >= debuff_target2.attributes.health and debuff_target3.attributes.health >= debuff_target1.attributes.health: #debuff3 is target
                                            debuff_target = debuff_target3
                                    elif debuff_target3.attributes.health >= debuff_target2.attributes.health:
                                        debuff_target = debuff_target3
                                elif character.in_ability_range_of(debuff_target1, gameMap, int(abilityIds)) and debuff_target3.attributes.health >= debuff_target1.attributes.health:
                                        debuff_target = debuff_target3
                                elif abs(character.position[0] - debuff_target2.position[0]) + abs(character.position[1] - debuff_target2.position[1]) < 4:
                                    move_target = debuff_target2
                                    spelled = True
                                elif abs(character.position[0] - debuff_target1.position[0]) + abs(character.position[1] - debuff_target1.position[1]) < 4:
                                    move_target = debuff_target1
                                    spelled = True

                    for abilityIds, cooldown in character.abilities.items():
                        if int(abilityIds) == 5 and spelled == False and which_tar != 99: #Silence
                            if character.in_ability_range_of(sil_tar, gameMap, int(abilityIds)):   #in range of silence
                                cast = False
                                if character.can_use_ability(5):   #on cooldown?
                                    ability = game_consts.abilitiesList[5]
                                    # Get ability
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": target.id,
                                        "AbilityId": int(abilityIds)
                                    })
                                    cast = True
                                    spelled = True
                                    break
                        elif int(abilityIds) == 6 and spelled == False:  # Debuff
                            if character.in_ability_range_of(debuff_target, gameMap, int(abilityIds)):  # in range of silence
                                cast = False
                                if character.can_use_ability(6):  # on cooldown?
                                    # Get ability
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": debuff_target.id,
                                        "AbilityId": int(abilityIds)
                                    })
                                    cast = True
                                    spelled = True
                                    break
                        elif int(abilityIds) == 7 and spelled == False: #Buff
                            better = True
                            helping_character = myteam[0]

                            teamsize = 0
                            for help_character in myteam:
                                dist = abs(help_character.position[0] - target.position[0]) + abs(help_character.position[1] - target.position[1])
                                if (helping_character.attributes.health/helping_character.attributes.maxHealth) < (help_character.attributes.health/help_character.attributes.maxHealth) or (help_character.can_use_ability(12) and (dist == 4 or dist == 3)):
                                    better = True
                                if better:
                                    helping_character = help_character
                                    better = False
                                if not help_character.is_dead():
                                    teamsize += 1
                            if teamsize > 1 and character.in_ability_range_of(helping_character, gameMap, int(abilityIds)):
                                if (help_character.can_use_ability(12) and (dist == 4 or dist == 3)) or helping_character.attributes.get_attribute('Health') < helping_character.attributes.get_attribute('MaxHealth'):
                                        cast = False
                                        if character.can_use_ability(7):   #on cooldown?
                                            # Get ability
                                            actions.append({
                                                "Action": "Cast",
                                                "CharacterId": character.id,
                                                "TargetId": helping_character.id,
                                                "AbilityId": int(abilityIds)
                                            })
                                            buffing_id = 0
                                            cast = True
                                            spelled = True
                                            break

                                # Was I able to cast something? Either wise attack
                    if spelled == False and character.in_range_of(target,gameMap):
                        actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
                    elif not spelled:  # Not in range, move towards
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": move_target.id,
                        })
                elif character.casting is not None:
                    if character.casting['AbilityId'] is 7:
                        buffing_id = character.abilities[6]


            if character.classId == 'Archer' and not character.is_dead():
                cc = False
                for debuff in character.debuffs:
                    #free yourself
                    if debuff['Attribute'] == 'Silenced' or debuff['Attribute'] == 'Rooted' or debuff[
                        'Attribute'] == 'Stunned':
                        if character.can_use_ability(0):
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 0
                            })
                            cc = True
                if not cc:
                    retreat = False
                    sprint = False
                    run_target = None
                    amount_of_allies = 0
                    amount_of_enemies = 0
                    for allies in myteam:
                        if not allies.is_dead():
                            amount_of_allies += 1
                    for enemies in enemyteam:
                        if not enemies.is_dead():
                            amount_of_enemies += 1
                    if amount_of_enemies == 1:
                        if not character.in_range_of(target, gameMap):
                            sprint = True
                    for enemy in enemyteam:
                        if enemy.attributes.attackRange == 0 and not enemy.attributes.get_attribute("Rooted") and not enemy.attributes.get_attribute("Stunned"):
                            enemy_pos = enemy.position
                            enemy.move_towards_target(target, gameMap)
                            if enemy.in_range_of(character, gameMap):
                                retreat = True
                                if allies == 1:
                                    sprint = True
                                if run_target is None:
                                    run_target = enemy
                            enemy.move_towards_position(enemy_pos, gameMap)
                        elif enemy.attributes.attackRange == 1:
                            if enemy.in_range_of(character, gameMap):
                                if allies == 1:
                                    sprint = True
                                retreat = True
                                run_target = enemy
                    if sprint and character.can_use_ability(2):
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                            "AbilityId": 2
                        })
                    elif retreat:
                        if not character.attributes.get_attribute("Rooted") and not character.attributes.get_attribute("Stunned"):
                            x = character.position[0]
                            y = character.position[1]
                            x -= run_target.position[0]
                            y -= run_target.position[1]
                            x += character.position[0]
                            y += character.position[1]
                            if x == character.position[0] and y == character.position[1]:
                                x = -1
                                y = -1
                                positions = gameMap.get_valid_adjacent_pos(character.position)
                                cur_pos = character.position
                                overall_x = -1
                                overall_y = -1
                                for pos in positions:
                                    character.move_towards_position(pos, gameMap)
                                    fail = False
                                    for enem in enemyteam:
                                        if not enem.in_range_of(character, gameMap) and not fail:
                                            x = pos[0]
                                            y = pos[1]
                                        else:
                                            fail = True
                                    character.move_towards_position(cur_pos, gameMap)
                                    if not fail:
                                        overall_x = x
                                        overall_y = y
                                x = overall_x
                                y = overall_y
                            if x != -1 and y != -1:
                                actions.append({
                                    "Action": "Move",
                                    "CharacterId": character.id,
                                    "Location": (x,y),
                                })
                            else:
                                actions.append({
                                    "Action": "Attack",
                                    "CharacterId": character.id,
                                    "TargetId": target.id,
                                })
                    elif character.in_range_of(target, gameMap):
                        actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
                    else:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })

            #ASSASSIN AI
            if character.classId == 'Assassin':  # if character is assassin
                cc = False
                for debuff in character.debuffs:
                    if debuff['Attribute'] == 'Silenced' or debuff['Attribute'] == 'Rooted' or debuff['Attribute'] == 'Stunned':
                        if character.can_use_ability(0):
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 0
                            })
                            cc = True
                if not cc:
                    if character.in_range_of(target, gameMap):  # at this point target = lowest health enemy
                        if character.casting is None:  # assassin casting is always instant
                            cast = False
                            if character.can_use_ability(11):  # backstab off cooldown
                                ability = game_consts.abilitiesList[int(11)]
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    "TargetId": target.id,
                                    "AbilityId": 11
                                })  # do the backstab
                            else:
                                actions.append({
                                    "Action": "Attack",
                                    "CharacterId": character.id,
                                    "TargetId": target.id,
                                })  # do standard attack
                    else:
                        dist = abs(character.position[0] - target.position[0]) + abs(character.position[1]-target.position[1])
                        if character.can_use_ability(12) and  (dist == 4 or dist == 3):  # sprint off cooldown
                            ability = game_consts.abilitiesList[int(12)]
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 12
                            })
                        elif buffing_id > 1:  # just move towards enemy
                            actions.append({
                                "Action": "Move",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })

            #WARRIOR AI
            if character.classId == 'Warrior' and not character.is_dead():
                cc = False
                spelled = False
                sil_tar = target
                move_target = target
                for debuff in character.debuffs:
                    if debuff['Attribute'] == 'Silenced' or (
                            debuff['Attribute'] == 'Rooted' and character.casting is None) or debuff[
                        'Attribute'] == 'Stunned':
                        actions.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": character.id,
                            "AbilityId": 0
                        })
                        cc = True
                if character.casting is None and not cc:
                    which_tar = 99
                    for abilityIds, cooldown in character.abilities.items():
                        if int(abilityIds) == 1 and cooldown == 0:
                            for sil_char in enemyteam:
                                if not sil_char.is_dead():
                                    already_stunned = False
                                    for debuff in sil_char.debuffs:
                                        if debuff['Attribute'] == 'Stunned':
                                            already_stunned = True
                                    if not already_stunned:
                                        if sil_char.classId == 'Wizard' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 0
                                        if sil_char.classId == 'Sorcerer' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 1
                                        if sil_char.classId == 'Paladin' and  (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 2
                                        if sil_char.classId == 'Druid' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 3
                                        if sil_char.classId == 'Warrior' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 4
                                        if sil_char.classId == 'Enchanter' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 5
                                        if sil_char.classId == 'Assassin' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 6
                                        if sil_char.classId == 'Archer' and (stun_target1 != sil_char or stun_target2 != sil_char):
                                            sil_tar = sil_char
                                            which_tar = 7
                            if stun_target1 is None:
                                stun_target1 = sil_tar
                            elif stun_target2 is None:
                                stun_target2 = sil_tar
                    for abilityIds, cooldown in character.abilities.items():
                        if int(abilityIds) == 1 and spelled == False and which_tar != 99:  # Silence
                            if character.in_ability_range_of(sil_tar, gameMap,
                                                             int(abilityIds)):  # in range of silence
                                cast = False
                                if character.can_use_ability(1):  # on cooldown?
                                    ability = game_consts.abilitiesList[1]
                                    # Get ability
                                    actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": sil_tar.id,
                                        "AbilityId": int(abilityIds)
                                    })
                                    cast = True
                                    spelled = True
                    if spelled == False and character.in_range_of(target, gameMap):
                        actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
                    elif not spelled:  # Not in range, move towards
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": move_target.id,
                        })
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
