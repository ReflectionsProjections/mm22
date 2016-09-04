##
#   This is a basic socket server that connects to X clients, where X is passed in at runtime, and then stops accepting incoming connections.
#   It opens up the connection for each client on separate threads, so that it always knows which player it is communicating with,
#   and then sends turn information to the engine. It waits some small amount of time for a turn before assuming that none was sent.
#   It waits indefinitely for the engine to finish processing a turn, so it will never close if the engine crashes.
#   Upon receiving the turn data from the engine, it will ignore any messages sent while the turn was being processed,
#   and send a message back to the player to take their next turn.
#   If a connection is dropped, that player automatically 'forfeits'
#   When the game ends, the server should send a final status to all players and then shut down gracefully.
import sys
import select
import socket
import time
import json
# import game
import src.server.server_constants as server_constants


class _logger(object):
    """
    A simple logger that prints stuff out
    """

    def __init__(self, ):
        """
        Does nothing
        """

    def print_stuff(self, stuff):
        """
        prints stuff
        """
        print (str(stuff))


class MMServer(object):
    #   Constructs the server
    #   @param numPlayers number of players entering the game
    #   @param game Game object that holds the game state
    #   @param log location of the log file
    #   @param timeLimit
    #       The amount of time to wait for a player to make their turn
    #   @param maxDataSize
    #      The length in bytes of data received in one call to recv
    def __init__(self, numPlayers, game, logger=_logger(),
                 timeLimit=server_constants.time, maxDataSize=server_constants.maxDataSize):
        self.maxPlayers = numPlayers
        self.game = game
        self.logger = logger
        self.timeLimit = timeLimit
        self.maxDataSize = maxDataSize
        self.initialTimeLimit = server_constants.initialConnectTime

    ##
    #   Runs the game
    #   @param port the port number to wait on
    def run(self, port, run_when_ready=None, run_for_each=None, time_out=None):

        # Create an INET, STREAMing socket
        serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serversocket.bind(('localhost', port))
        serversocket.settimeout(time_out)
        serversocket.listen(self.maxPlayers)

        # Initialize data
        playerConnections = [None for i in range(0, self.maxPlayers)]
        turnObjects = [None for i in range(0, self.maxPlayers)]
        recval = ["" for i in range(0, self.maxPlayers)]
        forfeit = [False for i in range(0, self.maxPlayers)]
        validTurns = 0
        print ('connecting ...')

        # Gamerunner: Server is ready, start clients
        if run_when_ready:
            run_when_ready()

        # Accept connections from correct number of players
        for i in range(0, self.maxPlayers):
            # Keep track of which client is in which array pos to determine winner
            if run_for_each:
                run_for_each()
            (clientsocket, address) = serversocket.accept()
            playerConnections[i] = clientsocket
        lookupPlayer = dict(zip(playerConnections, [i for i in range(0, self.maxPlayers)]))
        print ('sockets connected ...')

        # Handle initial connections
        starting = True
        currTime = time.time()
        endTime = time.time() + self.initialTimeLimit
        while starting:
            ready = [[], [], []]
            if endTime - currTime > 0:
                ready = select.select(playerConnections, [], [], endTime - currTime)
            if ready[0] == []:

                # Forfeits when there is a timeout on initial connection
                for i in range(0, self.maxPlayers):
                    if turnObjects[i] is None:
                        turnObjects[i] = json.loads('{ "status": "Failure", "errors" : ["Timeout on initial connection, auto-forfeit. Verify your starting message ends with \'\\n\'"], "team_name": false }')
                        forfeit[i] = True
                        validTurns = validTurns + 1
            else:
                # Receive data
                for connection in ready[0]:
                    player = lookupPlayer[connection]
                    try:
                        recval[player] += connection.recv(self.maxDataSize)
                    except socket.error as e:
                        forfeit[player] = True
                        continue
                    validJson = True
                    if turnObjects[player] is None and "\n" in recval[player]:
                        data = recval[player].split("\n")[0]
                        try:
                            jsonObject = json.loads(data)
                        except (ValueError, TypeError) as e:
                            jsonObject = {}
                            validJson = False
                        if validJson:
                            (success, response) = self.game.add_new_player(jsonObject, player)
                            if success:
                                turnObjects[player] = response
                                validTurns = validTurns + 1
                            else:
                                try:
                                    connection.sendall(json.dumps(response, ensure_ascii=True) + "\n")
                                except IOError:
                                    pass
                        else:
                            try:
                                connection.sendall(json.dumps(json.loads('{ "status": "Failure", "errors" : ["Not valid JSON"], "team_name": false }'), ensure_ascii=True) + "\n")
                            except IOError:
                                pass
            if validTurns == self.maxPlayers:

                starting = False

                # Return turn info back to the clients
                for i in range(0, self.maxPlayers):
                    try:
                        playerConnections[i].sendall(json.dumps(turnObjects[i], ensure_ascii=True) + "\n")
                    except IOError:
                        pass
            currTime = time.time()
        self.logger.print_stuff(json.dumps(turnObjects))

        # Reset values
        validTurns = 0
        for i in range(0, self.maxPlayers):
            turnObjects[i] = None
            recval[i] = ""
        currTime = time.time()
        endTime = time.time() + self.timeLimit
        running = True
        errors = [[] for i in turnObjects]

        # Receive info
        while running:
            ready = [[], [], []]
            if endTime - currTime > 0:
                ready = select.select(playerConnections, [], [], endTime - currTime)
            if ready[0] == []:
                # Timeout
                for i in range(0, self.maxPlayers):
                    if turnObjects[i] is None:
                        turnObjects[i] = {}
                        errors[i] = ["Timeout. Make sure that your message ends with '\n'"]
                        validTurns = validTurns + 1
            else:

                # Receive data
                for connection in ready[0]:
                    player = lookupPlayer[connection]
                    try:
                        recval[player] += connection.recv(self.maxDataSize)
                    except socket.error as e:
                        forfeit[player] = True
                        continue
                    if turnObjects[player] is None and "\n" in recval[player]:
                        try:
                            turnObjects[player] = json.loads(recval[player])
                        except (ValueError, TypeError):
                            turnObjects[player] = {}
                            errors[player] = ["Invalid JSON"]
                        validTurns += 1
            if validTurns == self.maxPlayers:
                # Send turns to engine
                for i in range(0, self.maxPlayers):
                    if not forfeit[i] and errors[i] == []:
                        errors[i] = self.game.queue_turn(turnObjects[i], i)

                running = self.game.execute_turn()

                # Send turn results back to clients
                player_data_for_turn = [None] * self.maxPlayers
                for i in range(0, self.maxPlayers):
                    if not forfeit[i]:
                        try:
                            data = self.game.get_info(i)
                            if running:
                                data["errors"] = errors[i]
                            player_data_for_turn[i] = data
                            playerConnections[i].sendall(
                                json.dumps(player_data_for_turn[i], ensure_ascii=True) + "\n")
                        except IOError:
                            pass
                # Log results
                self.logger.print_stuff(json.dumps(self.game.get_all_info()))

                # Clear turn objects
                validTurns = 0
                for i in range(0, self.maxPlayers):
                    turnObjects[i] = None
                    recval[i] = ""
                errors = [[] for i in turnObjects]

                # Reset end-time
                currTime = time.time()
                endTime = time.time() + self.timeLimit
            else:
                currTime = time.time()
        # Close connections
        for conn in playerConnections:
            conn.close()
        serversocket.close()

"""
if __name__ == "__main__":
    serv = MMServer(constants["players"], game.Game(constants["map"]))
    serv.run(constants["port"])
"""
