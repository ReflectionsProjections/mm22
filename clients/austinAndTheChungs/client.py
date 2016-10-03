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
teamName = "austinAndTheChungs"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Scrub1",
                 "ClassId": "Archer"},
                {"CharacterName": "Scrub2",
                 "ClassId": "Archer"},
                {"CharacterName": "Scrub3",
                 "ClassId": "Archer"},
            ]}
# ---------------------------------------------------------------------

def archerMove(Archer, MoveMap, archerLow):
    maxTile = None
    maxFarTile = None
    for tile in MoveMap:
        if gameMap.can_move_to(Archer.position, tile, Archer.attributes.get_attribute("MovementSpeed") + 1):
            #print "ewwertyu ", tile
            if not maxTile:
                maxTile = tile
            elif MoveMap[maxTile] < MoveMap[tile]:
                maxTile = tile
        if not maxFarTile:
            maxFarTile = tile
        elif MoveMap[maxFarTile] < MoveMap[tile]:
            maxFarTile = tile
    if maxTile:
        #print "Vehje5 ", maxTile
        if MoveMap[maxTile] > MoveMap[Archer.position] and archerLow:
            #print Archer.name , " moves to ", maxTile
            return {
                "Action": "Move",
                "CharacterId": Archer.id,
                "Location": maxFarTile,
            }
        elif MoveMap[maxTile] > MoveMap[Archer.position] + 100:
            #print "Moving"
            #print Archer.name , " moves to ", maxTile
            return {
                "Action": "Move",
                "CharacterId": Archer.id,
                "Location": maxTile,
            }
        elif maxFarTile:
            cast = False
            if Archer.casting is None:
                for abilityId, cooldown in Archer.abilities.items():
                    # Do I have an ability not on cooldown
                    if cooldown == 0 and int(abilityId) == 12 and Archer.attributes.get_attribute("MovementSpeed") == 1:
                        # If I can, then cast it
                        ability = game_consts.abilitiesList[int(abilityId)]
                        # Get ability
                        #print Archer.name , " casts Sprint"
                        return {
                            "Action": "Cast",
                            "CharacterId": Archer.id,
                            "TargetId": Archer.id,
                            "AbilityId" : 12 #sprint,
                        }
            if not cast:
                #print Archer.name , " moves toward ", maxFarTile
                return {
                    "Action": "Move",
                    "CharacterId": Archer.id,
                    "Location": maxFarTile,
                }
    else:
        #print Archer.name , " moves toward ", maxFarTile
        return {
            "Action": "Move",
            "CharacterId": Archer.id,
            "Location": maxFarTile,
        }
    
        
def archerAttack(Archer, enemyteam):
    priority = {}
    class_priority = {
        "Druid" : 1,
        "Assassin" : 2,
        "Sorcerer" : 3,
        "Archer"   : 4,
        "Enchanter": 5,
        "Wizard"   : 6,
        "Warrior"  : 7,
        "Paladin"  : 8
    }
    for enemy in enemyteam:
        if not enemy.is_dead():
            target = 0

            target -= class_priority[enemy.classId] * 175;
            target -= enemy.attributes.get_attribute("Health") / 20
            
            damage_potential = Archer.attributes.get_attribute("Damage") - enemy.attributes.get_attribute("Armor")
            if damage_potential > enemy.attributes.get_attribute("Health"):
                target += 2000
            elif damage_potential*3 > enemy.attributes.get_attribute("Health"):
                target += 300
            
            if enemy.attributes.get_attribute("Stunned"):
                target += 300
            if enemy.attributes.get_attribute("Rooted"):
                target += 300
            
            if enemy.casting != None:
                target += 100
            
            priority[enemy] = target
    
    targetEnemy = None    
    for enemy in priority:
        if Archer.in_range_of(enemy, gameMap):
            if not targetEnemy:
                targetEnemy = enemy
            elif priority[enemy] > priority[targetEnemy]:
                targetEnemy = enemy
    
    if targetEnemy:
        #print Archer.name , " attacks ", targetEnemy.name
        return {
            "Action": "Attack",
            "CharacterId": Archer.id,
            "TargetId": targetEnemy.id,
        }
    else:
        return None
        
def archerMoveMap(Archer, Druid, Warrior, enemyteam):
    MoveMap = {
        (0,0): 0, (0,1): 0, (0,2): 0, (0,3): 0, (0,4): 0, 
        (1,0): 0, (1,2): 0, (1,4): 0,
        (2,0): 0, (2,1): 0, (2,2): 0, (2,3): 0, (2,4): 0,
        (3,0): 0, (3,2): 0, (3,4): 0,
        (4,0): 0, (4,1): 0, (4,2): 0, (4,3): 0, (4,4): 0,
    }
    
    for enemy in enemyteam:
        if not enemy.is_dead():
            enemy_damage_potential = enemy.attributes.get_attribute("Damage") - Archer.attributes.get_attribute("Armor")
            enemy_danger = enemy_damage_potential
            damage_potential = Archer.attributes.get_attribute("Damage") - enemy.attributes.get_attribute("Armor")
            aggro = damage_potential
            if enemy_damage_potential*5 > Archer.attributes.get_attribute("Health"):
                enemy_danger *= 30
                aggro = 0
            elif enemy_damage_potential*10 > Archer.attributes.get_attribute("Health"):
                enemy_danger *= 2
            #print enemy.name

            for tile in MoveMap:
                path = gameMap.bfs(enemy.position, tile)
                dist = len(path)
                if enemy.position == tile:
                    MoveMap[tile] -= enemy_danger * 3 / 4
                    if enemy_damage_potential*10 > Archer.attributes.get_attribute("Health"):
                        MoveMap[tile] -= enemy_danger * 3
                if dist <= enemy.attributes.get_attribute("AttackRange"):
                    MoveMap[tile] -= enemy_danger * 2 
                    MoveMap[tile] += enemy_danger * dist / (enemy.attributes.get_attribute("AttackRange") * 2) 
                elif dist <= enemy.attributes.get_attribute("AttackRange") + enemy.attributes.get_attribute("MovementSpeed"):
                    MoveMap[tile] -= enemy_danger / 2
                    MoveMap[tile] += enemy_danger * (dist - enemy.attributes.get_attribute("AttackRange")) / (enemy.attributes.get_attribute("MovementSpeed") * 2) 
                #if gameMap.in_vision_of(enemy.position, tile, enemy.attributes.get_attribute("AttackRange")):
                #    print tile
                #    MoveMap[tile] -= enemy_danger / 2
                #if gameMap.in_vision_of(enemy.position, tile, enemy.attributes.get_attribute("AttackRange") + enemy.attributes.get_attribute("MovementSpeed")):
                #    print tile, "Safw"
                #    MoveMap[tile] -= enemy_danger / 2
                if gameMap.in_vision_of(tile, enemy.position, Archer.attributes.get_attribute("AttackRange")):
                    #print tile
                        MoveMap[tile] += aggro
    
    #MoveMap[Warrior.position] += 50
    #MoveMap[Druid.position] += 80
    #for pos in gameMap.get_valid_adjacent_pos(Druid.position):
    #    MoveMap[pos] += 80
        
    #for key in MoveMap:
    #    print key, " : ", MoveMap[key]
        
    return MoveMap
    
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

    Archer = None
    Druid = None
    Warrior = None
    archer_is_moving = False
    ARCHER_LOW_THRESHOLD = 400
    # Find the Archer
    #print "Turn ", serverResponse["TurnNumber"], '\n'
    for character in myteam:
        #if character.is_dead():
            #print character.name, " is dead"
        if character.classId == "Archer":
            Archer = character
        if character.classId == "Druid":
            Druid = character
        if character.classId == "Warrior":
            Warrior = character

        targets = []
        MoveMap = archerMoveMap(Archer, Druid, Warrior, enemyteam)
        archer_move = archerMove(Archer, MoveMap, Archer.attributes.get_attribute("Health") < ARCHER_LOW_THRESHOLD)
        archer_move_sq = Archer.position
        if "Location" in archer_move:
            archer_move_sq = archer_move["Location"] 
        archer_attack = archerAttack(Archer, enemyteam)
        # print Archer.position, MoveMap[Archer.position], " vs ", archer_move_sq, MoveMap[archer_move_sq] 
        if not archer_attack:
            actions.append(archer_move)
            archer_is_moving = True
        elif MoveMap[Archer.position] < MoveMap[archer_move_sq]:
            actions.append(archer_move)
            #print Archer.name, " moves"
            archer_is_moving = True
        else:
            actions.append(archer_attack)
            # print archer_attack
            #print Archer.name, " attacks"


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
