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
teamName = "chunks"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Lady Gaga",
                 "ClassId": "Archer"},
                {"CharacterName": "A Goose",
                 "ClassId": "Warrior"},
                {"CharacterName": "Russell",
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
    
    target = None 
    e0 = enemyteam[0].attributes.get_attribute("MaxHealth")
    e1 = enemyteam[1].attributes.get_attribute("MaxHealth")
    e2 = enemyteam[2].attributes.get_attribute("MaxHealth")
    r0 = enemyteam[0].attributes.get_attribute("AttackRange")
    r1 = enemyteam[0].attributes.get_attribute("AttackRange")
    r2 = enemyteam[0].attributes.get_attribute("AttackRange")
    

    if e0!= e1 and e0 != e2 and e1 != e2: 
        if enemyteam[0].attributes.get_attribute("MaxHealth") > enemyteam[1].attributes.get_attribute("MaxHealth"): 
                if not enemyteam[1].is_dead(): 
                    target = enemyteam[1]
                elif not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                else: 
                    target = enemyteam[2]

        if target.attributes.get_attribute("MaxHealth") > enemyteam[2].attributes.get_attribute("MaxHealth"): 
                if not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
                else: 
                    target = target      

        # ----- duplicate attack instances --- -- 
    else: 
        if e0 == e1: # first similary condition ----
            if e0 > e2: 
                if not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
                elif not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                elif not enemyteam[1].is_dead(): 
                    target = enemyteam[1]    
            else: 
                if not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
                elif not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                elif not enemyteam[1].is_dead(): 
                    target = enemyteam[1]

        elif e0 == e2: # second similary condition ----
            if e0 > e1: 
                if not enemyteam[1].is_dead(): 
                    target = enemyteam[1]
                elif not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                elif not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
            else: 
                if not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                elif not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
                elif not enemyteam[1].is_dead(): 
                    target = enemyteam[1]

        elif e1 == e2:  # third similary condition ----   
            if e1 > e0: 
                if not enemyteam[0].is_dead(): 
                    target = enemyteam[0]
                elif not enemyteam[1].is_dead(): 
                    target = enemyteam[1]
                elif not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
            else: 
                if not enemyteam[1].is_dead(): 
                    target = enemyteam[1]
                elif not enemyteam[2].is_dead(): 
                    target = enemyteam[2]
                elif not enemyteam[0].is_dead(): 
                    target = enemyteam[0]


# --- move ----
    def move(sprite, to): 
        if sprite: 
            if to == "targ": 
                actions.append({
                            "Action": "Move",
                            "CharacterId": sprite.id,
                            "TargetId": target.id,
                        }) 
            elif to == "loc":    
                actions.append({
                            "Action": "Move",
                            "CharacterId": sprite.id,
                            "Location": pos[0]
                        }) 
# --- cast spell ----
    def castSpell(sprite, spellId): 
        if target: 
            if sprite: 
                if sprite.in_range_of(target, gameMap): 
                    if sprite.casting is None: 
                        ability = game_consts.abilitiesList[spellId]
                        if sprite.can_use_ability(spellId): 
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": sprite.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else sprite.id,
                                "AbilityId": spellId
                            }) 
                        else: 
                            attack(sprite)

                else: 
                    move(sprite, "targ")
    
# --- attack ----  
    def attack(sprite): 
        if sprite: 
            if sprite.in_range_of(target, gameMap): 
                actions.append({
                                "Action": "Attack",
                                "CharacterId": sprite.id,
                                "TargetId": target.id
                            }) 
            else: 
                move(sprite, "targ")

# -- avoid ----  
    def avoid(sprite): 
        pos = gameMap.get_valid_adjacent_pos(sprite.position) 
        actions.append({
            "Action": "Move", 
            "CharacterId": sprite.id, 
            "Location": pos[1]
        }) 

    

    if myteam[0].attributes.get_attribute("Stunned") == 1 or myteam[0].attributes.get_attribute("Rooted") == 1:
	    castSpell(myteam[0],0)

    if myteam[1].attributes.get_attribute("Stunned") == 1 or myteam[1].attributes.get_attribute("Rooted") == 1:
	    castSpell(myteam[1],0)
        
    if myteam[2].attributes.get_attribute("Stunned") == 1 or myteam[2].attributes.get_attribute("Rooted") == 1:
	    castSpell(myteam[2],0)

        
    
    castSpell(myteam[1],12)
    castSpell(myteam[2],1)

    if enemyteam[0].in_range_of(myteam[0], gameMap) or enemyteam[1].in_range_of(myteam[0], gameMap) or enemyteam[2].in_range_of(myteam[0], gameMap): 
        if enemyteam[0].in_range_of(myteam[0], gameMap) and r0 < 1: 
            avoid(myteam[0]) 
        elif enemyteam[1].in_range_of(myteam[0], gameMap) and r1 < 1:  
            avoid(myteam[0]) 
        elif enemyteam[2].in_range_of(myteam[0], gameMap) and r2 < 1: 
            avoid(myteam[0]) 
        else: 
            castSpell(myteam[0],11)

    else: 
        castSpell(myteam[0],11)

    
    
# --- Send actions to the server ---
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
