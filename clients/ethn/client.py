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
teamName = "ethn"
# ---------------------------------------------------------------------





def adjWalkable(loc):
    x = loc[0]
    y = loc[1]
    adjWalkable = {(x+1,y), (x-1,y), (x,y+1), (x,y-1)}

    # discard out of bounds
    if (x+1) > 4: adjWalkable.discard((x+1,y))
    if (x-1) < 0: adjWalkable.discard((x-1,y))
    if (y+1) > 4: adjWalkable.discard((x,y+1))
    if (y-1) < 0: adjWalkable.discard((x,y-1))
    
    # discard pillars
    adjWalkable.discard((1,1))
    adjWalkable.discard((1,3))
    adjWalkable.discard((3,1))
    adjWalkable.discard((3,3))

    return adjWalkable

def distance(loc1, loc2):   # calculate distance accounting for pillars
    # print ("bfs",gameMap.bfs(loc1, loc2))
    return len(gameMap.bfs(tuple(loc1), tuple(loc2)))-1

def numAlive(team):
    return sum([(not character.is_dead()) for character in team])

def nearestAdjCharInfo(loc, team):  # input is a tuple specifying reference location
    enemy_positions = [(distance(enemy.position, loc), enemy.position) for enemy in team if not enemy.is_dead()]
    sorted(enemy_positions, key=lambda x: x[0]) # sorts list of tuples by first entry in each tuple

    for (dist, enemy_pos) in enemy_positions:
        if dist != 0:
            return {"dist":dist, "pos":enemy_pos} # return closest enemy's location that is NOT on your square

    return None # no enemies exist outside of your square

def nearestCharInfo(loc, team):  # input is a tuple specifying reference location
    enemy_positions = [(distance(enemy.position, loc), enemy.position) for enemy in team if not enemy.is_dead()]
    sorted(enemy_positions, key=lambda x: x[0]) # sorts list of tuples by first entry in each tuple

    for (dist, enemy_pos) in enemy_positions:
        return {"dist":dist, "pos":enemy_pos} # return closest enemy's location that is NOT on your square

    return None # no enemies exist; shouldn't happen


def away(loc, myteam, enemyteam):   # move away from enemyteam, and ideally toward team
    bestmoves = set()
    for move in adjWalkable(loc):
        if nearestCharInfo(move, enemyteam)["dist"] > nearestCharInfo(loc, enemyteam)["dist"]:
            bestmoves.add(move)

    for move in bestmoves:
        if nearestCharInfo(move, myteam)["dist"] <= nearestCharInfo(loc, myteam)["dist"]:
            return move


    if bestmoves == set():
        return loc
    return list(bestmoves)[0]

def hasNewDebuff(character):
    for debuff in character.debuffs:
        if debuff["Attribute"] == "Stunned" and debuff["Time"] in {1,2}:
            return True
        elif debuff["Attribute"] == "Silenced" and debuff["Time"] in {2,3}:
            return True
        elif debuff["Attribute"] == "Rooted" and debuff["Time"] == 3:
            # return True
            return False    # return false for now since we don't care about rooting as much
        # also don't care about armor debuffs for now
        else:
            return False








# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Fool1",
                 "ClassId": "Druid"},
                {"CharacterName": "Fool2",
                 "ClassId": "Archer"},
                {"CharacterName": "Fool3",
                 "ClassId": "Archer"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    chase_2latest = 0
    chase_latest = 0
    num_turns = 0

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

    # Determine when we should force a draw by running away
    runaway = False

    # if (numAlive(myteam) == 1) and (numAlive(myteam) < numAlive(enemyteam)):
    if (numAlive(myteam) == 1):
        # Get last character alive
        last_alive = None
        for character in myteam:
            if not character.is_dead():
                last_alive = character
                break

        if last_alive.attributes.get_attribute("Health") < 300:
            runaway = True
        else:
            runaway = False

    if runaway:
        # Get last character alive
        last_alive = None
        for character in myteam:
            if not character.is_dead():
                last_alive = character
                break

        moveto = away(last_alive.position, myteam, enemyteam)

        # print ("move from to:", last_alive.position, moveto)

        actions.append({
            "Action": "Move",
            "CharacterId": last_alive.id,
            "Location": moveto
        })

        return {
            'TeamName': teamName,
            'Actions': actions
        }


    # target priority list
    priority_list = ["Archer", "Druid", "Warrior"]

    # Choose a target
    target = None

    # First go off of priority list
    for p in priority_list:
        for character in enemyteam:
            if not character.is_dead():
                if character.classId == p:
                    target = character
                    break
        if target != None:
            break


    # Fallback onto choosing by least health
    if target == None:
        least_health = 2000
        for character in enemyteam:
            if not character.is_dead():
                if character.attributes.get_attribute("Health") < least_health:
                    least_health = character.attributes.get_attribute("Health")
                    target = character

    # If we found a target
    if target:
        for character in [c for c in myteam if (not c.is_dead())]:
            my_id = character.id


            # Runaway logic
            if character.attributes.get_attribute("Health") < 300 and (nearestCharInfo(character.position, enemyteam)["dist"] == 0):
                moveto = away(character.position, myteam, enemyteam)
                if not (moveto == character.position):
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "Location": moveto
                    })
                    continue

            # If I am in range, either move towards target
            if character.in_range_of(target, gameMap):
                # Am I already trying to cast something?
                cast = False
                if character.casting is None:

                    # make healing last priority ability if it exists (and rooting second last)
                    abils = list(character.abilities.items())
                    try:
                        idx = abils.index((13,0))
                        abils.pop(idx)
                        abils.append((13,0))
                    except ValueError: pass
                    try:
                        idx = abils.index((3,0))
                        abils.pop(idx)
                        abils.append((3,0))
                    except ValueError: pass

                    for abilityId, cooldown in abils:
                        ability = game_consts.abilitiesList[int(abilityId)]
                        targ_id = target.id if ability["StatChanges"][0]["Change"] < 0 else character.id

                        if abilityId == 0 and not hasNewDebuff(character): # burst
                            continue

                        if abilityId == 13: # rooting 
                            if abs(chase_latest-chase_2latest)==0 or num_turns<5:
                                continue
                            else: 
                                # # root lowest health character
                                healthstats = [
                                    (
                                        c.attributes.get_attribute("Health"), # net health
                                        c.attributes.get_attribute("MaxHealth") - c.attributes.get_attribute("Health"), # damage taken
                                        c.id # id
                                    )
                                for c in enemyteam if (not c.is_dead())]

                                healthstats = sorted(healthstats, key=lambda x: x[0]) # sorts list of tuples by first entry in each tuple

                                for (health, dmg, cid) in healthstats:
                                    if dmg > 200:
                                        targ_id = cid
                                        break

                        if abilityId == 12: # sprint
                            continue

                        if abilityId == 2: # armor debuff
                            continue

                        if abilityId == 3: # ranged heal
                            # heal lowest health player if needed
                            healthstats = [
                                (
                                    c.attributes.get_attribute("Armor"), # armor
                                    c.attributes.get_attribute("Health"), # net health
                                    c.attributes.get_attribute("MaxHealth") - c.attributes.get_attribute("Health"), # damage taken
                                    c.id # id
                                )
                            for c in myteam if (not c.is_dead() and c.id != my_id)]

                            healthstats = sorted(healthstats, key=lambda x: (x[0], x[1])) # sorts list of tuples by first entry in each tuple

                            for (armor, health, dmg, cid) in healthstats:
                                if dmg > 125:
                                    targ_id = cid
                                    break

                        if abilityId == 4: # ranged arm buff
                            # arm buff lowest health character
                            healthstats = [
                                (
                                    c.attributes.get_attribute("Health"), # net health
                                    c.attributes.get_attribute("MaxHealth") - c.attributes.get_attribute("Health"), # damage taken
                                    c.id # id
                                )
                            for c in myteam if (not c.is_dead() and c.id != my_id)]

                            healthstats = sorted(healthstats, key=lambda x: x[0]) # sorts list of tuples by first entry in each tuple

                            for (health, dmg, cid) in healthstats:
                                targ_id = cid
                                break



                        # Do I have an ability not on cooldown
                        if cooldown == 0:
                            # Get ability
                            actions.append({
                                "Action": "Cast",
                                "CharacterId": character.id,
                                # Am I buffing or debuffing? If buffing, target myself
                                "TargetId": targ_id,
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

                chase_2latest = chase_latest
                chase_latest = 0
            else:
                chase_2latest = chase_latest
                chase_latest = 1
                # pass # don't move
                # Not in range, move towards
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                })

    # print actions
    num_turns+=1

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
