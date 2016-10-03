class GameState(object):
    def __init__(self, ourTeam, enemyTeam, map):
        self.teams = {'allies': ourTeam, 'enemies': enemyTeam}
        self.map = map
        
STATE_DEFAULT = 0
STATE_RUNNING = 1
STATE_RAN = 2

class Agent(object):
    # charInfo is the Character obj created by server,
    # gameState is a gameState object
    def __init__(self, name, classId, ai_func):
        self.classId = classId
        self.ai_func = ai_func
        self.charInfo = None
        self.name = name
        self.target = None
        self.state = STATE_DEFAULT
        self.chasedOnThisTurn = False # Whether we chased the target on this turn. Reset to False at start of each getAction
        self.chaseTarget = None # The target we are currently tracking chase history for. Persists across calls to chaseTarget
        self.chaseCounter = 0 # The number of turns that we have been chasing chaseTarget for. Resets when we stop chasing
        self.move_history = list()
        self.turnsmoving = 0
        self.has_not_cast = True
        
    def getAction(self, gameState):
        action = None
        self.chasedOnThisTurn = False
        self.charInfo = [x for x in gameState.teams['allies'] if x.name == self.name][0]
        if self.target:
            # make sure our target doesn't have stale info
            self.target = [x for x in gameState.teams['enemies'] if x.id == self.target.id][0]
        if not self.target or self.target.is_dead():
            self.target = self.selectTarget(gameState)
        if self.target:
            action = self.ai_func(self, gameState)
        if not self.chasedOnThisTurn:
            self.chaseTarget = None
            self.chaseCounter = 0
        return action
        
    def setChasing(self):
        self.chasedOnThisTurn = True
        if self.target.id == self.chaseTarget:
            self.chaseCounter += 1
        else:
            self.chaseTarget = self.target.id
            self.chaseCounter = 0
        
    def addToMoveHistory(self, action):
        if len(self.move_history) > 5:
            self.move_history.remove(0)
        self.move_history.append(action)
        
    def selectTarget(self, gameState):
        # Caster list aka things we can interrupt
        casters = [
            'Druid',
            'Enchanter',
            'Sorcerer',
            'Paladin',
            'Wizard'
        ]

        # Choose a target
        priority_list = [
            'Druid',
            'Enchanter',
            'Sorcerer',
            'Wizard',
            'Archer',
            'Assassin',
            'Archer',
            'Paladin',
            'Warrior'
        ]
        
        target = None
        target_order = []
        
        target_order = [x for x in gameState.teams['enemies'] if not x.is_dead()]
        target_order.sort(key=lambda target: (8-priority_list.index(target.classId)) if not self.chaseLimitExceeded(target.id) else -1)
        

        if len(target_order) > 0:
            target = target_order[0]
        return target
        
    def chaseLimitExceeded(self, id):
        return self.chaseTarget == id and self.chaseCounter >= 4
        
    def get_best_location(self):

        character = self.charInfo

        cooldown = character.abilities[12]
        if cooldown == 0:
            return None #return None so we can cast Sprint

        print "me" + str(character.position)
        # for enemy in enemyteam:
            # print "enemy" + str(enemy.position)
        if character.position == (2, 1):
            # top, go up
            if character.attributes.movementSpeed == 2:
                destination = (3,0)
            else:
                destination = (2,0)

        elif character.position == (1, 2):
            # left, go left
            if character.attributes.movementSpeed == 2:
                destination = (0,1)
            else:
                destination = (0,2)

        elif character.position == (2, 3):
            # bottom, go down
            if character.attributes.movementSpeed == 2:
                destination = (1, 4)
            else:
                destination = (2, 4)

        elif character.position == (3, 2):
            # right, move right
            if character.attributes.movementSpeed == 2:
                destination = (4, 3)
            else:
                destination = (4, 2)

        elif character.position == (2, 2):
            # middle, go left
            if character.attributes.movementSpeed == 2:
                destination = (0, 2)
            else:
                destination = (1, 2)
        else:
            # we are in the perimeter, peruse around it
            x = character.position[0]
            y = character.position[1]
            if x == 0:
                if y == 0:
                    # top left, go right
                    destination = (x+1, y)
                else:
                    # we are on the left, go up
                    destination = (x, y-1)
            elif y == 0:
                if x == 4:
                    # top right, go down
                    destination = (x, y+1)
                #we are on the top, go left
                else:
                    destination = (x+1, y)
            elif x == 4:
                if y == 4:
                    # bottom right, go left
                    destination = (x-1, y)
                else:
                    #we are on the right, go down
                    destination = (x, y+1)
            elif y == 4:
                if x == 0:
                    # bottom left, go up
                    destination = (x, y-1)
                else:
                    # we are on the bottom, go left
                    destination = (x-1, y)
        return destination