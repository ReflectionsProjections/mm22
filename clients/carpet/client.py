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
#MY IMPORTS

# Game map that you can use to query 
gameMap = GameMap()

def log(s):
    print(s)

# --------------------------- SET THIS IS UP -------------------------
teamName = "carpet"
# ---------------------------------------------------------------------
turn = 0
# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
    return {'TeamName': teamName,
            'Characters': [
                {"CharacterName": "Assassin",
                 "ClassId": "Assassin"},
                {"CharacterName": "Assassin",
                 "ClassId": "Assassin"},
                {"CharacterName": "Druid", #formerly wizerd
                 "ClassId": "Druid"},
            ]}
# ---------------------------------------------------------------------

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    global turn
    turn += 1
    log("########################################")
    log("Turn = ")
    log(turn)
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



    def teamParity(guy, other_guy):
        a = (guy.id*2 - 7)*(other_guy.id*2 - 7)
        return a/abs(a)

    def getTeam(guy):
        if teamParity(myteam[0],guy) == 1:
            return myteam
        else:
            return enemyteam

    def getEnemyTeam(guy):
        if teamParity(myteam[0],guy) == 1:
            return enemyteam
        else:
            return myteam

    def damageValue(actor,target,amount):
        weakest_target = 99999999.9
        for targets_target in getEnemyTeam(target):
            if target.in_range_of(targets_target,gameMap):
                score = min(weakest_target,targets_target.attributes.health)
        if actor.id == target.id:
            amount += 1
        return teamParity(actor,target)*float(amount)/float(weakest_target)

    # def damageValue(actor,amount,foe):
    #     if foe:
    #         return -999
    #     else:
    #         lowestHealth = 999999
    #         for targ in enemyteam:
    #             if actor.in_range_of(targ):
    #                 lowestHealth = min(lowestHealth,targ.attributes.health)
    #         return float(amount)/float(lowestHealth)

    def healthChangeValue(actor,target,amount):
        if teamParity(actor,target) == -1:
            amount_ = amount + target.attributes.armor #TODO: slight bug here
        else:
            amount_ = min(amount, target.attributes.maxHealth - target.attributes.health) -10
        return float(amount_)/float(target.attributes.health)*teamParity(actor,target)

    # def healthValue(targ,amount,foe):
    #     amount = abs(amount)
    #     if foe:
    #         return float(max(0,amount - targ.attributes.armor))/float(targ.attributes.health) #we want damage on foe, - - 200 = +200
    #     else:
    #         return -float(max(0,amount - targ.attributes.armor))/float(targ.attributes.health)

    def attackValue(actor,target):
        if target.attributes.health == 0:
            return 0
        return float(actor.attributes.damage - target.attributes.armor)/float(target.attributes.health)

    def armorValue(actor,target,amount):
        #guess whether target is gonna be subject to heavy fire
        # for team_mate in getTeam(target):
        #     if not team_mate.is_dead() and team_mate.attributes.health*(30+team_mate.attributes.armor) < 1 + target.attributes.health*(30+target.attributes.armor):
        #         return 0
        num_near_target = 0
        for enemy in getEnemyTeam(target):
            if target.in_range_of(enemy,gameMap):
                num_near_target += 1
        if target.id == actor.id:
            amount += 1
        return teamParity(actor,target)*float(amount)*float(num_near_target)/float(target.attributes.health)

    # def armorValue(targ,amount,foe):
    #     if foe:
    #         return -9999
    #     else:
    #         greatestDamage = 0
    #         for actor in enemyteam:
    #             if actor.in_range_of(targ):
    #                 greatestDamage = max(greatestDamage,actor.attributes.damage)
    #     return min(amount,greatestDamage - targ.attributes.armor)

    def rootedValue(actor,target):
        val = 0
        if target.classId == "Warrior":
            near = False
            for enemy_of_warrior in getEnemyTeam(target):
                if target.in_range_of(enemy_of_warrior,gameMap):
                    near = True
            if (not near):
                val = 0.05
        if target.classId == "Archer" or target.classId == "Assassin":
            if target.attributes.movementSpeed > 1:
                val = 0.1
        return -teamParity(actor,target)*val

    # def rootedValue(targ,foe):
    #     if not foe:
    #         return -0.001
    #     else:
    #         return 0.001

    def silencedValue(actor,target):
        val = 0
        if target.casting is not None:
            val = 0.3
        return -val*0.9*teamParity(actor,target)

    # def silencedValue(actor,foe):
    #     if not foe:
    #         return -0.2
    #     else:
    #         return 0.2

    def notAtkValue(actor,target):
        val = 0
        for enemy_of_target in getEnemyTeam(target):
            if target.in_range_of(enemy_of_target,gameMap):
                val = max(val,attackValue(target,enemy_of_target))
        log("blocked attack val: %f" %val)
        return -val*0.9*teamParity(actor,target)

    # def noAtkValue(actor,foe):
    #     if not foe:
    #         return -0.19
    #     else:
    #         return 0.19

    def calc_ab_ev(actor,target,abilityNum):
        if (turn > 120 and abilityNum == 3):
            return 0
        if (abilityNum == 2):
            return 0
        if (abilityNum == 0 and actor.id == target.id):
            if actor.attributes.stunned or actor.attributes.silenced:
                return 999
            else:
                return 0
        if (abilityNum == 7 and actor.id is not target.id):
            return (500/float(target.attributes.health))*teamParity(actor,target)
        score = 0.0
        ability_info = game_consts.abilitiesList[abilityNum]
        for stat_change in ability_info["StatChanges"]:
            if stat_change["Target"] == 0 and actor.id != target.id:
                return -1
            duration = stat_change["Time"]
            if stat_change["Target"] == 0 and actor.id != target.id:
                continue
            if stat_change["Attribute"] == "Stunned":
                score += max(silencedValue(actor,target),rootedValue(actor,target),notAtkValue(actor,target))*duration*stat_change["Change"]*-1
            elif stat_change["Attribute"] == "Silenced":
                score += silencedValue(actor,target)*duration*stat_change["Change"]*-1
            elif stat_change["Attribute"] == "Rooted":
                score += rootedValue(actor,target)*duration*stat_change["Change"]*-1
            elif stat_change["Attribute"] == "Armor":
                score += armorValue(actor,target,stat_change["Change"])*duration
            elif stat_change["Attribute"] == "Health":
                score += healthChangeValue(actor,target,stat_change["Change"])
            elif stat_change["Attribute"] == "Damage":
                score += damageValue(actor,target,stat_change["Change"])*duration
            elif stat_change["Attribute"] == "MovementSpeed":
                if me.classId == "Assassin":
                    score += 0.3
                    for enemy in getEnemyTeam(me):
                        if me.in_range_of(enemy,gameMap):
                            score *= 0
            else:
                log("WTFFFFFFFFF")
        score /= float(max(ability_info["CastTime"],1))
        log("ABILITY: %d ==[%d]==> %d, scored %f" %(actor.id,abilityNum,target.id,score))
        if (ability_info["StatChanges"][0]["Attribute"] is not "Health"):
            score -= 0.00001*abs(abs(7-2*target.id)-abs(7-2*me.id))
        return score

    for me in myteam:
        if me.is_dead():
            continue
        log(me.casting)
        log(me.target)
        if me.casting is not None:
            continue
            # if me.target != None:
            #     if me.in_ability_range_of(me.target,gameMap,me.casting["AbilityId"]):
            #         continue
            #     else:
            #         continue
        log("CONSIDERING:")
        log(me.id)
        ab_ev = []
        mov_ev = []
        atk_ev = []
        for enemy in enemyteam:
            if enemy.is_dead():
                continue
            #tryCast
            for ability, cooldown in me.abilities.iteritems():
                if me.in_ability_range_of(enemy,gameMap,int(ability)) and me.can_use_ability(ability):
                    ab_ev.append((enemy.id,calc_ab_ev(me,enemy,int(ability)),int(ability)))
            #tryAttack
            if me.in_range_of(enemy, gameMap):
                log("ATTACK: %d ==[%d]==> %d, scored %f" % (me.id,me.attributes.damage,enemy.id,attackValue(me,enemy)))
                atk_ev.append((enemy.id,attackValue(me,enemy)))
        for friend in myteam:
            if friend.is_dead():
                continue  
            for ability, cooldown in me.abilities.iteritems():
                if me.in_ability_range_of(friend,gameMap,int(ability)) and me.can_use_ability(ability):
                    ab_ev.append((friend.id,calc_ab_ev(me,friend,int(ability)),int(ability)))
        #tryMove
        for enemy in enemyteam:
            if enemy.is_dead():
                continue
            mov_ev.append((enemy.id,0.001))
        best = -99
        best_id = 0
        best_option = ""
        best_ability = 0
        for tid, ev, ability in ab_ev:
            if ev > best:
                best_id = tid
                best = ev
                best_option = "ability"
                best_ability = ability
        for tid, ev in atk_ev:
            if ev > best:
                best_id = tid
                best = ev
                best_option = "attack"
        for tid, ev in mov_ev:
            if ev > best:
                best_id = tid
                best = ev
                best_option = "move"
        log("DECISION:")
        log(best_option)
        log(best_ability)
        log(best_id)
        log(best)
        if best_option == "attack":
            actions.append({
                "Action":"Attack", 
                "CharacterId": me.id, 
                "TargetId": best_id})
        elif best_option == "ability":
            actions.append({
                "Action":"Cast", 
                "CharacterId": me.id, 
                "TargetId": best_id, 
                "AbilityId": best_ability})
        elif best_option == "move":
            actions.append({
                "Action":"Move",
                "CharacterId": me.id,
                "TargetId": best_id,
                })

    log(actions)
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
