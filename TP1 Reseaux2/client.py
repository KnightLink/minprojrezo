import sys
import socket

def clientUDP_test():
    print("zozozozozozo")
    testSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    testSocket.sendto(bytes("FIN"),("127.0.0.1",4567))
    print("envoye")
    
    while 1:
        data,a=testSocket.recvfrom(2048)
        if data:
            print(data.decode("utf-8"))
        if data.decode("utf-8")=="recu : FIN":
            break
            
    testSocket.close()
    sys.exit()
    
clientUDP_test()
