import socket
import threading

class TCPServer(object):
    '''
    This class opens a TCP port connection as server
    '''

    def serverConnectionThread(self, connection, clientAddr):
        if self.callBackConnect is not None:
            self.callBackConnect(self, connection, clientAddr)
        while True:
            data = connection.recv(1024)
            if self.callBackReceive is not None:
                self.callBackReceive(self, connection, clientAddr, data.decode("utf-8"))
            if not data:
                break


    def serverListenThread(self):
        self.serverSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            self.serverSocket.bind((self.host,self.port))
            self.serverSocket.listen(10)
        except socket.error as msg:
            print("Server bind has failed %s" % msg)
            self.serverSocket.close()
            self.serverStarted.release()
            return
        self.serving=True
        self.stopServing=False
        self.serverStarted.release()
        while (not self.stopServing):
            connection, clientAddr = self.serverSocket.accept()
            print("Connected by", clientAddr)
            connectionThread=threading.Thread(target=self.serverConnectionThread,args=[connection, clientAddr])
            connectionThread.start()
        self.serverSocket.shutdown(socket.SHUT_RDWR)
        self.serving=False
        self.serverSocket.close()

    def startServer(self):
        self.serverStarted=threading.Lock()
        self.serverStarted.acquire()

        self.listenThread=threading.Thread(target=self.serverListenThread)
        self.listenThread.start()
        self.serverStarted.acquire()

    def stopServer(self):
        self.stopServing=True

    def isServing(self):
        return self.serving


    def __init__(self, host, port, callBackReceive=None, callBackConnect=None):
        self.host=host
        self.port=port
        self.callBackReceive=callBackReceive
        self.callBackConnect=callBackConnect

        self.serving=False
        self.serverStarted=False
        self.startServer()
