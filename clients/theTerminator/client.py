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

# My one true love and god is HARAMBE </3
# --------------------------- SET THIS IS UP -------------------------
teamName = "theTerminator"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "A1",
                 "ClassId": "Assassin"},
                {"CharacterName": "A2",
                 "ClassId": "Assassin"},
                {"CharacterName": "A3",
                 "ClassId": "Assassin"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
# --------------------------- CHANGE THIS SECTION -------------------------
    baseDangerScores = {
        'Assassin': 8,
        'Archer': 7,
        'Enchanter': 6.5,
        'Druid': 6,
        'Sorcerer': 6,
        'Warrior': 4,
        'Wizard': 4,
        'Paladin': 3.5
    }
    silDanger = ['Paladin', 'Sorcerer', 'Druid']
    dangerScores = {}
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

    # Choose a target
    target = None#max(enemyteam, key=lambda x:0 if x.is_dead() else dangerScores[x.ClassId])
    for character in enemyteam:
        if not character.is_dead():
            dangerScores[character.id] = baseDangerScores[character.classId]
            if character.attributes.get_attribute("Stunned") or character.attributes.get_attribute("Rooted"):
                dangerScores[character.id]+=1
            if character.attributes.get_attribute("Health")<100:
                dangerScores[character.id]+=1
            #if character.classId in silDanger and character.attributes.get_attribute("Silenced"):
            #    dangerScores[character.classId]+=2
            for d in character.debuffs:
                if d["Attribute"]=="Armor" and d["Change"]<0:
                    dangerScores[character.id]+=1
                if d["Attribute"]=="Damage" and d["Change"]<0:
                    dangerScores[character.id]+=1


            if(target==None or dangerScores[character.id]>dangerScores[target.id]):
                target = character

            #break
    a = 0
    if target:
        print "TARGET: ", target.classId
    # If we found a target
    if target:
        for character in myteam:
            # If I am in range, either move towards target
            if character.in_range_of(target, gameMap) and not character.is_dead():
                        
                # Am I already trying to cast something?
                if character.casting is None:
                    if(character.classId == "Enchanter"):
                        print "ABILITIES: ", character.abilities
                        done = 0
                        fiteme = None

                        if not done and character.abilities[0] == 0:
                            ability = game_consts.abilitiesList[int(0)]
                            priorities = {
                                "Druid":1,
                            }
                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and e.attributes.get_attribute("Silenced")):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(5)
                                    })

                        if not done and character.abilities[5] == 0:
                            ability = game_consts.abilitiesList[int(5)]
                            priorities = {
                                "Enchanter": 1,
                                "Druid":2,
                                "Assassin":3,
                                "Paladin":4,
                                "Sorcerer":5,
                                "Wizard":6
                            }
                            for e in enemyteam:
                                cc = (e.attributes.get_attribute("Silenced")) #or e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted"))
                                if not e.is_dead() and character.in_ability_range_of(e, gameMap, 5) and (e.classId in priorities and not cc):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                        "AbilityId": int(5)
                                    })
                            #silence

                        if not done and character.abilities[6]==0:
                            ability = game_consts.abilitiesList[int(6)]
                            priorities = {
                                "Warrior":1,
                                "Assassin":2,
                                "Archer":3,
                                "Paladin":4
                            }
                            for e in enemyteam:
                                if not e.is_dead() and character.in_ability_range_of(e, gameMap, 6) and (e.classId in priorities):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                            if fiteme:
                                done+=1
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                        "AbilityId": int(6)
                                    })
                            #damage curse
                        if not done and character.abilities[0]==0:
                            ability = game_consts.abilitiesList[int(0)]
                            priorities = {
                                "Warrior":1,
                                "Assassin":2,
                                "Paladin":3
                            }
                            for e in myteam:
                                condition = e.attributes.get_attribute("Silenced") or e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted")
                                if not e.is_dead() and (e.classId in priorities and condition):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                            if fiteme:
                                done+=1
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(0)
                                    })
                            #BURST
                        if not done and character.abilities[7]==0:
                            ability = game_consts.abilitiesList[int(7)]
                            priorities = {
                                "Assassin":1,
                                "Druid":2,
                                "Enchanter":3
                            }
                            cc = (e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted"))
                            for e in myteam:
                                if not e.is_dead() and not cc and (e.classId in priorities):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                            if fiteme:
                                done+=1
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(7)
                                    })

                        if done==0  or fiteme==None:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                            #+armor/dmg Warrior->druid->self
                    
                    elif(character.classId == "Druid"):
                        done = 0
                        fiteme = None

                        if not done and character.abilities[3] == 0:
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Druid":1,
                                "Assassin":2,
                                "Enchanter":3
                            }
                            emergencies = {
                                "Druid":200,
                                "Enchanter":400,
                                "Assassin":100
                            }
                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and e.attributes.get_attribute("Health")<=(e.attributes.get_attribute("MaxHealth")-emergencies[e.classId])):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(3)
                                    })
                        if not done and character.abilities[13] == 0:
                            ability = game_consts.abilitiesList[int(13)]
                            priorities = {
                                "Assassin":1,
                                "Druid":2,
                                "Paladin":3,
                                "Archer":4
                            }
                            for e in enemyteam:
                                cc = e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted")
                                if not e.is_dead() and character.in_ability_range_of(e, gameMap, 13) and (e.classId in priorities and not cc):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                        "AbilityId": int(13)
                                    })
                        if not done and character.abilities[3] == 0:
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Druid":1,
                                "Enchanter":2,
                                "Assassin":3
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and e.attributes.get_attribute("health")!=e.attributes.get_attribute("MaxHealth")):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(3)
                                    })
                        if not done and character.abilities[4] == 0:
                            ability = game_consts.abilitiesList[int(4)]
                            priorities = {
                                "Druid":1,
                                "Enchanter":2,
                                "Assassin":3
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(4)
                                    })
                        if not done and character.abilities[0] == 0:
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Enchanter":1,
                                "Assassin":2
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and (e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted") or e.attributes.get_attribute("Silenced"))):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(0)
                                    })            
                        if done==0  or fiteme==None:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })
                    
                    elif(character.classId == "Paladin"):
                        done = 0
                        fiteme = None

                        if not done and character.abilities[3] == 0:
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Druid":1,
                                "Assassin":2,
                                "Paladin":3,
                                "Enchanter":4
                            }
                            emergencies = {
                                "Druid":200,
                                "Paladin":200,
                                "Enchanter":400,
                                "Assassin":100
                            }
                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and e.attributes.get_attribute("Health")<=(e.attributes.get_attribute("MaxHealth")-emergencies[e.classId])):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(3)
                                    })
                        if not done and character.abilities[14] == 0:
                            ability = game_consts.abilitiesList[int(14)]
                            priorities = {
                                "Assassin":1,
                                "Druid":2,
                                "Paladin":3,
                                "Archer":4
                            }
                            for e in enemyteam:
                                cc = e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted")
                                if not e.is_dead() and character.in_ability_range_of(e, gameMap, 14) and (e.classId in priorities and not cc):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
                                        "AbilityId": int(14)
                                    })
                        if not done and character.abilities[3] == 0: #HEAL
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Druid":1,
                                "Assassin":2,
                                "Paladin":3,
                                "Enchanter":4
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and e.attributes.get_attribute("health")!=e.attributes.get_attribute("MaxHealth")):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(3)
                                    })
                        
                        if not done and character.abilities[0] == 0:
                            ability = game_consts.abilitiesList[int(3)]
                            priorities = {
                                "Enchanter":1,
                                "Assassin":2
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and (e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted") or e.attributes.get_attribute("Silenced"))):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(0)
                                    })            
                        if done==0  or fiteme==None:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })

                    elif(character.classId == "Assassin"):
                        done = 0
                        fiteme = None
                        #for e in enemyteam:
                        #    if not e.is_dead() and e.classId == "Assassin":
                        #        if e.abilities[11]==0:
                        #            #ability = game_consts.abilitiesList[12]
                        #            print "RUNNING AWAY"
                        #            done+=1
                        #            actions.append({
                        #                "Action": "Move",
                        #                "CharacterId": character.id,
                        #                "Position": (character.position[0]-1,character.position[1])
                        #                })
                        #if character.attributes.get_attribute("health")<700:
                        #    print "DYING!"
                        #    done = 1
                        #    fiteme = character
                        #    actions.append({
                        #        "Action": "Move",
                        #        "CharacterId": character.id,
                        #        "Position": str((a, 0)),
                        #    })
                        #    a+=1

                        if not done and character.abilities[11] == 0:
                            ability = game_consts.abilitiesList[int(11)]
                            print "BACKSTABBED!!"
                            fiteme = target
                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(11)
                                    })

                        if not done and character.abilities[0] == 0:
                            ability = game_consts.abilitiesList[int(0)]
                            priorities = {
                                "Druid":1,
                            }

                            for e in myteam:
                                if not e.is_dead() and (e.classId in priorities and (e.attributes.get_attribute("Stunned") or e.attributes.get_attribute("Rooted") or e.attributes.get_attribute("Silenced"))):
                                    if not fiteme or priorities[e.classId]<priorities[fiteme.classId]:
                                        fiteme = e
                                        print "FOUND IT"
                                if e.classId not in priorities:
                                    print e.classId

                            if fiteme:
                                done+=1
                                #character.use_ability(5, fiteme, gameMap)
                                actions.append({
                                        "Action": "Cast",
                                        "CharacterId": character.id,
                                        # Am I buffing or debuffing? If buffing, target myself
                                        "TargetId": fiteme.id if ability["StatChanges"][0]["Change"] < 0 else fiteme.id,
                                        "AbilityId": int(11)
                                    })

                        if done==0  or fiteme==None:
                            actions.append({
                                "Action": "Attack",
                                "CharacterId": character.id,
                                "TargetId": target.id,
                            })

                    else:    
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
