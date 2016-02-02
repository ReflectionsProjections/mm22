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
			"Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 1,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,5 ]
	}
	"assassin" : {
			"Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,2 ]
	}
    "druid" : {
            "Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 1,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,3,4 ]
    }
    "enchanter" : {
            "Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 2,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,6,7 ]
    }
    "warrior" : {
            "Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,1 ]
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
    {   #0 suicide- probably never cast this
        "StatChanges": [{
            "Target": 0,
            "Attribute": "Health",
            "Change": -1000,
            "Time": 5
        }],
        "Cooldown"  : 10,
        "Range"     : 1,
    },
    {   #1 warrior stun (PROBABLY BROKEN)
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": True,
            "Time": 15
        }],
        "Cooldown"  : 60,
        "Range"     : 0,
    },
    {   #2 assassin armor debuff
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Armor",
            "Change": -10,
            "Time": 40
        }],
        "Cooldown"	: 100,
        "Range"		: 0,
    },
    {   #3 druid heal
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Health",
            "Change": 200,
            "Time": 0
        }],
        "Cooldown"  : 50,
        "Range"     : 1,
    },
    {   #4 druid armor buff
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Armor",
            "Change": 20,
            "Time": 30
        }],
        "Cooldown"  : 120,
        "Range"     : 1,
    },
    {   #5 archer attack speed buff (self)
        "StatChanges": [{
            "Target": 0,
            "Attribute": "AttackSpeed",
            "Change": -3,
            "Time": 20
        }],
        "Cooldown"  : 120,
        "Range"     : 0,
    },
    {   #6 enchanter curse
        "StatChanges": [{
            "Target": 1,
            "Attribute": "AttackSpeed",
            "Change": 2,
            "Time": 20
        },
        {
            "Target": 1,
            "Attribute": "Damage",
            "Change": -10,
            "Time": 20
        }],
        "Cooldown"  : 60,
        "Range"     : 2,
    },
    {   #6 enchanter buff
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Armor",
            "Change": 20,
            "Time": 20
        },
        {
            "Target": 1,
            "Attribute": "Damage",
            "Change": 20,
            "Time": 20
        }],
        "Cooldown"  : 60,
        "Range"     : 2,
    }
]

numPlayersPerRound = 2
numCharacterPerTeam = 3
