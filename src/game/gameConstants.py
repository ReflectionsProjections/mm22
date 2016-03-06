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
    "dummy_one" : {
			"Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,5 ]
	}
    "dummy_two" : {
			"Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,5 ]
	}
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
    "paladin" : {
            "Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 0,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,3 ]
    }
    "sorcerer" : {
            "Health"        : 500,
            "Damage"        : 100,
            "AttackRange"   : 1,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
            "Abilities"     : [ 0,8 ]
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
    "wizard" : {
            "Health"        : 500,
            "Damage"        : 50,
            "AttackRange"   : 1,
            "AttackSpeed"   : 5,
            "Armor"         : 50,
            "MovementSpeed" : 5,
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
        {
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
        "Range":    : 0,
    },
    {   #9 deep freeze
        "StatChanges": [{
        {
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
        {
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
        {
            "Target": 1,
            "Attribute": "Health",
            "Change": -200,
            "Time": 0
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #12 dummy_health_pos
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Health",
            "Change": 100,
            "Time": 0
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #13 dummy_health_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Health",
            "Change": -100,
            "Time": 0
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #14 dummy_damage_buff
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Damage",
            "Change": 100,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #15 dummy_damage_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Damage",
            "Change": -100,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #16 dummy_attackrange_pos
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "AttackRange",
            "Change": 1,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #17 dummy_attackrange_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "AttackRange",
            "Change": -1,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #18 dummy_attackspeed_pos
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "AttackSpeed",
            "Change": 1,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #19 dummy_attackspeed_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "AttackSpeed",
            "Change": 100,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #20 dummy_armor_pos
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Armor",
            "Change": 100,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #21 dummy_armor_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Armor",
            "Change": 100,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #22 dummy_movementspeed_pos
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "MovementSpeed",
            "Change": 1,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #23 dummy_movementspeed_neg
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "MovementSpeed",
            "Change": -1,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    }
    {   #24 dummy_stun
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Stunned",
            "Change": True,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #25 dummy_silence
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Silenced",
            "Change": True,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    {   #24 dummy_root
        "StatChanges": [{
        {
            "Target": 3,
            "Attribute": "Rooted",
            "Change": True,
            "Time": 30
        }],
        "Cooldown"  : 30,
        "Range"     : 1,
    },
    
]

numPlayersPerRound = 2
numCharacterPerTeam = 3
