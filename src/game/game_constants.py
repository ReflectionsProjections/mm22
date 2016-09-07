numPlayers = 2
numCharacterPerTeam = 3
totalTurns = 400

"""
Defines the classes
- Must contain in json
    Health - health of class
    Damage - damage dealt from autoattack
    SpellPower - added amount to spells in given direction
    AttackRange - range of attack in zones (range 0 = melee range)
    Armor - damage removed from each attack
    MovementSpeed - cooldown (in ticks) on ability to move to adjacent zone
    Abilties - list of abilities
"""
classesJson = {
	"archer" : {
			"Health"        : 500,
            "Damage"        : 50,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 50,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,5 ]
	},
	"assassin" : {
			"Health"        : 400,
            "Damage"        : 60,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 30,
            "MovementSpeed" : 2,
            "Abilities"     : [ 0,2 ]
	},
    "druid" : {
            "Health"        : 600,
            "Damage"        : 50,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 60,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,3,4 ]
    },
    "enchanter" : {
            "Health"        : 400,
            "Damage"        : 65,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 50,
            "MovementSpeed" : 2,
            "Abilities"     : [ 0,6,7 ]
    },
    "paladin" : {
            "Health"        : 700,
            "Damage"        : 40,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 70,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,3 ]
    },
    "sorcerer" : {
            "Health"        : 500,
            "Damage"        : 75,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 50,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,8 ]
    },
    "warrior" : {
            "Health"        : 600,
            "Damage"        : 75,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 70,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,1 ]
    },
    "wizard" : {
            "Health"        : 500,
            "Damage"        : 50,
            "SpellPower"    : 0,
            "AttackRange"   : 1,
            "Armor"         : 50,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,9,10,11 ]
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
    {   #0 burst - break crowd control with a long cooldown
        "StatChanges": [{
            "Target": 0,
            "Attribute": "Stunned",
            "Change": False,
            "Time": 0
        },
        {
            "Target": 0,
            "Attribute": "Silenced",
            "Change": False,
            "Time": 0
        },
        {
            "Target": 0,
            "Attribute": "Rooted",
            "Change": False,
            "Time": 0
        }],
        "Cooldown"  : 120,
        "Range"     : 0,
    },
    {   #1 melee stun (PROBABLY BROKEN)
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": True,
            "Time": 10
        }],
        "Cooldown"  : 60,
        "Range"     : 0,
    },
    {   #2 armor debuff
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Armor",
            "Change": -10,
            "Time": 40
        }],
        "Cooldown"	: 100,
        "Range"		: 0,
    },
    {   #3 ranged heal
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Health",
            "Change": 200,
            "Time": 0
        }],
        "Cooldown"  : 50,
        "Range"     : 1,
    },
    {   #4 ranged armor buff
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Armor",
            "Change": 20,
            "Time": 30
        }],
        "Cooldown"  : 120,
        "Range"     : 1,
    },
    {   #5 attack speed buff (self)
        "StatChanges": [{
            "Target": 0,
            "Attribute": "AttackSpeed",
            "Change": -3,
            "Time": 20
        }],
        "Cooldown"  : 120,
        "Range"     : 0,
    },
    {   #6 ranged damage reduction curse
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Damage",
            "Change": -10,
            "Time": 20
        }],
        "Cooldown"  : 60,
        "Range"     : 2,
    },
    {   #7 ranged armor and damage buff
        "StatChanges": [{
            "Target": 2,
            "Attribute": "Armor",
            "Change": 20,
            "Time": 20
        },
        {
            "Target": 2,
            "Attribute": "Damage",
            "Change": 20,
            "Time": 20
        }],
        "Cooldown"  : 60,
        "Range"     : 2,
    },
    {   #8 sacrifice health for damage (self)
        "StatChanges": [{
            "Target": 0,
            "Attribute": "Health",
            "Change": -150,
            "Time": 0
        },
        {   "Target": 0,
            "Attribute": "Damage",
            "Change": 50,
            "Time" : 20
        }],
        "Cooldown"  : 60,
        "Range"     : 0,
    },
    {   #9 deep freeze
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": True,
            "Time": 10
        }],
        "Cooldown"  : 120,
        "Range"     : 1,
    },
    {   #10 frostbolt
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": -200,
            "Time": 0
        }],
        "Cooldown"  : 25,
        "Range"     : 1,
    },
    {   #11 icicles
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": -200,
            "Time": 0
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    }
]
