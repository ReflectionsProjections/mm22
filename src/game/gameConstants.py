"""
Defines the classes
- Must contain in json
    Health - health of class
    Damage - damage dealt each tick
    AbilityDamage - damage added to each ability that does damage
    AtackRange - range of autoattack
    Armor - damage removed from each attack
    MovementSpeed - speed moved every tick
    Abilties - list of abilities
"""
classesJson = {
    "warrior" : {
            "Health"        : 500,
            "Damage"        : 50,
            "AbilityDamage" : 50,
            "AttackRange"   : 5,
            "Armor"         : 10,
            "MovementSpeed" : 5,
            "Abilities"     : [ 1 ]
    }
}

"""
Defines the abilities
- Must contain in json:
    List of stat changes
        Target - 0 for self, 1 for enemy target, 2 for ally target, 3 for anyone
        Attribute - Attribute of target to change
        Value - Value of attribute being changed
        Time - Total time this ability affects target
    Cooldown - number of ticks to refresh ability
    Range - range of ability
"""
# abilitiesList = [
        
#             "StatChanges": [
#                 "Target": 1,
#                 "Attribute": "MovementSpeed",
#                 "Change": -2,
#                 "Time": 5
#             ],
#             "Cooldown"  : 10,
#             "Range"     : 5,
#         ]

numPlayersPerRound = 2
numCharacterPerTeam = 3
