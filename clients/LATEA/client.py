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
teamName = "LATEA"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "BParmFries",
                 "ClassId": "Assassin"},
                {"CharacterName": "QSwtHazlnut",
                 "ClassId": "Assassin"},
                {"CharacterName": "NSwtRose",
                 "ClassId": "Assassin"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    best_positions = [(0, 4), (2, 2), (4, 0)]
    turn_count = serverResponse["TurnNumber"]

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
    # target = None
    # for character in enemyteam:
    #     if not character.is_dead():
    #         target = character
    #         break

    target = None

    for character in myteam:
        same_spot_enemies = []
        archer_enemies = []
        target = None
        for enemy in enemyteam:
            if get_distance(character.position, enemy) == 0 and not enemy.is_dead():
                same_spot_enemies.append(enemy)
            if enemy.classId == "Archer" and not enemy.is_dead():
                archer_enemies.append(enemy)

        if len(same_spot_enemies) != 0:
            #print('samespot')
            lowest_health = 999999999
            for enemy in same_spot_enemies:
                if enemy.attributes.get_attribute("Health") < lowest_health:
                    lowest_health = enemy.attributes.get_attribute("Health")
                    target = enemy 

        if (character.attributes.get_attribute("Stunned") and character.can_use_ability(0)):
            #print('cleanse')
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 0
                })

        elif (get_furthest_position(character, myteam) != character.position):
            #print('timetoreturnhome')
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "Location": get_furthest_position(character, myteam)
                })

        elif target:
            if character.can_use_ability(11):
                #print(target.id)
                #print('backstabthatho')
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                    "AbilityId": 11
                    })
            elif character.abilities[12] == 5:
                #print('bounce')
                actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": avoid_enemies(avoid_enemies(character.position, enemyteam), enemyteam),
                            })
            else:
                #print('hitthatsht')
                actions.append({
                    "Action": "Attack",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                    })

        elif (character.attributes.get_attribute("Rooted") and character.can_use_ability(0)):
            #print('cleanse')
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 0
            })
        elif character.can_use_ability(12):
            #print('sprint')
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 12
                }) 

        elif len(archer_enemies) != 0:
            #print('gangbangthem')
            lowest_health = 999999999
            for enemy in archer_enemies:
                if enemy.attributes.get_attribute("Health") < lowest_health:
                    lowest_health = enemy.attributes.get_attribute("Health")
                    target = enemy
            if target:
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id
                    })   
        elif (get_living_characters(myteam) > get_living_characters(enemyteam) or turn_count >= 120):
            #print('gangbangthem')
            lowest_health = 999999999
            target = None
            for enemy in enemyteam:
                if enemy.attributes.get_attribute("Health") < lowest_health and not enemy.is_dead():
                    lowest_health = enemy.attributes.get_attribute("Health")
                    target = enemy
            if target:
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id
                    })    
        else:
            if character.attributes.get_attribute("MovementSpeed") > 1:
                if character.abilities[12] == 7:
                    nearby_enemies = []
                    target = None
                    for enemy in enemyteam:
                        if get_distance(character.position, enemy) <= 2:
                            nearby_enemies.append(enemy)
                    for enemy in nearby_enemies:
                        lowest_health = 9999999999
                        if enemy.attributes.get_attribute("Health") <= lowest_health:
                            lowest_health = enemy.attributes.get_attribute("Health")
                            target = enemy
                    if target:
                        #print('ballsack')
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "TargetId": target.id
                            })
                    else:
                        #print('antiballsack')
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": avoid_enemies(avoid_enemies(character.position, enemyteam), enemyteam),
                            })
                else:
                    #print('superantiballsack')
                    actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": avoid_enemies(avoid_enemies(character.position, enemyteam), enemyteam),
                            })

            else:
                #print('supersuperantiballsack')
                actions.append({
                "Action": "Move", 
                "CharacterId": character.id,
                "Location": avoid_enemies(character.position, enemyteam),
                })

    # if turn_count < 5:
    #     for character_index in range(len(myteam)):
    #         actions.append({
    #             "Action": "Move",
    #             "CharacterId": myteam[character_index].id,
    #             "Location": best_positions[character_index],
    #             })
    # If we found a target
    # if target:
    #     for character in myteam:
    #         # If I am in range, either move towards target
    #         if character.in_range_of(target, gameMap):
    #             # Am I already trying to cast something?
    #             if character.casting is None:
    #                 cast = False
    #                 for abilityId, cooldown in character.abilities.items():
    #                     # Do I have an ability not on cooldown
    #                     if cooldown == 0:
    #                         # If I can, then cast it
    #                         ability = game_consts.abilitiesList[int(abilityId)]
    #                         # Get ability
    #                         actions.append({
    #                             "Action": "Cast",
    #                             "CharacterId": character.id,
    #                             # Am I buffing or debuffing? If buffing, target myself
    #                             "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
    #                             "AbilityId": int(abilityId)
    #                         })
    #                         cast = True
    #                         break
    #                 # Was I able to cast something? Either wise attack
    #                 if not cast:
    #                     actions.append({
    #                         "Action": "Attack",
    #                         "CharacterId": character.id,
    #                         "TargetId": target.id,
    #                     })
    #         else: # Not in range, move towards
    #             actions.append({
    #                 "Action": "Move",
    #                 "CharacterId": character.id,
    #                 "TargetId": target.id,
    #             })

    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------


def get_distance(position, enemy):
    return abs(position[0] - enemy.position[0]) + abs(position[1] - enemy.position[1])

def get_total_distance(position, enemies):
    sum = 0
    counter = 0
    for enemy in enemies:
        if not enemy.is_dead():
            sum += get_distance(position, enemy)
            counter += 1
    if counter == 0:
        counter = 4
    return sum / float(counter)

def get_distance_to_middle(position):
    return abs(position[0] - 2) + abs(position[1] -2)

def avoid_enemies(position, enemies):
    down = (position[0], position[1] + 1)
    up = (position[0], position[1] - 1)
    left = (position[0] - 1, position[1])
    right = (position[0] + 1, position[1])
    not_move = position

    possible_positions = [not_move, down, up, left, right]
    best_move = possible_positions[0]
    best_distance = 0.0
    for position in possible_positions:
        if is_valid_position(position):
            if get_total_distance(position, enemies) > best_distance:
                best_distance = get_total_distance(position, enemies)
                best_move = position
            elif get_total_distance(position, enemies) == best_distance:
                #print('pee')
                if get_distance_to_middle(position) < get_distance_to_middle(best_move):
                    best_move = position
                    #print('poo')

    return best_move


def is_valid_position(position):
    if position[0] < 0 or position[0] > 4:
        return False
    if position[1] < 0 or position[1] > 4:
        return False
    if position == (1, 1) or position == (3, 1) or position == (1, 3) or position == (3, 3):
        return False
    return True

def get_furthest_position(me, team):
    furthest_position = me.position
    furthest_distance = 0
    furthest_char = me
    for character in team:
        if get_distance(me.position, character) > furthest_distance and not character.is_dead():
            furthest_char = character
            furthest_distance = get_distance(me.position, character)
            furthest_position = ((character.position[0] + me.position[0])/2,(character.position[1] + me.position[1])/2)
    if is_valid_position(furthest_position):
        return furthest_position
    else:
        return furthest_char.position

def get_living_characters(team):
    counter = 0
    for character in team:
        if not character.is_dead():
            counter += 1
    return counter

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
