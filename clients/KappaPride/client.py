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
teamName = "KappaPride"
# ---------------------------------------------------------------------
def calculate_dist(guy1,guy2):
    guy1_x=guy1.position[0]
    guy1_y=guy1.position[1]
    guy2_x=guy2.position[0]
    guy2_y=guy2.position[1]
    return abs(guy2_y-guy1_y)+abs(guy2_x-guy1_x)

def target_val(target, myteam):

    targetVal = 0
    
    if target.is_dead():
        deathMod = 0
    else:
        deathMod = 1

    for character in myteam:  
        if character.attributes.get_attribute('Stunned'):
            stunMod = 0.5
        else:
            stunMod = 1
                          
        if calculate_dist(character, target) < character.attributes.get_attribute('AttackRange'):
            rootMod = 1
        elif character.attributes.get_attribute('Rooted'):
            rootMod = 0.8 
        else:
            rootMod = 1

        threat = (target.attributes.get_attribute('Damage') + target.attributes.get_attribute('SpellPower')) / max((character.attributes.get_attribute('Damage') + character.attributes.get_attribute('SpellPower')), 1)
       
        vuln = (character.attributes.get_attribute('Damage') - target.attributes.get_attribute('Armor')) / max((target.attributes.get_attribute('Damage') - character.attributes.get_attribute('Armor')), 1)

        sizeDiff = 0
        if not character.is_dead():
            sizeDiff = character.attributes.get_attribute('Health') / max(target.attributes.get_attribute('Health'), 1)
    
        targetVal = targetVal + (threat + vuln * stunMod * rootMod + sizeDiff)* deathMod

    return targetVal

def mostValuableID(myteam, enemyteam):
    enemyteam_val = []
    target = None
    for character in enemyteam:
        enemyteam_val.append(target_val(character, myteam))
        #print(target_val(character, myteam))

    #print(len(enemyteam_val))

    mostValTarget_val = -100000

    for x in xrange(len(enemyteam_val)):
        if(enemyteam_val[x] >= mostValTarget_val):
            target = enemyteam[x]
            mostValTarget_val = enemyteam_val[x]
    return target


def range_matrix(myteam, enemyteam):

    our_range_matrix = [[0 for x in range(3)] for y in range(3)] 
    enemy_range_matrix = [[0 for x in range(3)] for y in range(3)] 
    num_member_in_enemy_range = [0 for x in range(3)]
    num_enemy_in_member_range = [0 for x in range(3)]
    
    for i in xrange(3):
        for j in xrange(3):
            if not myteam[i].is_dead() and not enemyteam[j].is_dead():
                if myteam[i].in_range_of(enemyteam[j],gameMap):
                    our_range_matrix[i][j] =  1 
                    num_enemy_in_member_range[i] = num_enemy_in_member_range[i] + 1
                if enemyteam[j].in_range_of(myteam[i],gameMap):
                    enemy_range_matrix[j][i] =  1 
                    num_member_in_enemy_range[i] = num_member_in_enemy_range[i] + 1 
            else:
                    our_range_matrix[i][j] =  0
                    enemy_range_matrix[j][i] = 0 


    return [our_range_matrix, enemy_range_matrix, num_member_in_enemy_range, num_enemy_in_member_range]


def warriror_decesion(idx,myteam,enemyteam):
    warrior = myteam[idx]
    characterId = warrior.id

    target    = mostValuableID(myteam,enemyteam)
    attack_id = mostValuableID(myteam, enemyteam).id

    #rangess   = range_matrix()

    if warrior.casting != None:
        return {}

    if warrior.attributes.get_attribute("Stunned") <0 :  
        if warrior.can_use_ability(0):
            return {"CharacterId": characterId,"Action": "Cast", "TargetId": characterId, "AbilityId": 0}

    

    if warrior.can_use_ability(15) and calculate_dist(warrior,target) == 4:return {"CharacterId": characterId,"Action": "Cast", "TargetId":characterId , "AbilityId": 15}
            
    if warrior.in_range_of(target, gameMap) == True :
        if warrior.can_use_ability(1) and target.attributes.get_attribute("Stunned") >=0:
            return {"CharacterId": characterId,"Action": "Cast", "TargetId": attack_id, "AbilityId": 1}
        else:
            return {"CharacterId": characterId,"Action": "Attack","TargetId": attack_id}
    else:
        return {"CharacterId": characterId, "Action": "Move",   "TargetId": attack_id }

def team_need_heal(myteam):
    for character in myteam:
        if character.attributes.get_attribute('Health')/character.attributes.get_attribute('MaxHealth') < .75:
            return True
    return False

def dying_char(myteam):
    for character in myteam:
        if character.attributes.get_attribute('Health')/character.attributes.get_attribute('MaxHealth') < .75:
            return character

    
def paladin_decision(idx,myteam,enemyteam):
    paladin = myteam[idx]
    characterId = paladin.id

    target    = mostValuableID(myteam,enemyteam)
    attack_id = mostValuableID(myteam, enemyteam).id

    #rangess   = range_matrix()

    if paladin.casting != None:
        return {}

    if paladin.attributes.get_attribute("Stunned") <0 :  
        if paladin.can_use_ability(0):
            return {"CharacterId": characterId,"Action": "Cast", "TargetId": characterId, "AbilityId": 0}

    if team_need_heal(myteam):
        dyingMem = dying_char(myteam)
        if paladin.in_ability_range_of(dyingMem, gameMap, 3) == True :
            if paladin.can_use_ability(3):
                return {"CharacterId": characterId,"Action": "Cast", "TargetId": dyingMem.id, "AbilityId": 3}
 

    if paladin.in_ability_range_of(target, gameMap, 14) == True :
        if paladin.can_use_ability(14) and (paladin.abilities[14] == 0):
            if not target.attributes.get_attribute('Stunned'):
                return {"CharacterId": characterId,"Action": "Cast", "TargetId": attack_id, "AbilityId": 14}
    #else:
     #   return {"CharacterId": characterId, "Action": "Move", "TargetId": attack_id }

    if paladin.in_range_of(target, gameMap) == True :
        return {"CharacterId": characterId,"Action": "Attack","TargetId": attack_id}
    else:
        return {"CharacterId": characterId, "Action": "Move",   "TargetId": attack_id }

def assasin_decesion(idx,myteam,enemyteam):
    assasin = myteam[idx]
    characterId = assasin.id

    target    = mostValuableID(myteam,enemyteam)
    attack_id = mostValuableID(myteam, enemyteam).id

    if assasin.attributes.get_attribute("Stunned") <0 or assasin.attributes.get_attribute("Rooted") <0 :  
        if assasin.can_use_ability(0):
            return {"CharacterId": characterId,"Action": "Cast", "TargetId": characterId, "AbilityId": 0}

    if assasin.can_use_ability(11) and assasin.in_range_of(target,gameMap):
        return {"CharacterId": characterId,"Action": "Cast", "TargetId": attack_id, "AbilityId": 11}

    if assasin.can_use_ability(12) and calculate_dist(assasin,target)>=2:
        return {"CharacterId": characterId,"Action": "Cast", "TargetId": characterId, "AbilityId": 12}

    if assasin.in_range_of(target,gameMap):
        return {"CharacterId": characterId,"Action": "Attack","TargetId": attack_id}
    else:
        return {"CharacterId": characterId, "Action": "Move",   "TargetId": attack_id }

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Draius",
                 "ClassId": "Warrior"},
                {"CharacterName": "Jayce",
                 "ClassId": "Paladin"},
                {"CharacterName": "Garen",
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

    # Choose a 
   

    actions_test_team = []
    target = None
    for character in enemyteam:
        if not character.is_dead():
            target = character
            break

    actions_test_team.append(warriror_decesion(2,myteam,enemyteam))
    actions_test_team.append(paladin_decision(1,myteam,enemyteam))
    actions_test_team.append(warriror_decesion(0,myteam,enemyteam))
 

    # Send actions to the server
    return {
        'TeamName': teamName,
        #'Actions': actions
        'Actions':  actions_test_team
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
