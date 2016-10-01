numPlayers = 2
numCharacterPerTeam = 3
totalTurns = 180

"""
Defines the classes
- Must contain in json
    Health - health of class
    Damage - damage dealt from autoattack
    SpellPower - added amount to spells in given direction (+ for healing, - for damage)
    AttackRange - range of attack in zones (range 0 = melee range)
    Armor - damage removed from each attack
    MovementSpeed - distant you can move in one turn
    Abilties - list of abilities
"""
classesJson = {
	"Archer" : {
			"Health"        : 1000,
            "Damage"        : 100,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 25,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,2,12 ] #sprint, armordebuff
	},
	"Assassin" : {
			"Health"        : 800,
            "Damage"        : 110,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 25,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,12,11 ] #sprint,backstab
	},
    "Druid" : {
            "Health"        : 1000,
            "Damage"        : 60,
            "SpellPower"    : 0,
            "AttackRange"   : 1,
            "Armor"         : 30,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,3,4,13 ] #heal, ranged armor buff, root
    },
    "Enchanter" : {
            "Health"        : 1000,
            "Damage"        : 45,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 25,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,6,7,5 ] #armor reduction, armor+dmg buff, silence
    },
    "Paladin" : {
            "Health"        : 1100,
            "Damage"        : 50,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 45,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,3,14 ] #heal, med cd stun
    },
    "Sorcerer" : {
            "Health"        : 800,
            "Damage"        : 80,
            "SpellPower"    : 0,
            "AttackRange"   : 2,
            "Armor"         : 20,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,8,16 ] #self damage buff, dot spell
    },
    "Warrior" : {
            "Health"        : 1200,
            "Damage"        : 75,
            "SpellPower"    : 0,
            "AttackRange"   : 0,
            "Armor"         : 50,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,1,15 ] #short cd stun, self armor buff
    },
    "Wizard" : {
            "Health"        : 1000,
            "Damage"        : 50,
            "SpellPower"    : 0,
            "AttackRange"   : 1,
            "Armor"         : 20,
            "MovementSpeed" : 1,
            "Abilities"     : [ 0,9,10 ] #damage spell, long cd stun
    }
}

"""
Defines the abilities
- Must contain in json:
    List of stat changes
        Target - 0 for self, 1 for any target
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
            "Change": 1,
            "Time": 0
        },
        {
            "Target": 0,
            "Attribute": "Silenced",
            "Change": 1,
            "Time": 0
        },
        {
            "Target": 0,
            "Attribute": "Rooted",
            "Change": 1,
            "Time": 0
        }],
        "CastTime"  : 0,
        "Cooldown"  : 30,
        "Range"     : 0,
    },
    {   #1 melee stun 
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": -1,
            "Time": 2
        }],
        "CastTime"  : 0,
        "Cooldown"  : 6,
        "Range"     : 0,
    },
    {   #2 armor debuff
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Armor",
            "Change": -10,
            "Time": 4
        }],
        "CastTime"  : 0,
        "Cooldown"	: 10,
        "Range"		: 2,
    },
    {   #3 ranged heal
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": 250,
            "Time": 0
        }],
        "CastTime"  : 2,
        "Cooldown"  : 3,
        "Range"     : 1,
    },
    {   #4 ranged armor buff
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Armor",
            "Change": 40,
            "Time": 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 8,
        "Range"     : 1,
    },
    {   #5 Silence
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Silenced",
            "Change": -1,
            "Time": 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 6,
        "Range"     : 2,
    },
    {   #6 ranged damage reduction curse
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Damage",
            "Change": -20,
            "Time": 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 5,
        "Range"     : 2,
    },
    {   #7 ranged armor and damage buff
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Armor",
            "Change": 20,
            "Time": 3
        },
        {
            "Target": 1,
            "Attribute": "Damage",
            "Change": 30,
            "Time": 3
        }],
        "CastTime"  : 2,
        "Cooldown"  : 6,
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
            "Time" : 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 0,
        "Range"     : 0,
    },
    {   #9 deep freeze
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": -1,
            "Time": 2
        }],
        "CastTime"  : 0,
        "Cooldown"  : 10,
        "Range"     : 2,
    },
    {   #10 frostbolt
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": -250,
            "Time": 0
        }],
        "CastTime"  : 2,
        "Cooldown"  : 3,
        "Range"     : 1,
    },
    {   #11 Backstab
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": -200,
            "Time": 0
        }],
        "CastTime"  : 0,
        "Cooldown"  : 6,
        "Range"     : 0,
    },
    {   #12 Sprint
        "StatChanges": [{
            "Target": 0,
            "Attribute": "MovementSpeed",
            "Change": 1,
            "Time": 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 8,
        "Range"     : 1,
    },
    {   #13 Root
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Rooted",
            "Change": -1,
            "Time": 3
        }],
        "CastTime"  : 0,
        "Cooldown"  : 6,
        "Range"     : 1,
    },
    {   #14 Smite
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Stunned",
            "Change": -1,
            "Time": 2
        }],
        "CastTime"  : 0,
        "Cooldown"  : 8,
        "Range"     : 1,
    },
    {   #15 self armor buff
        "StatChanges": [{
            "Target": 0,
            "Attribute": "Armor",
            "Change": 30,
            "Time": 3
        }],
        "CastTime"  : 2,
        "Cooldown"  : 7,
        "Range"     : 0,
    },
    {   #16 corruption
        "StatChanges": [{
            "Target": 1,
            "Attribute": "Health",
            "Change": -200,
            "Time": 0
        }],
        "CastTime"  : 2,
        "Cooldown"  : 5,
        "Range"     : 2,
    },
]
