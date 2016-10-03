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
teamName = "MinionsOfLong"
# ---------------------------------------------------------------------

def pick1stchar():
    # pick the first character in the team, randomly
    candChar = [char for char in game_consts.classesJson]
    #return i2char[random.randrange(len(i2char))]
    return random.choice(candChar)

def findBestComps(char):
    # Find the best companions for a given char

    #i2char = dict((k,v) for (k,v) in enumerate(game_consts.classesJson))
    comps0 = {
            'Archer':['Druid','Enchanter','Sorcerer','Wizard'],
            'Assassin':['Druid','Enchanter','Sorcerer','Wizard'],
            'Druid':['Paladin','Warrior'],
            'Enchanter':['Paladin','Warrior'],
            'Paladin':['Archer','Assassin'],
            'Sorcerer':['Paladin','Warrior'],
            'Warrior':['Archer','Assassin'],
            'Wizard':['Paladin','Warrior']
            }
    comps1 = {
            'Archer':['Paladin','Warrior'],
            'Assassin':['Paladin','Warrior'],
            'Druid':['Archer','Assassin'],
            'Enchanter':['Archer','Assassin'],
            'Paladin':['Druid','Enchanter','Sorcerer','Wizard'],
            'Sorcerer':['Archer','Assassin'],
            'Warrior':['Druid','Enchanter','Sorcerer','Wizard'],
            'Wizard':['Archer','Assassin']
            }

    # list of candidates
    comp0 = random.choice(comps0[char])
    comp1 = random.choice(comps1[char])

    return comp0,comp1

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    char0 = pick1stchar()
    char1,char2 = findBestComps(char0)
    '''
    print('I called this')
    print('char0 = '+char0)
    print('char1 = '+char1)
    print('char2 = '+char2)
    '''
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": char0+"0",
                 "ClassId": char0},
                {"CharacterName": char1+"1",
                 "ClassId": char1},
                {"CharacterName": char2+"2",
                 "ClassId": char2},
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

    '''
    # Choose a target
    target = findMinHealth(enemyteam)

    # If we found a target
    if target:
        for character in myteam:
            # If I am in range, either move towards target
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
    '''
    for character in myteam:
        if character.classId in ['Archer','Assassin']:
            actions.append(attackerPolicy(character,myteam,enemyteam))
        elif character.classId in ['Druid','Enchanter']: 
            actions.append(supportCasterPolicy(character,myteam,enemyteam))
        elif character.classId in ['Sorcerer','Wizard']: 
            actions.append(attackCasterPolicy(character,myteam,enemyteam))
        elif character.classId in ['Paladin','Warrior']: 
            actions.append(tankerPolicy(character,myteam,enemyteam))

    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }

def findMinHealth(team):
    chosen = random.choice(team)

    minHealth = sys.maxint
    for character in team:
        charHealth = character.attributes.health
        if not character.is_dead() and charHealth < minHealth:
            chosen = character
    return chosen

def findVulnerable(team):
    chosen = random.choice(team)

    minArmor = sys.maxint
    for character in team:
        charArmor = character.attributes.armor
        if not character.is_dead() and charArmor < minArmor:
            chosen = character
    return chosen

def findToughest(team):
    chosen = random.choice(team)

    maxToughness = -sys.maxint-1
    for character in team:
        # max damage is 200
        charTough = character.attributes.health/max(1,200-character.attributes.armor)
        if not character.is_dead() and charTough > maxToughness:
            chosen = character
    return chosen

def findMainCaster(team):
    chosen = random.choice(team)

    maxSP = -sys.maxint-1
    for character in team:
        charSP = character.attributes.spellPower
        if not character.is_dead() and charSP > maxSP:
            chosen = character
    return chosen

def findMainDamage(team):
    chosen = random.choice(team)

    maxDam = -sys.maxint-1
    for character in team:
        charDam = character.attributes.damage
        if not character.is_dead() and charDam > maxDam:
            chosen = character
    return chosen

def findStunned(team):
    chosen = None

    for character in team:
        if not character.is_dead() and character.attributes.stunned:
            chosen = character
    return chosen

def findSilenced(team):
    chosen = None

    for character in team:
        if not character.is_dead() and character.attributes.silenced:
            chosen = character
    return chosen

def findRooted(team):
    chosen = None

    for character in team:
        if not character.is_dead() and character.attributes.rooted:
            chosen = character
    return chosen

def evasiveAction(chosen,enemyteam,gameMap):
    dx5 = 0
    dy5 = 0
    for char in enemyteam:
        dx5 += (char.position[0]-5)**2
        dy5 += (char.position[1]-5)**2
    d5 = dx5 + dy5

    dx0 = 0
    dy0 = 0
    for char in enemyteam:
        dx0 += (char.position[0]-0)**2
        dy0 += (char.position[1]-0)**2
    d0 = dx0 + dy0

    if d0 < d5: 
        return {
            "Action": "Move",
            "CharacterId": chosen.id,
            "Location": (0,0),
        }
    else:
        return {
            "Action": "Move",
            "CharacterId": chosen.id,
            "Location": (4,4),
        }

def attackerPolicy(chosen,myteam,enemyteam):
    # must break free first
    if chosen.attributes.stunned or chosen.attributes.silenced or chosen.attributes.rooted:
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(0):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": chosen.id,
                    "AbilityId": 0
                }
    # attacker cast
    if chosen.classId == 'Archer':
        # sprint
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(12):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 12
            }

        toughTarget = findToughest(enemyteam)
        if chosen.casting is None:
            if chosen.abilities[2] == 0:
                if chosen.in_ability_range_of(toughTarget,gameMap,2):
                    return {
                        "Action": "Cast",
                        "CharacterId": chosen.id,
                        "TargetId": toughTarget.id,
                        "AbilityId": 2
                    }

    # backstab the weakest if possible
    minHealthTarget = findMinHealth(enemyteam)
    if chosen.classId == 'Assassin':
        # sprint
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(12):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 12
            }

        #if chosen.casting is None and chosen.abilities[11] == 0:
        if chosen.casting is None and chosen.can_use_ability(11):
            if chosen.in_ability_range_of(minHealthTarget,gameMap,11):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": minHealthTarget.id,
                    "AbilityId": 11
                }
    # attack the weakest
    if chosen.in_range_of(minHealthTarget, gameMap):
        return {
            "Action": "Attack",
            "CharacterId": chosen.id,
            "TargetId": minHealthTarget.id,
        }
    else:
        # or the most vulnerable
        vulnerableTarget = findVulnerable(enemyteam)
        if chosen.in_range_of(vulnerableTarget,gameMap):
            return {
                "Action": "Attack",
                "CharacterId": chosen.id,
                "TargetId": vulnerableTarget.id,
            }
        # move toward the weakest if still strong
        elif chosen.attributes.health > chosen.attributes.maxHealth/10:
            return {
                "Action": "Move",
                "CharacterId": chosen.id,
                "TargetId": minHealthTarget.id,
            }
        else:
            return evasiveAction(chosen,enemyteam,gameMap)

def supportCasterPolicy(chosen,myteam,enemyteam):
    # must break free first
    if chosen.attributes.stunned or chosen.attributes.silenced or chosen.attributes.rooted:
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(0):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 0
            }
                
    if chosen.classId == 'Druid':
        # heal allied
        minHealthTarget = findMinHealth(myteam)
        if minHealthTarget.attributes.health < minHealthTarget.attributes.maxHealth/2:
            if chosen.casting is None:
                if chosen.abilities[3] == 0:
                    if chosen.in_ability_range_of(minHealthTarget,gameMap,3):
                        return {
                            "Action": "Cast",
                            "CharacterId": chosen.id,
                            "TargetId": minHealthTarget.id,
                            "AbilityId": 3
                        }
        # armor buff allied
        vulnerableTarget = findVulnerable(myteam)
        if chosen.casting is None:
            if chosen.abilities[4] == 0:
                if chosen.in_ability_range_of(vulnerableTarget,gameMap,4):
                    return {
                        "Action": "Cast",
                        "CharacterId": chosen.id,
                        "TargetId": vulnerableTarget.id,
                        "AbilityId": 4
                    }
        # root enemy
        minHealthTarget = findMinHealth(enemyteam)
        if minHealthTarget.attributes.health < minHealthTarget.attributes.maxHealth/2:
            if chosen.casting is None:
                if chosen.abilities[13] == 0:
                    if chosen.in_ability_range_of(minHealthTarget,gameMap,13):
                        return {
                            "Action": "Cast",
                            "CharacterId": chosen.id,
                            "TargetId": minHealthTarget.id,
                            "AbilityId": 13
                        }

    if chosen.classId == 'Enchanter':
        # armor/dam buff allied
        dice = random.uniform(0,1)
        if dice >= 0.5:
            vulnerableTarget = findVulnerable(myteam)
            if chosen.casting is None and chosen.can_use_ability(7):
                if chosen.in_ability_range_of(vulnerableTarget,gameMap,7):
                    return {
                        "Action": "Cast",
                        "CharacterId": chosen.id,
                        "TargetId": vulnerableTarget.id,
                        "AbilityId": 7
                    }
        else:
            mainDamTarget = findMainDamage(myteam)
            if chosen.casting is None and chosen.can_use_ability(7):
                if chosen.in_ability_range_of(mainDamTarget,gameMap,7):
                    return {
                        "Action": "Cast",
                        "CharacterId": chosen.id,
                        "TargetId": mainDamTarget.id,
                        "AbilityId": 7
                    }

        # armor nerf enemy
        toughTarget = findToughest(enemyteam)
        #if chosen.casting is None and chosen.abilities[4] == 0:
        if chosen.casting is None and chosen.can_use_ability(6):
            if chosen.in_ability_range_of(toughTarget,gameMap,6):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": toughTarget.id,
                    "AbilityId": 6
                }
        # silence enemy
        mainCastTarget = findMainCaster(enemyteam)
        #if chosen.casting is None and chosen.abilities[13] == 0:
        if chosen.casting is None and chosen.can_use_ability(5):
            if chosen.in_ability_range_of(mainCastTarget,gameMap,5):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": mainCastTarget.id,
                    "AbilityId": 5
                }

    minHealthTarget = findMinHealth(enemyteam)
    if chosen.in_range_of(minHealthTarget,gameMap):
        return {
            "Action": "Attack",
            "CharacterId": chosen.id,
            "TargetId": minHealthTarget.id,
        }
    elif chosen.attributes.health > chosen.attributes.maxHealth/10:
        target = random.choice(myteam)
        return {
            "Action": "Move",
            "CharacterId": chosen.id,
            "TargetId": target.id,
        }
    else:
        return evasiveAction(chosen,enemyteam,gameMap)

def attackCasterPolicy(chosen,myteam,enemyteam):
    # must break free first
    if chosen.attributes.stunned or chosen.attributes.silenced or chosen.attributes.rooted:
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(0):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 0
            }

    if chosen.classId == 'Sorcerer':
        # sacrify health to improve dam
        if chosen.attributes.health > chosen.attributes.maxHealth/2 and chosen.casting is None and chosen.can_use_ability(8):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 8
            }
        # direct dam cast on enemy
        minHealthTarget = findMinHealth(enemyteam)
        if chosen.casting is None and chosen.can_use_ability(16):
            if chosen.in_ability_range_of(minHealthTarget,gameMap,16):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": minHealthTarget.id,
                    "AbilityId": 16
                }
            
    if chosen.classId == 'Wizard':
        # direct dam cast on enemy
        minHealthTarget = findMinHealth(enemyteam)
        if chosen.casting is None and chosen.can_use_ability(10):
            if chosen.in_ability_range_of(minHealthTarget,gameMap,10):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": minHealthTarget.id,
                    "AbilityId": 10
                }

        mainDamTarget = findMainDamage(enemyteam)
        if chosen.casting is None and chosen.can_use_ability(9):
            if chosen.in_ability_range_of(mainDamTarget,gameMap,9):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": mainDamTarget.id,
                    "AbilityId": 9
                }

    minHealthTarget = findMinHealth(enemyteam)
    if chosen.in_range_of(minHealthTarget,gameMap):
        return {
            "Action": "Attack",
            "CharacterId": chosen.id,
            "TargetId": minHealthTarget.id,
        }
    elif chosen.attributes.health > chosen.attributes.maxHealth/10:
        target = random.choice(enemyteam)
        return {
            "Action": "Move",
            "CharacterId": chosen.id,
            "TargetId": target.id,
        }
    else:
        return evasiveAction(chosen,enemyteam,gameMap)

def tankerPolicy(chosen,myteam,enemyteam):
    # must break free first
    if chosen.attributes.stunned or chosen.attributes.silenced or chosen.attributes.rooted:
        #if chosen.casting is None and chosen.abilities[0] == 0:
        if chosen.casting is None and chosen.can_use_ability(0):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 0
            }
    if chosen.classId == 'Paladin':
        # heal allied
        minHealthTarget = findMinHealth(myteam)
        if minHealthTarget.attributes.health < minHealthTarget.attributes.maxHealth/2:
            #if chosen.casting is None and chosen.abilities[3] == 0:
            if chosen.casting is None and chosen.can_use_ability(3):
                if chosen.in_ability_range_of(minHealthTarget,gameMap,3):
                    return {
                        "Action": "Cast",
                        "CharacterId": chosen.id,
                        "TargetId": minHealthTarget.id,
                        "AbilityId": 3
                    }
        # stun enemy
        mainDamTarget = findMainDamage(enemyteam)
        if chosen.casting is None and  chosen.can_use_ability(14):
            if chosen.in_ability_range_of(mainDamTarget,gameMap,14):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": mainDamTarget.id,
                    "AbilityId": 14
                }
    if chosen.classId == 'Warrior':
        # stun enemy
        mainDamTarget = findMainDamage(enemyteam)
        if chosen.casting is None and  chosen.can_use_ability(1):
            if chosen.in_ability_range_of(mainDamTarget,gameMap,1):
                return {
                    "Action": "Cast",
                    "CharacterId": chosen.id,
                    "TargetId": mainDamTarget.id,
                    "AbilityId": 1
                }
        # self armor buff
        if chosen.casting is None and chosen.can_use_ability(15):
            return {
                "Action": "Cast",
                "CharacterId": chosen.id,
                "TargetId": chosen.id,
                "AbilityId": 15
            }

    mainDamTarget = findMainDamage(enemyteam)
    if chosen.in_range_of(mainDamTarget,gameMap):
        return {
            "Action": "Attack",
            "CharacterId": chosen.id,
            "TargetId": mainDamTarget.id,
        }
    elif chosen.attributes.health > chosen.attributes.maxHealth/10:
        return {
            "Action": "Move",
            "CharacterId": chosen.id,
            "TargetId": mainDamTarget.id,
        }
    else:
        return evasiveAction(chosen,enemyteam,gameMap)

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
