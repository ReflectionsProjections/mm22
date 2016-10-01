#!/usr/bin/env python2
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import src.misc_constants as misc_constants
import json


class WebSocketServer(WebSocket):

    def handleMessage(self):
        # method gets called when server is pinged
        # use self.data to access incoming data
        # self.sendMessage(self.data)
        return

    def handleConnected(self):
        # Read json for data and send it
        print(self.address, 'connected')

        data = []

        with open(misc_constants.logFile, "r") as file:
            if file:
                for line in file.readlines():
                    data.append(json.loads(line))

        self.sendMessage(json.dumps({"data": data}))

    def handleClose(self):
        print(self.address, 'closed')

# WebSocket Server
server = SimpleWebSocketServer('', 8080, WebSocketServer)
server.serveforever()
