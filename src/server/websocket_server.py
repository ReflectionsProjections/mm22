from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

class WebSocketServer(WebSocket):

    def init(self, logFile):
        self.logFile = logFile

        self.clients = []

    def handleConnected(self):
        print(self.address, 'connected')

        #append client
        #read file, send all

    def sendMessage(self, json):
        self.sendMessage(str(json))

    def broadCastMessage(self, json):
        return

    def handleClose(self):
        print (self.address, 'closed')