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
teamName = "Team_4407"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Archer",
                 "ClassId": "Archer"},
                {"CharacterName": "Archer",
                 "ClassId": "Archer"},
                {"CharacterName": "Warrior",
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



    if len(enemyteam) == 0:
            return
    target = first_nondead_enemy(enemyteam)
    for enemy in enemyteam:
        if not enemy.is_dead():
            if enemy.attributes.get_attribute("Health") < target.attributes.get_attribute("Health"):
                target = enemy
    print target.classId

    lowest_Health = first_nondead_enemy(myteam)
    for y in myteam:
        if not y.is_dead():
            if y.attributes.get_attribute("Health") < lowest_Health.attributes.get_attribute("Health"):
                lowest_Health = y

    warrior_occupied = False
    archer_occupied = False
    palandin_occupied = False

    for character in myteam:
        archer_occupied = False
        high_profile_targets = abilityCalled(3, enemyteam)
        if len(high_profile_targets) > 0:
            action_items = stunAll(myteam, high_profile_targets)
            for item in action_items:
                if item["CharacterId"] == myteam[0].id:
                    warrior_occupied = True
                elif item["CharacterId"] == myteam[1].id:
                    archer_occupied = True
                elif item["CharacterId"] == myteam[2].id:
                    palandin_occupied = True
                actions.append(item)

        if character.classId == "Warrior" and not warrior_occupied:
            print shouldHoldOffOnStuns(enemyteam)
            if (shouldHoldOffOnStuns(enemyteam) == False or character.attributes.get_attribute('Armor')<50) and character.can_use_ability(1) and inAbilityRangeOfAnyEnemy(character, enemyteam, 1):
                print 'stun them'
                canHit = False
                for enemy in enemyteam:
                    if character.in_ability_range_of(enemy, gameMap, 1) and not warrior_occupied:
                        print "stun"
                        warrior_occupied = True
                        actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        "TargetId": target.id,
                                        "AbilityId": 1
                                    })
            elif character.attributes.get_attribute('Stunned') == True and not warrior_occupied:
                print "break stun"
                warrior_occupied = True
                actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 0
                            })
            elif character.in_range_of(enemyteam[0], gameMap) and not enemyteam[0].is_dead() and not warrior_occupied:
                print "attack 0"
                warrior_occupied = True
                actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
            elif character.in_range_of(enemyteam[1], gameMap) and not enemyteam[1].is_dead() and not warrior_occupied: 
                print "attack 1"
                warrior_occupied = True
                actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
            elif character.in_range_of(enemyteam[2], gameMap) and not enemyteam[2].is_dead() and not warrior_occupied:
                print "attack 2"
                warrior_occupied = True
                actions.append({
                            "Action": "Attack",
                            "CharacterId": character.id,
                            "TargetId": target.id,
                        })
            elif not warrior_occupied:
                print "move"
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })

        if character.classId == "Archer" and not archer_occupied:
            A_cast = False
            
            just_armor_buffed = False
            if not character.is_dead():

                if character.attributes.get_attribute('Stunned') == True and not archer_occupied:
                    archer_occupied = True
                    print("stunned")
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        # Am I buffing or debuffing? If buffing, target myself
                        "TargetId": character.id,
                        "AbilityId": 0
                    })
                    print("burst")
                    A_cast = True
                                        
            # If we found a target
            if target:
                # If I am in range, either move towards target
                if character.in_range_of(target, gameMap):
                    # Am I already trying to cast something?
                    if character.casting is None:
                        if not just_armor_buffed:
                            if character.can_use_ability(2) and character.attributes.get_attribute('Silenced') == False and not archer_occupied:
                                archer_occupied = True
                                actions.append({
                                    "Action": "Cast",
                                    "CharacterId": character.id,
                                    # Am I buffing or debuffing? If buffing, target myself
                                    "TargetId": target.id,
                                    "AbilityId": 2
                                })
                                A_cast = True
                                just_armor_buffed = True
                    # Was I able to cast something? Either wise attack
                        if not A_cast and not archer_occupied:
                            #print "attack"
                            archer_occupied = True
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                            just_armor_buffed = False
                elif not archer_occupied: # Not in range, move towards
                    print "moved"
                    archer_occupied = True
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
                    just_armor_buffed = False
    #################################
        cast = False
        #print palandin_occupied
        if character.classId == "Paladin" and not palandin_occupied:
            if character.in_ability_range_of(enemy, gameMap, 14) and character.can_use_ability(14) and not palandin_occupied:
                print "stun"
                palandin_occupied = True
                actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                                "AbilityId": 14
                            })
            if character.can_use_ability(0):
                print lowest_Health.attributes.get_attribute("Health")
                if (character.attributes.get_attribute("Stunned") == True or character.attributes.get_attribute("Root") == True) and not palandin_occupied:
                    palandin_occupied = True
                    actions.append({
                                   "Action": "Cast",
                                   "CharacterId": character.id,
                                   # Am I buffing or debuffing? If buffing, target myself
                                   "TargetId": character.id,
                                   "AbilityId": 0
                    })
                    cast = True
            if character.can_use_ability(3):
                if lowest_Health.attributes.get_attribute("Health") <= 900:
                    
                    if character.in_ability_range_of(lowest_Health, gameMap, 3) and not character.attributes.get_attribute("Silenced") and not palandin_occupied:
                        #print "healed " + str(lowest_Health.id)
                        palandin_occupied = True
                        actions.append({
                                       "Action": "Cast",
                                       "CharacterId": character.id,
                                       # Am I buffing or debuffing? If buffing, target myself
                                       "TargetId": lowest_Health.id,
                                       "AbilityId": 3
                        })
                        cast = True

                    elif not palandin_occupied:
                        palandin_occupied = True
                        #print lowest_Health.attributes.get_attribute("Health")
                        actions.append({
                                       "Action": "Move",
                                       "CharacterId": character.id,
                                       # Am I buffing or debuffing? If buffing, target myself
                                       "TargetId": lowest_Health.id
                        })
            if not cast and inRangeOfAnyEnemy(character, enemyteam) and not palandin_occupied:
                palandin_occupied = True
                print "pal attack"
                actions.append({
                    "Action": "Attack",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })
            elif not palandin_occupied: # Not in range, move towards
                palandin_occupied = True
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })
    #print actions
    # Send actions to the server
    return {
            'TeamName': teamName,
            'Actions': actions
    }

def abilityCalled(abilID, enemyteam):
        array = []
        for enemy in enemyteam:
            #print enemy.casting
            if (not enemy.casting == None and enemy.casting.get("AbilityId") == abilID) or shouldHoldOffOnStuns(enemyteam) == False:
                array.append(enemy) 
        return array

#assumes enemies in array are about to cast
def stunAll(myteam, enemArray):
    things_to_do = []
    for character in myteam:
            for enemy in enemArray:
                if not enemy.is_dead():
                    if character.can_use_ability(1) and character.in_ability_range_of(enemy, gameMap, 1) and not enemy.attributes.get_attribute('Stunned'):
                        things_to_do.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": enemy.id,
                            "AbilityId": 1
                        })
                        print "stun 1" + str(enemy.id)
                        enemArray.remove(enemy)
                    if character.can_use_ability(14) and character.in_ability_range_of(enemy, gameMap, 10) and not enemy.attributes.get_attribute('Stunned'):
                        things_to_do.append({
                            "Action": "Cast",
                            "CharacterId": character.id,
                            "TargetId": enemy.id,
                            "AbilityId": 14
                        })
                        print "stun 10"
    return things_to_do

def inAbilityRangeOfAnyEnemy(myChar, enemyteam, abilityId):
    for enemy in enemyteam:
        if myChar.in_ability_range_of(enemy, gameMap, abilityId):
            return True
    return False

def inRangeOfAnyEnemy(myChar, enemyteam):
    for enemy in enemyteam:
        if myChar.in_range_of(enemy, gameMap):
            return True
    return False

def shouldHoldOffOnStuns(enemyteam):
    for enemy in enemyteam:
        if not enemy.is_dead():
            if enemy.classId == "Druid" or enemy.classId == "Paladin":
                return True
    return False

def canCastOnAny(myteam, enemyteam, abilityId):
    for character in myteam:
        for enemy in enemyteam:
            if character.in_ability_range_of(enemy, gameMap, abilityId) and character.can_use_ability(abilityId):
                return True
    return False

#if warrior, if ability called is heal and you can cast your stun, cast stun on personsho called heal
#else if you're stunned, and can cast burst, burst
#else if your enemy is in range, attack,
#else move

def first_nondead_enemy(arr):
    for x in arr:
        if not x.is_dead():
            return x


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
