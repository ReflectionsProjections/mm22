#!/usr/bin/python2
import socket
import json
import random
import sys

# Python terminal colors; useful for debugging
# Make sure to concat a "printColors.RESET" to the end of your statement!
class printColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Debugging function
def log(x,c=printColors.BLUE):
    pass
    sys.stderr.write(c + str(x) + printColors.RESET + "\n")

# Set initial connection data
def initialResponse():
    # @competitors YOUR CODE HERE
    return {'teamName':'test'}

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    # @competitors YOUR CODE HERE

    # Helpful variables
    actions = []
    myId = serverResponse["playerInfo"]["id"]
    myNodes = [x for x in serverResponse["map"] if x["owner"] == myId]
    myP = sum(x["processingPower"] for x in myNodes)
    myN = sum(x["networkingPower"] for x in myNodes)

    # AI variables
    bestScore = 0
    target = None
    action = "control"

    # Node lists
    attackedNodes = [x for x in myNodes if max(x["infiltration"]) != 0]
    otherNodes = [x for x in serverResponse["map"] if x["owner"] != myId and x["isIPSed"] == False]
    #log("Player {} P {} / N {}".format(myId, myP, myN))
    #log("MINE " + str([x["id"] for x in myNodes]))
    #log("VIS  " + str([x["id"] for x in otherNodes]))

    # 1) Defend our nodes under attack
    if len(attackedNodes) != 0:
        for n in attackedNodes:
            score = max(n["infiltration"])*4
            if score > bestScore:
                target = n
                bestScore = score

                # Last stand of the DDoS
                if max(n["infiltration"]) > 0.5*(n["processingPower"] + n["networkingPower"]):
                    action = "ddos"

    # 2) Capture most powerful nearby node (with free ones being slightly worse than taken ones)
    if len(otherNodes) != 0:
        target = otherNodes[0]
        bestScore = 0
        for n in otherNodes:
            maxI = max(int(x) for x in n["infiltration"])
            iBoost = 0
            if not maxI:
                iBoost = (0 if int(n["infiltration"][str(myId)]) == maxI else maxI)
            score = n["processingPower"] + n["networkingPower"] - iBoost
            if myP < myN:
                score = n["networkingPower"]
            if myP > myN:
                score = n["processingPower"]

            score = score * 1.5 if n["owner"] != None else score
            if score > bestScore:
                target = n
                bestScore = score
                action = "control"

    rand = random.randint(0, 1)
    if rand == 0:
        actions.append({
            "action": action,
            "target": target["id"],
            "multiplier": min(myP, myN)
        })
    elif rand == 2:
        actions.append({
            "action": "portScan",
            "target": myNodes[0]['id'] 
        })
    elif rand == 3:
        actions.append({
            "action": "scan",
            "target": myNodes[0]['id'] 
        })
    elif rand == 4:
        actions.append({
            "action": "ddos",
            "target": target["id"]
        })
    elif rand == 1:
        actions.append({
            "action": "rootkit",
            "target": target["id"]
        })

    # Send actions to the server
    return {
        'teamName': 'test',
        'actions': actions
    }

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
                    msg = processTurn(value) if "map" in value else initialResponse()
                    s.sendall(json.dumps(msg) + '\n')
                    data = s.recv(1024)
        else:
            data += s.recv(1024)
    s.close()
