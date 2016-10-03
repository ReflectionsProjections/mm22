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
turn = 0

applied_actions = [] #action, character, enemy
# --------------------------- SET THIS IS UP -------------------------
teamName = "wwa_2"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Warrior1",
                 "ClassId": "Warrior"},
                {"CharacterName": "Warrior2",
                 "ClassId": "Warrior"},
                {"CharacterName": "Warrior3",
                 "ClassId": "Warrior"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    # Setup helper variables
    global turn
    global applied_actions
    turn+=1
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
    target = chooseTarget(enemyteam); 
    # Choose a target
    for character in myteam:
      action=None
      if character.name == "Warrior1":
        action = warriorMove(character, myteam, enemyteam, target)
      elif character.name == "Warrior2":
        action = warriorMove(character, myteam, enemyteam, target)
      elif character.name == "Warrior3":
        action = warriorMove(character,myteam, enemyteam, target)
      else:
        print "WE FUCKED UP->_>P>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

      if action:
	actions.append(action)

    #Clear actions from this round
    applied_actions[:] = []

    # If we found a target
    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
# ---------------------------------------------------------------------

def chooseTarget(enemyteam):
    target = enemyteam[0]
    for character in enemyteam:
        if not character.is_dead():
            target = character
    targetHealth = target.attributes.get_attribute("Health")
    for character in enemyteam:
	cHealth = character.attributes.get_attribute("Health")
        if not character.is_dead() and cHealth<targetHealth:
            target = character
	    targetHealth = cHealth
    return target


def warriorMove(char, myteam, enemyteam, target):
  action = { "Action": "Attack",
      "CharacterId": char.id,
      "TargetId": target.id
      }

  if char.casting is not None:
      return None

  #Find stun target, might be None
  stun_target = find_stun_target(char, enemyteam)
  buff_self = choose_to_buff(char, enemyteam)

  if buff_self and char.can_use_ability(15, ret=False):
      action["Action"] = "Cast"
      action["AbilityId"] = 15
      action["TargetId"] = char.id

  elif not char.in_range_of(target, gameMap):
    action["Action"]= "Move"
    action["Location"]= target.id
  elif stun_target:
    print "smite"''
    action["Action"]="Cast"
    action["AbilityId"]=1
    action["TargetId"]=stun_target.id
  if is_dodgeable_attack(char, enemyteam):
    action = get_dodge_action(char)
  #logic goes here
  return action

def choose_to_buff(char, enemies):
    for enemy in enemies:
        dist = abs((char.position[0] - enemy.position[0])) + abs((char.position[1] - enemy.position[1]))
        print dist
        if dist < 4 and dist != 0:
            return True
    return False

def get_dodge_action(char):
    selectPosition = list(char.position)
    posbelow = tuple([char.position[0], char.position[1] - 1])
    posabove = tuple([char.position[0], char.position[1] + 1])
    posleft = tuple([char.position[0] - 1, char.position[1]])
    posright = tuple([char.position[0] + 1, char.position[1]])
    if gameMap.is_inbounds(posbelow):
        selectPosition = posbelow
    elif gameMap.is_inbounds(posleft):
        selectPosition = posleft
    elif gameMap.is_inbounds(posright):
        selectPosition = posright
    elif gameMap.is_inbounds(posabove):
        selectPosition = posabove

    selectPosition = tuple(selectPosition)

    return {"Action": "Move",
              "CharacterId": char.id,
              "Location": selectPosition
              }


def find_stun_target(char, enemyteam):
    global applied_actions

    damage = 0
    target = None
    for enemy in enemyteam:
        if not enemy.is_dead() and not enemy.attributes.get_attribute("Stunned") \
                and char.in_ability_range_of(enemy, gameMap, 1) and char.can_use_ability(1) and not stunned_this_round(enemy):

            if enemy.can_use_ability(3):
                target = enemy
                break
            elif enemy.id == "Archer":
                target = enemy
                break
            else:
                t_damage = enemy.attributes.get_attribute("Damage")
                if t_damage > damage:
                    damage = t_damage
                    target = enemy

    if target is not None:
        applied_actions.append(target.id)

    return target

def stunned_this_round(target):
    global applied_actions

    for t in applied_actions:
        if t == target.id:
            return True

    return False

def is_dodgeable_attack(char, enemyteam):
    for enemy in enemyteam:
        cast = enemy.casting
        if cast is not None:
            target = cast["TargetId"]
            #print cast["AbilityId"]
            #print enemy.can_use_ability(cast["AbilityId"])
            #print char.id == target
            if enemy.can_use_ability(cast["AbilityId"]) and char.id == target:
                    if cast['CurrentCastTime'] == 0:
                        print "dodging"
                        return True
    return False


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
