import socket
import sys
import threading

def serveurTCP():
    class ThreadClient(threading.Thread):
        def __init__(self,conn):
            threading.Thread.__init__(self)
            self.connexion=conn
            
        def run(self):
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            serversocket.bind(('127.0.0.1', 4568))
            serversocket.listen(5)
            while 1:
                clientsocket,addr=serversocket.accept()
                clientthread=ThreadClient(clientsocket)
                clientthread.start()
            serversocket.close()
            sys.exit()
            
if __name__=="__main__":
    serveurTCP()
                               
