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
teamName = "GreatStrategy"
# ---------------------------------------------------------------------

# Set initial connection data
def initialResponse():
# ------------------------- CHANGE THESE VALUES -----------------------
	return {'TeamName': teamName,
			'Characters': [
				{"CharacterName": "Legolas",
				 "ClassId": "Archer"},
				{"CharacterName": "Will Tell",
				 "ClassId": "Archer"},
				{"CharacterName": "Robin Hood",
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
	
	# Choose a target
	locs = [(0,0), (1,0), (2,0), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (3, 4), (2, 4), (1, 4), (0, 4), (0, 3), (0, 2), (0, 1)]
	target = None
	
	#armor_buff = {"Action": "Cast", "CharacterId": character.id, "AbilityId": 15}
	#print(game_consts.abilitiesList[15])
	
	
	unstun = dict()
	stun = dict()
	hp = [0, 0, 0, 0, 0, 0, 0, 0]
	ourcnt = 0
	theircnt = 0
	ass = 0
	arch = 0
	wars = 0
	for my in myteam:
		unstun[my] = 0
		if my.is_dead() == 0:
			ourcnt += 1
	for en in enemyteam:
		hp[en.id] = en.attributes.get_attribute("Health")
		stun[en] = 0
		if en.is_dead() == 0:
			theircnt += 1
			if en.classId == "Assassin":
				ass += 1
			if en.classId == "Archer":
				arch += 1
			if en.classId == "Warrior":
				wars += 1
	maxHP = myteam[0]
	"""if wars == theircnt and wars <= 2 and ourcnt >= 2:
		
		for my in myteam:
			if my.is_dead() == 0:
				maxHP = my
		for my in myteam:
			if my.is_dead() == 0:
				if my.attributes.get_attribute("Health") > maxHP.attributes.get_attribute("Health"):
					maxHP = my
		if maxHP.position != (2, 2):
			actions.append({"Action": "Move", "CharacterId": maxHP.id, "Location": (2, 2)})	
		else:
			for en in enemyteam:
				if en.is_dead() == 0:
					if(maxHP.in_range_of(en, gameMap)):
						actions.append({
									"Action": "Attack",
									"CharacterId": maxHP.id,
									"TargetId": en.id
								})
	"""							
			
	#print(hp)
	
	#print("actual hp", hp)
	
	for my in myteam:
		if my.is_dead():
			continue
		pos = my.position
		x1 = pos[0] + pos[1]
		x2 = 4 - pos[0] + 4 - pos[1]
		posOrig = (0,0)
		pos2 = (4, 0)
		y1 = 4 - pos[0] + pos[1]
		y2 = pos[0] + 4 - pos[1]
		if x1 < x2:
			posOrig = (4, 4)
		i0 = -1
		for i in range(len(locs)):
			if pos == locs[i]:
				i0 = i
		i0 += 1
		i0 %= len(locs)
		if i0 == -1:
			posOrig = (2, 4)
		else:
			posOrig = locs[i0]
			
		#if my.position != enemyteam[0].position and (enemyteam[0].position == (0,0) or enemyteam[0].position == (4, 4)):
		#	continue
		if my.casting:
			continue
		didAct = 0
		
		if my.abilities[0] == 0:
			for tm in myteam:
				if tm.is_dead():
					continue
				if tm.attributes.get_attribute("Stunned") == 1 and unstun[tm] == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": tm.id, "AbilityId": 0})
					didAct = 1
					unstun[tm] = 1
		if didAct:
			continue
		#print(my.abilities)
		#if my.classId == "Warrior" and my.abilities['15'] == 0 and my.attributes.get_attribute("Health") < gameConstants.classesJson[my.classId]['Health'] * 0.7:
		#	actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 15})
		#	didAct = 1
			
		
		
		if didAct:
			continue
			
		mostDanTarget = enemyteam[0]
		leastHP = enemyteam[0]
		mostHP = enemyteam[0]
		caster = myteam[0]
		
		besttm = myteam[0]
		tmhp = myteam[0]
		
		
		for m in myteam:
			if m.is_dead() == 0:
				besttm = m
				tmhp = m
		for m in myteam:
			if m.is_dead() == 0:
				if gameConstants.classesJson[m.classId]['Damage'] > gameConstants.classesJson[besttm.classId]['Damage']:
					besttm = m
				if gameConstants.classesJson[m.classId]['Health'] - m.attributes.get_attribute("Health") > gameConstants.classesJson[tmhp.classId]['Health'] - tmhp.attributes.get_attribute("Health"):
					tmhp = m
		for e in enemyteam:
			if hp[e.id] <= 0:
				continue
			leastHP = e
			mostHP = e
			mostDanTarget = e
			caster = e
		for en in enemyteam:
			if hp[en.id] <= 0:
				continue
			if gameConstants.classesJson[en.classId]['Damage'] > gameConstants.classesJson[mostDanTarget.classId]['Damage']:
				mostDanTarget = en
			if en.attributes.get_attribute("Health") < leastHP.attributes.get_attribute("Health") or (en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health") and en.attributes.get_attribute("Armor") < leastHP.attributes.get_attribute("Armor")):
				leastHP = en 
			if en.attributes.get_attribute("Health") > leastHP.attributes.get_attribute("Health"):
				mostHP = en 
			if en.classId == "Sorcerer":
				caster = en
			if en.classId == "Enchanter":
				caster = en
			if en.classId == "Druid":
				caster = en
				
		if didAct:
			continue
			
		
			
		if(my.classId == "Sorcerer" and my.attributes.get_attribute("Health") > 700):
			if(my.abilities[8] == 0):
				actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 8})
				continue
		if(my.in_range_of(caster, gameMap)):
			if my.classId == "Enchanter" and my.abilities[5] == 0:
				actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": caster.id, "AbilityId": 5})
				continue	
		if(my.in_range_of(tmhp, gameMap)):	
			if my.classId == "Enchanter" and my.abilities[7] == 0 and tmhp.attributes.get_attribute("Health") < gameConstants.classesJson[tmhp.classId]['Health'] - 20:
				actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": tmhp.id, "AbilityId": 7})
				continue
			
		
		#	print(my.abilities)
		if character.in_ability_range_of(tmhp, gameMap, 3):
			if (my.classId == "Druid" or my.classId == "Paladin") and my.abilities[3] == 0 and tmhp.attributes.get_attribute("Health") < gameConstants.classesJson[tmhp.classId]['Health'] - 10:
				actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": tmhp.id, "AbilityId": 3})
				continue
		if character.in_ability_range_of(tmhp, gameMap, 4):
			if my.classId == "Druid" and my.abilities[4] == 0 and tmhp.attributes.get_attribute("Health") < gameConstants.classesJson[tmhp.classId]['Health'] - 20:
				actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": tmhp.id, "AbilityId": 4})
				continue
				
		
		for en in enemyteam:
			if hp[en.id] <= 0:
				continue
			if didAct:
				continue
			target = en
			character = my
			
			"""if target.in_range_of(character, gameMap):
				if gameConstants.classesJson[en.classId]['AttackRange'] == gameConstants.classesJson[my.classId]['AttackRange']:
					if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health"):
						actions.append({
							"Action": "Attack",
							"CharacterId": character.id,
							"TargetId": target.id
						})
						hp[en.id] -= max(0, character.attributes.get_attribute("Damage") - en.attributes.get_attribute("Armor"))
						didAct = 1
						continue"""
					
			
			"""my.attributes.get_attribute("Health") < 500 and"""
			if((not theircnt == arch) and (not (theircnt < ourcnt and ass == theircnt))):
				if my.position != posOrig and gameConstants.classesJson[en.classId]['AttackRange'] <= gameConstants.classesJson[my.classId]['AttackRange']:
					if  abs(character.position[0] - target.position[0]) + abs(character.position[1] - target.position[1]) <= 1:
						if my.attributes.get_attribute("Health") < (650 + 301 * (int)(en.classId == "Warrior")):
							"""if(my.abilities[12] == 0 and en.classId == "Warrior"):
								actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 12})
								didAct = 1
								continue	"""
							actions.append({"Action": "Move", "CharacterId": my.id, "Location": posOrig})
							didAct = 1
							continue
			
			if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health") and character.in_range_of(target, gameMap) == 0:
				if my.attributes.get_attribute("Health") >= (650 + 301 * (int)(en.classId == "Warrior")) and (gameConstants.classesJson[en.classId]['AttackRange'] <= gameConstants.classesJson[my.classId]['AttackRange'] or (en.position == (0,0) or en.position == (4,4))):
					if((my.classId == "Assassin" or my.classId == "Archer") and my.attributes.get_attribute("MovementSpeed") == 1):
						if(my.abilities[12] == 0):
							actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 12})
							didAct = 1
							continue	
					
					actions.append({"Action": "Move", "CharacterId": my.id, "TargetId": target.id})
					didAct = 1
					continue
			"""if(my.classId == "Archer" and my.attributes.get_attribute("MovementSpeed") == 1) and  abs(character.position[0] - target.position[0]) + abs(character.position[1] - target.position[1]) <= 1:
					if(my.abilities[12] == 0):
						actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 12})
						didAct = 1
						continue	
			"""
				
			#if target.in_range_of(character, gameMap) == 0:
			if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health"):
				if my.classId == "Archer":
						if gameConstants.classesJson[target.classId]['Armor'] == 45:
							if character.in_ability_range_of(target, gameMap, 2):
								if my.abilities[2] == 0:
									actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 2})
									didAct = 1
									continue
			if my.classId == "Druid":
				if character.in_ability_range_of(target, gameMap, 13):
					if my.abilities[13] == 0:
						actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 13})
						didAct = 1
						continue
			if my.classId == "Sorcerer":
				if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health") and character.in_ability_range_of(target, gameMap, 16) == 0:
					actions.append({"Action": "Move", "CharacterId": my.id, "TargetId": target.id})
					didAct = 1
					continue
			
			if didAct == 0:
				if character.in_ability_range_of(target, gameMap, 1):
					if en == mostDanTarget:
						if stun[en] == 0:
							if my.classId == "Warrior" and my.abilities[1] == 0 and target.attributes.get_attribute("Stunned") == 0:
								actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 1})
								stun[en] = 1
								didAct = 1
					else:
						if stun[en] == 0:
							if my.classId == "Warrior" and my.abilities[1] == 0 and target.attributes.get_attribute("Stunned") == 0:
								actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 1})
								stun[en] = 1
								didAct = 1
					
			if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health") and didAct == 0:
				if my.classId == "Enchanter" and my.abilities[6] == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 6})
					didAct = 1
				if my.classId == "Sorcerer" and my.abilities[16] == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 16})
					didAct = 1
				if my.classId == "Assassin" and my.abilities[11] == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 11})
					didAct = 1
				if my.classId == "Wizard" and my.abilities[9] == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 9})
					didAct = 1
					continue
			if character.in_ability_range_of(target, gameMap, 10):
				if didAct == 0 and my.classId == "Wizard" and my.abilities[10] == 0 and stun[target] == 0 and target.attributes.get_attribute("Stunned") == 0:
					actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": target.id, "AbilityId": 10})
					didAct = 1
					stun[target] = 1
			
			
			if not didAct:
				if character.in_range_of(target, gameMap):
					if en.attributes.get_attribute("Health") == leastHP.attributes.get_attribute("Health"):
						actions.append({
							"Action": "Attack",
							"CharacterId": character.id,
							"TargetId": target.id
						})
						hp[en.id] -= max(0, character.attributes.get_attribute("Damage") - en.attributes.get_attribute("Armor"))
						#print target.attributes.get_attribute("Armor")
						#print(en.attributes.get_attribute("Health"), character.attributes.get_attribute("Damage") , en.attributes.get_attribute("Armor"), hp[en.id]) 
						
						didAct = 1
							
			if didAct:
				break
					
		
					
		if didAct:
			continue
		
		if my.classId == "Warrior" and my.abilities[15] == 0:
			actions.append({"Action": "Cast", "CharacterId": my.id, "TargetId": my.id, "AbilityId": 15})
			didAct = 1
			
		continue
		pos = my.position
		ps = 0
		for i in range(0, len(locs)):
			if locs[i] == pos:
				ps = i
				break
		npos = locs[(ps + 1) % len(locs)]
		#pos[0] += 1
		actions.append({
		"Action": "Move",
		"CharacterId": my.id,
		# Am I buffing or debuffing? If buffing, target myself
		#"TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
		#"AbilityId": int(abilityId)
		"Location": npos
		})

	"""for character in myteam:
		pos = character.position
		pos[0] += 1
		actions.append({
			"Action": "Move",
			"CharacterId": character.id,
			# Am I buffing or debuffing? If buffing, target myself
			#"TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
			#"AbilityId": int(abilityId)
			"Location":(3,3)
			})
	"""
	#print("changed hp", hp)		
	# If we found a target
	# if target:
		# for character in myteam:
			# # If I am in range, either move towards target
			# if character.in_range_of(target, gameMap):
				# # Am I already trying to cast something?
				# if character.casting is None:
					# cast = False
					# for abilityId, cooldown in character.abilities.items():
						# # Do I have an ability not on cooldown
						# if cooldown == 0:
							# # If I can, then cast it
							# ability = game_consts.abilitiesList[int(abilityId)]
							# # Get ability
							# actions.append({
								# "Action": "Cast",
								# "CharacterId": character.id,
								# # Am I buffing or debuffing? If buffing, target myself
								# "TargetId": target.id if ability["StatChanges"][0]["Change"] < 0 else character.id,
								# "AbilityId": int(abilityId)
							# })
							# cast = True
							# break
					# # Was I able to cast something? Either wise attack
					# if not cast:
						# actions.append({
							# "Action": "Attack",
							# "CharacterId": character.id,
							# "TargetId": target.id,
						# })
			# else: # Not in range, move towards
				# actions.append({
					# "Action": "Move",
					# "CharacterId": character.id,
					# "TargetId": target.id,
				# })

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
