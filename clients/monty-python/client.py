#!/usr/bin/python2
import socket
import json
import os
import random
import math
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
teamName = "monty-python"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
    processTurn.turn_count = 0

# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "King Arthur",
                 "ClassId": "Archer"},
                {"CharacterName": "BlackKnight",
                 "ClassId": "Archer"},
                {"CharacterName": "Lancelot",
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

    processTurn.turn_count += 1

    def get_priority(enemies):
        PRIORITY_LIST = ["Assassin", "Sorcerer", "Wizard", "Enchanter", "Archer", "Paladin", "Druid", "Warrior"]
        lowest_priorities = []

        for enemy in enemies:
            if len(lowest_priorities) == 0:
                lowest_priorities.append(enemy)
                continue

            old_priority = PRIORITY_LIST.index(lowest_priorities[0].classId)
            new_priority = PRIORITY_LIST.index(enemy.classId)

            if new_priority <= old_priority:
                if new_priority < old_priority:
                    lowest_priorities = []
                lowest_priorities.append(enemy)

        lowest_health = lowest_priorities[0]
        for enemy in lowest_priorities:
            if enemy.attributes.get_attribute("Health") < lowest_health.attributes.get_attribute("Health"):
                lowest_health = enemy

        return lowest_health

    def evaluate(first_pass):
        # All characters are on the same spot
        one = None
        for character in myteam:
            if not character.is_dead():
                one = character
                break

        if one:
            targets = []
            for character in enemyteam:
                if not character.is_dead() and one.in_range_of(character, gameMap):
                    targets.append(character)

            if len(targets) > 0:
                priority_enemy = get_priority(targets)

                total_damage = 0
                total_debuff = 0
                characters_to_cast = {}

                # Determine the max total debuff we can apply
                for character in myteam:
                    # Add up the damage each character could do
                    if not character.is_dead() and not character.attributes.get_attribute("Stunned"):
                        total_damage += character.attributes.get_attribute("Damage") - priority_enemy.attributes.get_attribute("Armor")

                    if character.can_use_ability(2) and total_debuff < priority_enemy.attributes.get_attribute("Armor"):
                        total_debuff -= game_consts.abilitiesList[2]["StatChanges"][0]["Change"]
                        characters_to_cast[character.id] = True
                    else:
                        characters_to_cast[character.id] = False

                if total_damage == 0:
                    should_debuff = False
                else:
                    turns_to_kill_no_debuff = math.ceil(priority_enemy.attributes.get_attribute("Health") / total_damage)
                    turns_to_kill_debuff = math.ceil((priority_enemy.attributes.get_attribute("Health")) / (total_damage + total_debuff) + 1)
                    should_debuff = turns_to_kill_debuff < turns_to_kill_no_debuff

                # Decide if each character should debuff or attack
                for character in list(myteam):
                    if not character.is_dead() and not character.attributes.get_attribute("Stunned"):
                        if should_debuff and characters_to_cast[character.id]:
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": priority_enemy.id,
                                "AbilityId": 2
                            })
                        else:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": priority_enemy.id,
                            })

                            # Update enemy health
                            enemyteam[enemyteam.index(priority_enemy)].attributes.health -= character.attributes.get_attribute("Damage") - priority_enemy.attributes.get_attribute("Armor")

                        myteam.remove(character)
                        if enemyteam[enemyteam.index(priority_enemy)].is_dead():
                            evaluate(False)
                            break

            elif first_pass:

                one = None
                for character in myteam:
                    if not character.is_dead():
                        one = character
                        break

                if one.attributes.get_attribute("MovementSpeed") > 1:

                    valid_positions = gameMap.get_valid_adjacent_pos(one.position)

                    new_valid_positions = []

                    for valid_position in valid_positions:
                        new_valid_positions.extend(gameMap.get_valid_adjacent_pos(valid_position))

                    new_best_position = one.position
                    for valid_position in new_valid_positions:
                        new_distance = get_closest_enemy(valid_position)

                        if new_distance > get_closest_enemy(new_best_position):
                            new_best_position = valid_position

                    for character in myteam:
                        actions.append({
                            "Action": "Move",
                            "CharacterId": character.id,
                            "Location": new_best_position,
                        })
                else:
                    enemy_is_sprinting = False
                    for enemy in enemyteam:
                        if not enemy.is_dead() and enemy.attributes.get_attribute("MovementSpeed") > 1:
                            enemy_is_sprinting = True

                    if enemy_is_sprinting:
                        for character in myteam:
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                "TargetId": character.id,
                                "AbilityId": 12
                            })

                    elif processTurn.turn_count > 120:
                        target = get_priority(enemyteam)

                        for character in myteam:
                            actions.append({
                                "Action": "Move",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })


    def get_closest_enemy(position):
        closest_distance = 100
        for enemy in enemyteam:
            if not enemy.is_dead():
                distance = len(gameMap.bfs(position, enemy.position))
                if distance < closest_distance:
                    closest_distance = distance

        return closest_distance

    evaluate(True)

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
