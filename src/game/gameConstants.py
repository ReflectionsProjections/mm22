"""
Defines the classes
- Must contain in json
    Health - health of class
    Damage - damage dealt from autoattack
    AttackRange - range of attack in zones (range 0 = melee range)
    AttackSpeed - cooldown on attack in ticks
    Armor - damage removed from each attack
    MovementSpeed - cooldown (in ticks) on ability to move to adjacent zone
    Abilties - list of abilities
"""
classesJson = {
	"archer" : {
			"Health"        : 300,
            "Damage"        : 50,
            "AttackRange"   : 1,
            "AttackSpeed"   : 5,
            "Armor"         : 0,
            "MovementSpeed" : 5,
            "Abilities"     : [ 1 ]
	}
    "warrior" : {
            "Health"        : 500,
            "Damage"        : 50,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
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
        Time - Total time this ability affects target in ticks
    Cooldown - number of ticks to refresh ability
    Range - range of ability in zones
"""
abilitiesList = [
    {
            "StatChanges": [{
                "Target": 1,
                "Attribute": "MovementSpeed",
                "Change": -2,
                "Time": 5
            }],
            "Cooldown"  : 10,
            "Range"     : 5,
    },
        {
            "StatChanges": [{
                "Target": 1,
                "Attribute": "Health",
                "Change": -50,
                "Time": 0
            }],
            "Cooldown"  : 10,
            "Range"     : 5,
    },
]

numPlayersPerRound = 2
numCharacterPerTeam = 3
