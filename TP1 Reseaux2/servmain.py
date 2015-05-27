import sys
import socket

def servSimple():

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    try:
        serversocket.bind(('127.0.0.1', 4568))
    except socket.error:
        print("Erreur")
        sys.exit()
    serversocket.listen(5)
    print("serveur lance")
    
    while 1:
        clientsocket,addr=serversocket.accept()
        
        #if clientsocket:
         #   serversocket.send(bytes("connected : "+str(addr)))
        while 1:
            data=clientsocket.recv(2048)
            if data:
                print("server get : "+data.decode("utf-8"))
                clientsocket.send(b"recu : "+data)
            if data.decode("utf-8")=="FIN" or data.decode("utf-8")=="":
                break
        
        clientsocket.close()
        break
                
    serversocket.close()
    sys.exit()
    
if __name__ == "__main__":
    servSimple()
        
