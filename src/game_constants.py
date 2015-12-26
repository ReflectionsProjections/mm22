"""
Holds constants used by the core game logic
"""

class Classes:

    warrior = 
    {
            "Health": 500,
            "Damage": 50,
            "MovementSpeed": 5,
            "Abilities" : [ 1 ]
    }

"""
Defines the abilities
- Must contain in json:
    Target - 0 for self, 1 for target
    Attribute - Attribute of target to change
    Value - Value of attribute being changed
    Time - Total time this ability affects target
    Cooldown - number of ticks to refresh ability
"""
class Abilities:

    abilities = 
    [
        {
            "Target": 0,
            "Attribute": "MovementSpeed",
            "Value": 0,
            "Time": 5,
            "Cooldown": 10
        }
    ]


# Default number of players
numPlayers = 5
