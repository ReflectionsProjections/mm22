from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import src.misc_constants as miscConstants
from threading import Thread

import json

clients = []
class WebSocketServer(WebSocket):

  def init(self, jsonFile):
    self.jsonFile = miscConstants.logFile

  def broadCastMessage(self, jsonFileName):
    data = []

    with open(jsonFileName, "o") as file:
      if file:
        for line in file.readlines():
          data.append(line)

    # Send message
    for client in clients:
     client.sendMessage(json.dumps({"data": data}))

  def handleMessage(self):
    # method gets called when server is pinged
    # use self.data to access incoming data
    self.sendMessage(self.data)

  def handleConnected(self):
    # Read json for data and send it
    print (self.address, 'connected')
    # self.sendMessage("{data: [{'teams': [{'id': 1,'teamName': 'Team1','characters': [{'charId': 1,'x': 0,'casting': None,'buffs': [],'name': 'Player1','attributes': {'AttackRange': 0,'Stunned': False,'Health': 500,'AttackSpeed': 5, 'Armor': 50,'MovementSpeed': 5,'MaxHealth': 500,'Damage': 100,'Silenced': False},'debuffs': [],'abilities': {0: 0.0, 1: 0.0},'y': 0,'class': 'warrior'}]}]}]}")
    clients.append(self)

  def handleClose(self):
    print (self.address, 'closed')

# WebSocket Server
serverInstance = WebSocketServer
server = SimpleWebSocketServer('', 8080, serverInstance)
t = Thread(target=server.serveforever, arg=(server,))
t.start()

input = input("Command:")
while len(input) != 0:
  if input[0] == "s ":
    jsonFileName = input[2:]
    serverInstance.broadCastMessage(jsonFileName)

# server = SimpleWebSocketServer('', 8080, SimpleEcho)
# server.serveforever()

# from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
#
# clients = []
# class SimpleChat(WebSocket):
#
#     def handleMessage(self):
#        for client in clients:
#           if client != self:
#              client.sendMessage(self.address[0] + u' - ' + self.data)
#
#     def handleConnected(self):
#        print self.address, 'connected'
#        for client in clients:
#           client.sendMessage(self.address[0] + u' - connected')
#        clients.append(self)
#
#     def handleClose(self):
#        clients.remove(self)
#        print self.address, 'closed'
#        for client in clients:
#           client.sendMessage(self.address[0] + u' - disconnected')
#
# server = SimpleWebSocketServer('', 8000, SimpleChat)
# server.serveforever()
