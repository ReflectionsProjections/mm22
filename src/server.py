from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket

class SimpleEcho(WebSocket):
  def testMessages(self):
    self.sendMessage("{\"version\":\"1.0.0\", \"text\":\"Hello world!\"}")

  def handleMessage(self):
    # method gets called when server is pinged
    # use self.data to access incoming data
    print self.data
    self.sendMessage(self.data)

  def handleConnected(self):
    print (self.address, 'connected')
#   testMessages()
    self.sendMessage("{\"version\":\"1.0.0\", \"text\":\"Hello world!\"}")
#   self.sendMessage('Hello')

  def handleClose(self):
    print (self.address, 'closed')

server = SimpleWebSocketServer('', 8080, SimpleEcho)
server.serveforever()
