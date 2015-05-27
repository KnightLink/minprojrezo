
import socket
import threading
from TCPServer import TCPServer 

from DebugOut import DebugOut

class PhyMaster(object):
    '''
    classdocs
    '''

    def __waitForAcknowledge(self,connection):
        found=False
        while not found:
            index=0
            for (thisConnection,clientAddr,line) in self.__commandlist:
                if thisConnection == connection:
                    (command, separator, line)=line.partition(",")
                    (result, separator, line)=line.partition(",")
                    if command=="STATUS":
                        found=True
                        self.__commandlist.pop(index)
                        self.__debugOut.out("PhyMaster %s - Waited for Acknowledge and got: %s %s" % (clientAddr, result, line))
                        if result=="ACK" :
                            result=True
                        else:
                            result=False
                index=index+1
            if not found:
                self.__receivedMessage.wait()
        return result
 
    def __nodeConnect(self, node, connectNode, clientAddr, listenPort, interfaceNumber):
        connectNode.connection.sendall(('CONNECT,%d,%s,%d\n' % (interfaceNumber,clientAddr[0],listenPort)).encode("utf-8"))
        retval=False
        if not self.__waitForAcknowledge(connectNode.connection):
            self.__debugOut.out("DEBUG: PhyMaster %s - connect for previous node %s failed" % (clientAddr,connectNode.clientAddr))
        else:
            connectNode.sendInterfaceConfig[interfaceNumber]=(clientAddr[0],listenPort)
            retval=True
        return retval

    def __nodeDisconnect(self, node, disconnectNode, interfaceNumber):
        # We can also safely disconnect the current node
        disconnectNode.connection.sendall(("DISCONNECT,%d\n" % interfaceNumber).encode("utf-8"))
        retval=False
        if not self.__waitForAcknowledge(disconnectNode.connection):
            self.__debugOut.out("DEBUG: PhyMaster %s - disconnect for current node %s failed" % (node.clientAddr,disconnectNode.clientAddr))
        else:
            disconnectNode.sendInterfaceConfig[interfaceNumber]=('',0)
            retval=True
            
        return retval
            
    def __nodeAddInterface(self, node, addInterfaceNode, interfaceNumber):
        (addInterfaceRingNumber, addInterfaceNodeNumber)=self.__phyNetwork.getNodePositionByConnection(addInterfaceNode.connection)
        listenPort=self.__phyNetwork.getListenInterfacePort(interfaceNumber,addInterfaceRingNumber, addInterfaceNodeNumber)
        acknowledge=False
        while not acknowledge:
            addInterfaceNode.connection.sendall(("ADDINTERFACE,%d,%d\n" % (interfaceNumber,listenPort)).encode("utf-8"))
            acknowledge=self.__waitForAcknowledge(addInterfaceNode.connection)
            if not acknowledge:
                listenPort=listenPort+1
        addInterfaceNode.listenInterfacePorts[interfaceNumber]=listenPort
        return True

    def __nodeDelInterface(self, node, delInterfaceNode, interfaceNumber):
        delInterfaceNode.connection.sendall(("DELINTERFACE,%d\n"% interfaceNumber).encode("utf-8"))
        retval=False
        if not self.__waitForAcknowledge(delInterfaceNode.connection):
            self.__debugOut.out("DEBUG: PhyMaster %s - delinterface for current node %s failed" % (node.clientAddr,delInterfaceNode.clientAddr))
        else:
            delInterfaceNode.listenInterfacePorts[interfaceNumber]=0
            retval=True
        return retval
    

 
    def __dispatchCommands(self):
        while True:
            self.__receivedMessage.acquire()
            while len(self.__commandlist)>0:
                (connection,clientAddr,thisCommand)=self.__commandlist.pop(0)
                (command, separator, line)=thisCommand.partition(",")
                if command == "ENTER":
                    self.__phyNetwork.addNode(connection, clientAddr)
                    self.__debugOut.out("ENTER : Entering configuration section")
                    thisNode=self.__phyNetwork.getNodeByConnection(connection)
                    if thisNode is None:
                        self.__debugOut.out("DEBUG: PhyMaster %s received ENTER request from unknown client" % (clientAddr,)) 
                    else:
                        (ringNumber, nodeNumber)=self.__phyNetwork.getNodePositionByConnection(connection)
                        # If this is the first node of a new Ring, we need to connect it downwards by enabling interface 1 of the lowerRing Node
                        if nodeNumber == 0 and ringNumber > 0:
                            lowerRingRouterNode=self.__phyNetwork.getLowerRingRouterNode(ringNumber)
                            (lowerRingNumber, lowerRingNodeNumber)=self.__phyNetwork.getNodePositionByConnection(lowerRingRouterNode.connection)
                            self.__nodeAddInterface(thisNode, lowerRingRouterNode, 1)
                            
                        # Let's imagine we want to insert B between A and C
                        self.__nodeAddInterface(thisNode, thisNode, 0)

                        (previousNode, previousInterfaceNumber)=self.__phyNetwork.getPreviousNode(ringNumber,nodeNumber)
                        # We are disconnecting A from C
                        self.__nodeDisconnect(thisNode, previousNode, previousInterfaceNumber)
                   
                        # We are connecting A to B
                        self.__nodeConnect(thisNode, previousNode, clientAddr, thisNode.listenInterfacePorts[0], previousInterfaceNumber)
                
                        # We are connecting B to C
                        (nextNode, nextInterfaceNumber)=self.__phyNetwork.getNextNode(ringNumber,nodeNumber)
                        
                        self.__debugOut.out("Trying to connect %s %d " % (nextNode.clientAddr[0],nextNode.listenInterfacePorts[0]))
                        
                        self.__nodeConnect(thisNode, thisNode, nextNode.clientAddr, nextNode.listenInterfacePorts[nextInterfaceNumber], 0)
                        
                    self.__phyNetwork.API_dumpPhyNetworkState()
                    self.__debugOut.out("ENTER : Leaving configuration section")
                elif command == "LEAVE":
                    self.__debugOut.out("LEAVE : Entering configuration section")
                    thisNode=self.__phyNetwork.getNodeByConnection(connection)
                    (ringNumber, nodeNumber)=self.__phyNetwork.getNodePositionByConnection(connection)
                    (previousNode, previousInterfaceNumber)=self.__phyNetwork.getPreviousNode(ringNumber,nodeNumber)
                    (nextNode, nextInterfaceNumber)=self.__phyNetwork.getNextNode(ringNumber,nodeNumber)
                    ringHandoverNode=None
                    if thisNode is None:
                        self.__debugOut.out("DEBUG: PhyMaster %s received LEAVE request from unknown client" % (clientAddr,))
                    else:  
                        # We first treat interface 0 : Reconnect previous and next node
                        # Assume, B is to be removed from the middle of A and C
                        
                        # We can disconnect the previous node in any case
                        self.__nodeDisconnect(thisNode, previousNode, previousInterfaceNumber)

                        # We can also safely disconnect the current node
                        self.__nodeDisconnect(thisNode, thisNode, 0)
                            
                        # We shutdown the current interface 0 which should no longer be connected in any case (even if immediate loop)
                        self.__nodeDelInterface(thisNode, thisNode, 0)

                        # Check whether we are the last node on the ring
                        if ringNumber > 0 and self.__phyNetwork.getRingLength(ringNumber)==1: 
                            # then the previousNode (and the nextNode should be the connection to the lower ring
                            if previousInterfaceNumber != 1:
                                self.__debugOut.out("DEBUG: PhyMaster %s - Something is strange, only one node left but previous is not on interface 1" % (clientAddr,))
                            else:
                                ringHandoverNode=previousNode
                                self.__nodeDelInterface(thisNode, previousNode, previousInterfaceNumber)
                                    
                        else: # This is the normal case, we have at least 2 nodes left
                            self.__nodeConnect(thisNode, previousNode, nextNode.clientAddr, nextNode.listenInterfacePorts[nextInterfaceNumber], previousInterfaceNumber)
                                  
                        # Check whether we are the uplink node
                        if thisNode.listenInterfacePorts[1]!=0:
                            if self.__phyNetwork.getRingLength(ringNumber)>1:
                                if previousNode.listenInterfacePorts[1]!=0:
                                    self.__debugOut.out("DEBUG: PhyMaster %s - Something is strange, there is a previous node which is an uplink but the current is uplink, too" % (clientAddr,))
                                else:
                                    # We need to do a Ring Handover here: Imagine, we have D2 -> D1 -> A2 with D1 being in Ring 1, the rest in Ring 2
                                    # Then we want to handover from D1 to C1 because we remove D1
                                    if ringHandoverNode == None:
                                        ringHandoverNode=previousNode
                                    (handoverRingNumber, handoverNodeNumber)=self.__phyNetwork.getNodePositionByConnection(ringHandoverNode.connection)
                                    
                                    # We first enable the interface 1 on C1
                                    self.__nodeAddInterface(thisNode, ringHandoverNode, 1)
                                    
                                    # Now we need to hand over the upper ring to the previous Node
                                    predecessorNode=self.__phyNetwork.getNodeByIndex(ringNumber+1,-1)
                                    sucessorNode=self.__phyNetwork.getNodeByIndex(ringNumber+1,0)
                                    
                                    # Then we connect D2 to C1
                                    self.__nodeDisconnect(thisNode, predecessorNode, 0)
                                    self.__nodeConnect(thisNode, predecessorNode, ringHandoverNode.clientAddr, ringHandoverNode.listenInterfacePorts[1], 0)
                                    
                                    # Now we connect C1 to A2
                                    self.__nodeDisconnect(thisNode, thisNode, 1)
                                    self.__nodeConnect(thisNode, ringHandoverNode, sucessorNode.clientAddr, sucessorNode.listenInterfacePorts[0], 1)
                                    
                            
                                    
                    self.__phyNetwork.delNode(ringNumber,nodeNumber)
                    self.__phyNetwork.API_dumpPhyNetworkState()
                    self.__debugOut.out("LEAVE : Leaving configuration section")
                else:
                    self.__debugOut.out("DEBUG: PhyMaster %s - Unknown Command %s" % (clientAddr,line))
            self.__receivedMessage.wait()
            

       

    def __masterListen(self, tcpServer, connection, clientAddr, data):
        self.__receivedMessage.acquire()
        while data:
            (line, separator, data)=data.partition("\n")
            self.__debugOut.out("DEBUG: PhyMaster %s - received %s" % (clientAddr,line))
            self.__commandlist.append((connection,clientAddr,line))
            self.__receivedMessage.notify()
        self.__receivedMessage.release()
  

    def __masterConnect(self, tcpServer, connection, clientAddr):
        self.__debugOut.out("PhyMaster %s - Incoming connection" % (clientAddr,))
    
    def __init__(self, phyNetwork):
        self.__host='' # We are listening on any incoming connection
        self.__phyNetwork=phyNetwork;
        self.__receivedMessage=threading.Condition()
        self.__debugOut=DebugOut(phyNetwork)
        self.active=False
        self.__commandlist=[]
        try:
            self.__masterServer=TCPServer(self.__host, self.__phyNetwork.baseport-1, self.__masterListen, self.__masterConnect)
            self.active=True
        except:
            self.__debugOut.out("PhyMaster : Master Server seems to be already running")

        if self.active:
            # This is the serialized dispatch thread
            self.__dispatchThread=threading.Thread(target=self.__dispatchCommands)
            self.__dispatchThread.start()

        

        