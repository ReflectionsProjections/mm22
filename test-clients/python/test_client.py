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
    return {'teamName':'test',
            'characters': [
                {"characterName": "warrior_one",
                 "classId": "warrior"},
                {"characterName": "warrior_two",
                 "classId": "warrior"},
                {"characterName": "warrior_three",
                 "classId": "warrior"},
            ]}

# Determine actions to take on a given turn, given the server response
def processTurn(serverResponse):
    # @competitors YOUR CODE HERE

    # Helpful variables
    actions = []
    myId = serverResponse["playerInfo"]["id"]

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
                    msg = processTurn(value) if "playerInfo" in value else initialResponse()
                    s.sendall(json.dumps(msg) + '\n')
                    data = s.recv(1024)
        else:
            data += s.recv(1024)
    s.close()
