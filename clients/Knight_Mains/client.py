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

turnCount = 0

# --------------------------- SET THIS IS UP -------------------------
teamName = "Knight Mains"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "TheTeamShe",
                 "ClassId": "Paladin"},
                {"CharacterName": "ToldYouNot",
                 "ClassId": "Assassin"},
                {"CharacterName": "ToWorryAbt",
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
    global turnCount
    turnCount = turnCount + 1
   
    
    def hitFirst(ClassId):
        return {
            'Druid': 1,
            'Paladin': 2,
            'Enchanter': 3,
            'Sorcerer': 4,
            'Wizard': 5,
            'Assassin': 6,
            'Warrior': 7,
            'Archer': 8,
        }[ClassId]

    def debuffFirst(ClassId) : # mesh with hitFirst
        return {
            'Paladin' : 1,
            'Druid' : 2,
            'Enchanter' : 3,
            'Sorcerer' : 4,
            'Assassin' : 5,
            'Archer' : 6,
            'Warrior' : 7,
            'Wizard' : 8
        }
    
    def stunFirst(ClassId):
        return {
            'Assassin': 1,
            'Archer': 2,
            'Warrior': 3,
            'Sorcerer': 4,
            'Wizard': 5,
            'Paladin': 6,
            'Druid': 7,
            'Enchanter': 8,
        }[ClassId]
    
    def applyArmorFirst(ClassId):
        return {
            'Assassin': 1,
            'Warrior': 2,
            'Archer': 3,
            'Sorcerer': 4,
            'Wizard': 5,
            'Paladin': 6,
            'Druid': 7,
            'Enchanter': 8,
        }[ClassId]

    def stunSelect(character, team):
        #print 'getting stunman'
        minPriority = 10
        target = None
        for member in team:
            priority = stunFirst(member.classId)
            if not member.is_dead() and priority < minPriority and not member.attributes.get_attribute('Stunned'):
                if character.classId =='Warrior' and character.in_ability_range_of(member, gameMap, 1):
                    #print 'Im a warrior'
                    target = member
                    minPriority = priority
                if character.classId == "Paladin" and character.in_ability_range_of(member, gameMap, 14):
                    #print 'Im a paladin'
                    target = member
                    minPriority = priority
        return target
    
    def targetSelectFrom(team, priorityList):
        #'''
        minPriority = 10
        target = None
        
        for member in team:
            priority = priorityList(member.classId)
            if not member.is_dead() and priority < minPriority:
                target = member
                minPriority = priority
        
        
        '''
        priority0 = priorityList(enemyteam[0].classId)
        priority1 = priorityList(enemyteam[1].classId)
        priority2 = priorityList(enemyteam[2].classId)
        
        if enemyteam[0].is_dead():
           if priority1 < priority2 and not enemyteam[1].is_dead() or enemyteam[2].is_dead():
               target = enemyteam[1]
           else:
               target = enemyteam[2]
        elif enemyteam[1].is_dead():
           if priority0 < priority2 and not enemyteam[0].is_dead() or enemyteam[2].is_dead():
               target = enemyteam[0]
           else:
               target = enemyteam[2]
        elif enemyteam[2].is_dead():
            if priority0 < priority1 and not enemyteam[0].is_dead() or enemyteam[1].is_dead():
                target = enemyteam[0]
            else:
                target = enemyteam[1]
        else:
            if priority0 < priority1 and priority0 < priority2:
                target = enemyteam[0]
            elif priority1 < priority0 and priority1 < priority2:
                target = enemyteam[1]
            else:
                target = enemyteam[2]
        #''' 
        ##print target.id
        return target
        
    def greatestHealthDifferential(myteam):
        lowestDiff = 2
        ret = myteam[0]
        for teamMember in myteam:
            differential = 1.0 * teamMember.attributes.get_attribute('Health') / teamMember.attributes.get_attribute('MaxHealth')
            ##print differential
            if differential < lowestDiff and differential > 0:
                lowestDiff = differential
                ret = teamMember
                
        return ret
    
    def manhattanDistance(player1, player2):
        return abs(player1.position[0] - player2.position[0] + player1.position[1] - player2.position[1])
        
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

    for character in myteam:
        #print character.classId
        if not character.casting is None:
            #print 'casting...'
            #print character.casting
            null = 0
            # This will be handled by character updating; UPDATE YOUR CODE
            # Finish the fucking spell
        elif character.attributes.get_attribute('Stunned') and character.abilities[0] == 0:
            # Cast burst
            ##print 'bursting'
            actions.append({
                "Action": "Cast",
                "CharacterId": character.id,
                "TargetId": character.id,
                "AbilityId": 0
            })
      #  elif(character.ClassId == 'Druid'):
      #      null = 0
      #  elif(character.ClassId == 'Enchanter'):
      #      null = 0
      #  elif(character.ClassId == 'Sorcerer'):
      #      null = 0
      #  elif(character.ClassId == 'Wizard'):
      #      null = 0
        elif(character.classId == "Assassin"):
            if turnCount == 1: # Sprint the first turn
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": character.id,
                    "AbilityId": 12,
                })
            else:
                target = targetSelectFrom(enemyteam, hitFirst)
                
                #print character.abilities
                #print character.can_use_ability('11')
                #print '11' in character.abilities
                #inAbilityRange = gameMap.in_vision_of(character.position,
                 #               target.position,
                  #              gameConstants.abilitiesList[11]["Range"])
                
                if character.in_ability_range_of(target, gameMap, 11) and character.can_use_ability(11):
                #if inAbilityRange and character.can_use_ability(11):
                    
                    actions.append({ # Backstab if possible 
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                        "AbilityId": 11,
                    })
                elif character.in_range_of(target, gameMap):
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
                elif not character.attributes.get_attribute("Rooted") and not character.attributes.get_attribute("Stunned"):
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
                else:
                    actions.append({
                        "Action": "Cast",
                        "CharacterId": character.id,
                        "TargetId": character.id,
                        "AbilityId": 12,
                    })
        elif(character.classId == "Warrior"):
            #print 'I\'m a warrior'
            archOrAss = False
            allStunned = True
            target = stunSelect(character, enemyteam)
            if target:
                null = 0
                #print target.id
                #print character.in_ability_range_of(target, gameMap, 1)
            for enemy in enemyteam:
                archOrAss = archOrAss or enemy.classId == 'Archer' or enemy.classId == 'Assassin'
                allStunned = allStunned and enemy.attributes.get_attribute('Stunned')  == 0
            if character.attributes.get_attribute('Health') < character.attributes.get_attribute('MaxHealth') and not archOrAss and character.abilities[15] == 0:
                #print 'buffing armor'
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                    "AbilityId": 15,
                })
            elif target and character.in_ability_range_of(target, gameMap, 1) and character.abilities[1] == 0 and character.can_use_ability(1):
                #print 'stunning'
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": target.id,
                    "AbilityId": 1,
                })
                character.use_ability(1, target, gameMap)
            else:
                target = targetSelectFrom(enemyteam, hitFirst)
                #print 'targetting'
                if character.in_range_of(target, gameMap):
                    #print 'attacking'
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
                elif not character.attributes.get_attribute("Rooted") and not character.attributes.get_attribute("Stunned"):
                    #print 'moving'
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": target.id,
                    })
        elif character.classId == "Druid":
            teamNeedsHealing = False
            for teamMember in myteam:
                teamNeedsHealing = teamNeedsHealing or teamMember.attributes.get_attribute('Health') < teamMember.attributes.get_attribute('MaxHealth') 
            #if teamNeedsHealing:
                #print 'Need healing.'
            healTarget = greatestHealthDifferential(myteam)
            #print healTarget.id
            armorTarget = targetSelectFrom(myteam, applyArmorFirst)
            
            canHeal = character.in_ability_range_of(healTarget, gameMap, 3) and character.abilities[3] == 0
            #No healing past turn 120
            if teamNeedsHealing and turnCount < 118 and canHeal:
                #print 'Have a health'
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": healTarget.id,
                    "AbilityId": 3,
                })
                
            #Can't heal, apply armor
            elif character.in_ability_range_of(armorTarget, gameMap, 4) and character.abilities[4] == 0:
                #print 'Armor here!'
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": armorTarget.id,
                    "AbilityId": 4,
                })
                
            #Can't heal or apply armor, move one tile away from teammates
            elif manhattanDistance(character, armorTarget) > 1:
            
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": armorTarget.id,
                })
                
            elif manhattanDistance(character, enemyteam[0]) == 0 or manhattanDistance(character, enemyteam[1]) == 0 or manhattanDistance(character, enemyteam[2]) == 0: 
                 
                #While(True) to emulate do-while loop in Python
                #repick random coordinates until they are not columns or the tile you are in
                while(True):
                    randX = random.randrange(0, 5)
                    randY = random.randrange(0, 5)
                    positionValid = abs(character.position[0] - randX + character.position[1] - randY) >= 1
                    isNotColumn = not (randX == 1 and randY == 1) and not (randX == 1 and randY == 3) and not (randX == 3 and randY == 1) and not (randX == 3 and randY == 3)
                    if  positionValid and isNotColumn:
                        break;
                
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "Location": (randX, randY),
                })
            #If Druid ends up in a battle, should move out of it one tile away

            
        elif character.classId == "Paladin":
            '''
            shouldHeal = 0 # an integer value between 0 - 10 for how big of a deal healing is
            shouldStun = 0 # an integer value between 0 - 9 for how valuable stunning could be
            shouldRun = 0 # an integer value between 0 - 8 for deciding if self should move
            shouldAttack = 0 # an integer value between 0 - 7 for how good it would be to attack
         
            # Choose a teammate to heal & put a value on it
         
            if turnCount < 118 and character.abilities[3] == 0 :
                friendlyTarget = greatestHealthDifferential(myteam)
                
                #self # initialize to self in case of a tie
                targetHealth = friendlyTarget.attributes.get_attribute('Health')
                targetMaxHealth = friendlyTarget.attributes.get_attribute('MaxHealth')
                                                 
                shouldHeal = 10 - 10 * targetHealth / targetMaxHealth #lower health -> higher value : [0,10]
            else :
                shouldHeal = 0
            print shouldHeal
           
            # Choose an enemy stun target & put a value on it
            stunTarget = stunSelect(character, enemyteam) # initialize to first enemy in list (shouldn't matter)
            print stunTarget
            if stunTarget:
                if not character.in_ability_range_of(stunTarget, gameMap, 14) :
                    shouldStun = 0
                else:
                    shouldStun = 10 # - stunFirst(stunTarget.classId)
         
         
         
            # should only run if there's nobody in proximity to help or fight
            # will work way toward target (a teammate who needs to be healed)
            # implements very similar to heal section, but doesn't check for proximity
            # Choose a teammate to run to (to heal) & put a value on it
            if turnCount < 117 :
                healTarget = greatestHealthDifferential(myteam) # initialize to self knowing that it will change
                healTargetHealth = healTarget.attributes.get_attribute('Health')
                healTargetMaxHealth = healTarget.attributes.get_attribute('MaxHealth')
         
                if healTarget == character :
                    shouldRun = 0
                elif character.attributes.get_attribute("Rooted") or character.attributes.get_attribute("Stunned"):
                    shouldRun = 0
                else : # see next line to correct implementation
                    shouldRun = 8 - manhattanDistance(character, healTarget)
            else :
                shouldRun = 0  
            '''
         
         
         
        ########### general AI Fight implementation goes here ########
         
         
        ## Kyle's weighted value code (relies upon above) goes here ##
            attackTarget = targetSelectFrom(enemyteam, hitFirst)      

            teamNeedsHealing = False
            for teamMember in myteam:
                teamNeedsHealing = teamNeedsHealing or teamMember.attributes.get_attribute('Health') < teamMember.attributes.get_attribute('MaxHealth') 
            #if teamNeedsHealing:
                #print 'Need healing.'
            healTarget = greatestHealthDifferential(myteam)
            
            canHeal = character.in_ability_range_of(healTarget, gameMap, 3) and character.abilities[3] == 0
            #No healing past turn 120
            
            stunTarget = stunSelect(character, enemyteam)
            if teamNeedsHealing and turnCount < 118 and canHeal:
                #print 'Have a health'
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": healTarget.id,
                    "AbilityId": 3,
                })
                
            elif stunTarget and character.can_use_ability(14):
                actions.append({
                    "Action": "Cast",
                    "CharacterId": character.id,
                    "TargetId": stunTarget.id,
                    "AbilityId": 14,
                })
            else:
                if character.in_range_of(attackTarget, gameMap):
                    actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": attackTarget.id,
                    })
                else:
                    actions.append({
                        "Action": "Move",
                        "CharacterId": character.id,
                        "TargetId": attackTarget.id,
                    })
                
            '''
            if max(shouldHeal, shouldStun, shouldRun, shouldAttack) == 0 :
                null = 0 # there is no move that has value, don't move
                actions.append({
                    "Action": "Move",
                    "CharacterId": character.id,
                    "TargetId": attackTarget.id,
                })
            elif max(shouldHeal, shouldStun, shouldRun, shouldAttack) == shouldHeal :
                actions.append({    "Action" : "Cast",
                                    "CharacterId" : character.id,
                                    "TargetId" : friendlyTarget.id,
                                    "AbilityId" : 3   })
            elif max(shouldStun, shouldRun, shouldAttack) == shouldStun and character.can_use_ability(14):
                actions.append({    "Action" : "Cast",
                                    "CharacterId" : character.id,
                                    "TargetID" : stunTarget.id,
                                    "AbilityId" : 14   })
                characterAlreadyStunned = stunTarget
            elif max(shouldRun, shouldAttack) == shouldRun :
                actions.append({    "Action": "Move",
                                    "CharacterId": character.id,
                                    "TargetId": healTarget.id,   })
            else :
                actions.append({    "Action": "Attack",
                                    "CharacterId": character.id,
                               "TargetId": attackTarget.id,   })
            '''
        elif character.classId == "Archer":
            feelThreatened = False # assume not threatened unless nearby enemy is found
            feelSupported = False # assume not supported unless nearby fighter teammate is found
            debuffTarget = enemyteam[0] # the enemy that the archer will attempt to cast debuff on
            rangedTarget = enemyteam[0] # the enemy that the archer will standard attack
            #runTarget # where the archer will head if running away from an enemy
        #code to determine feelThreatened
            for enemy in enemyteam :
                if not enemy.is_dead() :
                    if enemy.classId == 'Assassin' or enemy.classId == 'Warrior' :
                        feelThreatened = feelThreatened or manhattanDistance(character, enemy) <= 1
                    #elif enemy.classId == 'Archer': # update as we decide how to handle archer mirrors
                        #feelThreatened = feelThreatened or manhattanDistance(character, enemy) <= 2
        #code to determine feelSupported
            for teammate in myteam :
                if not teammate.is_dead() :
                    if teammate.classId == 'Warrior' or teammate.classId == 'Assassin' or teammate.classId == 'Archer':
                        feelSupported = feelSupported or manhattanDistance(character, teammate) <= 2
        #code to find debuffTarget
            debuffTarget = targetSelectFrom(enemyteam, debuffFirst)
            
            '''
            for enemy in enemyteam :
                if not enemy.isDead() :
                    debuffValue = debuffRank(enemy.attributes.get_atrribute('ClassId'))
                    if debuffValue <= debuffRank(debuffTarget.attributes.get_atrribute('ClassId')) :
                        if character.in_ability_range_of(enemy, map, 2) :
                            debuffTarget = enemy
                            '''
                            
            #code to find rangedTarget
            rangedTarget = targetSelectFrom(enemyteam, hitFirst)
            #Retrieve closest enemy
            potentialEnemies = []
            distance = 0
            while(len(potentialEnemies) == 0 and (not enemyteam[0].is_dead() or not enemyteam[1].is_dead() or not enemyteam[2].is_dead())) :
                for enemy in enemyteam :
                    if manhattanDistance(character, enemy) == distance and not enemy.is_dead():
                        potentialEnemies.append(enemy)
                        
                distance += 1        
            
            closestEnemy = targetSelectFrom(potentialEnemies, hitFirst)
                
            canSprint = character.abilities[12] == 0 and character.can_use_ability(12)
         
            if feelThreatened :
                #print 'feeling threatened'
                if canSprint :
                    #print 'casting sprint'
                    actions.append({    "Action" : "Cast",
                                   "CharacterId" : character.id,
                                   "TargetID" : character.id,
                                   "AbilityId" : 12,   })
                else :
                    #print 'moving toward target'
                    actions.append({    "Action": "Move",
                                   "CharacterId": character.id,
                                   "TargetId": closestTarget.id,   })
            elif feelSupported :#and #can use armor debuff# :
                if debuffTarget and character.in_ability_range_of(debuffTarget, gameMap, 2) and character.abilities[2] == 0:
                    actions.append({    "Action" : "Cast",
                                    "CharacterId" : character.id,
                                    "TargetID" : debuffTarget.id,
                                    "AbilityId" : 2,   })
                elif rangedTarget:
                    if character.in_range_of(rangedTarget, gameMap):
                        actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": rangedTarget.id,
                        })
                    else:
                        #print 'supported, moving in range'
                        actions.append({    "Action": "Move",
                                   "CharacterId": character.id,
                                   "TargetId": rangedTarget.id,   })
            else :
                if character.in_range_of(rangedTarget, gameMap):
                        actions.append({
                        "Action": "Attack",
                        "CharacterId": character.id,
                        "TargetId": rangedTarget.id,
                        })
                else:
                    #print 'moving to target'
                    actions.append({    "Action": "Move",
                               "CharacterId": character.id,
                               "TargetId": rangedTarget.id,   })

    # Send actions to the server
    return {
        'TeamName': teamName,
        'Actions': actions
    }
    

def attack(char, enemyteam):
    target = enemyteam[0]
    # For each enemy
    for enemy in enemyteam:
        # If enemy more important than target
        if hitFirst(enemy.ClassId) < hitFirst(target.ClassId):
            target = enemy
    if character.casting is None:
        # If in range
        if char.in_range_of(target, gameMap):
            # Attack target
            actions.append({
                "Action": "Attack",
                "CharacterId": character.id,
                "TargetId": target.id,
            })
        else: # Not in range, move to target
            actions.append({
                "Action": "Move",
                "CharacterId": character.id,
                "TargetId": target.id,
            })
    
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
