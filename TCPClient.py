import socket
import threading

class TCPClient(object):
    '''
    Client for TCP Connections
    '''

    def clientListenThread(self, connection, clientAddr):
        self.listenStarted.release()
        while True:
            data = connection.recv(1024)
            if self.callBackReceive is not None:
                self.callBackReceive(self, connection, clientAddr, data.decode("utf-8"))
            if not data:
                break
 

    def startClient(self):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            self.clientSocket.connect((self.host, self.port))
        except socket.error as msg:
            print("TCPClient : Connection failed %s" % msg)
            return False
        print("connected")
        
        self.listenStarted=threading.Lock()
        self.listenStarted.acquire()
        
        self.listenThread=threading.Thread(target=self.clientListenThread, args=(self.clientSocket,(self.host, self.port)))
        self.listenThread.start()
        self.listenStarted.acquire()
        self.connected=True
      
    def stopClient(self):
        self.clientSocket.shutdown(socket.SHUT_RDWR)
        self.clientSocket.close()
        self.connected=False

    def send(self, data):
        self.clientSocket.sendall(data.encode("utf-8"))

    def isConnected(self):
        return self.connected

    def __init__(self, host, port, callBackReceive=None):
        self.host=host
        self.port=port
        self.callBackReceive=callBackReceive
        
        self.connected=False
        
        self.startClient()

        
