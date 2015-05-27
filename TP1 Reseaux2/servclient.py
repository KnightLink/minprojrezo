import socket
import sys
import time

def clientSimple():
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect(("127.0.0.1",4568))
    except socket.error:
        print("erreur")
        sys.exit()
    clientsocket.send(b"coucou")
    while 1:
        data=clientsocket.recv(2048)
        if data:
            print("from server : "+data.decode("utf-8"))
            if data.decode("utf-8")=="recu : FIN":
                break
                
    clientsocket.close()
    sys.exit()
    
clientSimple()
