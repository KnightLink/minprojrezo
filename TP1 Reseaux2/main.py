
#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys

HOTE = "127.0.0.1"
PORT = 4567

def servUDP_simple():
    testSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    testSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    
    try:
        testSocket.bind((HOTE,PORT))
    except socket.error:
        print("kk")
        sys.exit()
        
    print("Serveur on "+HOTE+":"+str(PORT))
    
    while 1:
        data,addr=testSocket.recvfrom(4096)
        if data:
            print(data.decode("utf-8"))
            
        msg="recu : "+data.decode("utf-8")
        testSocket.sendto(msg,addr)
        
        if data.upper()=="FIN":
            break
    
    print("closed")
    testSocket.close()
    sys.exit()
    
if __name__ == "__main__":
    servUDP_simple()
        
             

