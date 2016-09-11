#!/usr/bin/env python2
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import argparse
import src.misc_constants as miscConstants
import json

data = []

with open(miscConstants.logFile, "r") as file:
  if file:
    for line in file.readlines():
      data.append(json.loads(line))

clients = []

class WebSocketServer(WebSocket):

  def init(self, jsonFile):
    self.jsonFile = miscConstants.logFile

  def handleMessage(self):
    # method gets called when server is pinged
    # use self.data to access incoming data
    # self.sendMessage(self.data)
    return

  def handleConnected(self):
    # Read json for data and send it
    print (self.address, 'connected')
    clients.append(self)
    self.sendMessage(json.dumps({"data": data}))
#client.sendMessage('{"data": ' + data + '}')

  def handleClose(self):
    print (self.address, 'closed')

# WebSocket Server
server = SimpleWebSocketServer('', 8080, WebSocketServer)
server.serveforever()
