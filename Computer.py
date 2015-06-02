'''
Created on 17 mai 2015

@author: barkowsky-m
'''

from NetworkStack import NetworkStack
import threading
import time

class Computer(object):

    def __init__(self, ownIdentifier, sendDestinations=["A"], masterHost='127.0.0.1', baseport=10000):

        self.__masterHost=masterHost
        self.__baseport=baseport
        self.__networkstack=NetworkStack(self.__masterHost, self.__baseport, ownIdentifier)
        self.__sendDestinations=sendDestinations
        self.__ownIdentifier=ownIdentifier
        self.__appMessageList=[]
        self.startComputer()

    # The "APP" functions send a message to the other computers given in sendDestinations and counts the number of correctly received packets
    def appMessageReceived(self, source, applicationPort, message):
        self.__appThreadLock.acquire()
        self.__appMessageList.append((source,applicationPort,message))
        self.__appThreadLock.release()

    def appMessageReceive(self):
        self.__appStartedTime=time.clock()
        self.__appThreadLock=threading.Lock()

        self.__networkstack.applicationAddCallback(10,self.appMessageReceived)

        while True:
            self.__appThreadLock.acquire()
            currentList=self.__appMessageList[:]
            #        self.__appMessageList=[]
            self.__appThreadLock.release()

            totalNumber=0
            correct=0
            wrongDestination=0
            wrongApplicationPort=0
            outOfOrder=0
            lastReceived=-1000
            for (source,applicationPort,message) in currentList:
                totalNumber=totalNumber+1
                thisCorrect=True
                (messagebody, separator, remainder)=message.partition(",")
                (messagenumber, separator, remainder)=remainder.partition(",")
                (messagedestination, separator, remainder)=remainder.partition(",")

                if applicationPort!=10:
                    wrongApplicationPort=wrongApplicationPort+1
                    thisCorrect=False
                try:
                    messageNumberInt=int(float(messagenumber))
                except:
                    messageNumberInt=-2
                if lastReceived==-1000:
                    lastReceived=messageNumberInt-1

                if messageNumberInt != lastReceived+1:
                    outOfOrder=outOfOrder+1
                    thisCorrect=False
                if messagedestination!=self.__ownIdentifier:
                    wrongDestination=wrongDestination+1
                    thisCorrect=False

                if thisCorrect:
                    correct=correct+1
            #print("\n%s === Application Status of Computer %s after %.1f seconds:" % (self.__ownIdentifier, self.__ownIdentifier,(time.clock()-self.__appStartedTime)))
            #print("%s === Received %d messages with %d correct (%d out of order, %d wrong destination, %d wrong application)\n" % (self.__ownIdentifier, totalNumber, correct, outOfOrder, wrongDestination, wrongApplicationPort))
            time.sleep(1)

    def appMessageSend(self, destinationIdentifier="B"):
        for i in range(10):
            for d in self.__sendDestinations:
                thisMessage="Message n°%d from %s to %s" % (i, self.__ownIdentifier, d)
                #thisMessage="%s Sending Message n°%d to %s,%d,%s" % (self.__ownIdentifier, i,d,i,d)
                self.__networkstack.application_layer_outgoingPDU(d,10,thisMessage)

    # Please Adapt/Change
    def initiateToken(self):
        self.__networkstack.initiateToken()

    def startComputer(self):
        self.__application_incoming=threading.Thread(target=self.appMessageReceive)
        self.__application_incoming.start()

        self.__application_outgoing=threading.Thread(target=self.appMessageSend)
        self.__application_outgoing.start()

    def stopComputer(self):
        self.__networkstack.leaveNetwork()
