
import threading
import LayerPhy
import math
import random

class NetworkStack(object):

    TAILLE_HEADER = 13

    class Header :

        def __init__(self, vers, type, dest, debut_mess, src, taille) :
            self.vers=str(vers)
            self.type=str(type)
            self.dest=str(dest)
            self.debut_mess=str(debut_mess)
            self.src=str(src)
            self.taille=str(taille)

        def to_string_parse(self) :
            return  self.vers+self.type+self.dest+self.debut_mess+self.src+self.taille+self.data

        def to_header_parse(string) :
            new_header = Header(string[0],string[1],string[2:3],string[4:7],string[8:9],string[10:12])
            return new_header

    class SousPaquet :
        def __init__(self, header, data) :
            self.header=header
            self.data=data

        def to_souspaquet_parse(header_string, data_string):
            header=Header.to_header_parse(header_string)
            return SousPaquet(header,data_string)

        def to_string_header_parse(self):
            return header.to_string_parse

    class Paquet :

        def __init__(self) :
            self.sous_paquets=[]

        def add_souspaquet(self, souspaquet):
            sous_paquets.append(souspaquet)

        def get_nb_paquets(self) :
            return self.sous_paquets[0].debut_mess/TAILLE_HEADER
        
        def to_paquet_parse(string) :
            packet=Paquet()
            # exploration du string puis appels de to_souspaquet_parse à la suite, puis append de tous les sous-paquets à la suite dans le tableau sous_paquets
            return 1

        def to_string_parse(self) :
            # appelle to_string_header parse de tous les paquets, puis concatène tous les data pour créer un string (datagram)
            # ne pas oublier de mettre à jour les pointeurs vers data avant de concaténer
            return ""
            


    def __init__(self, masterHost='127.0.0.1', baseport=10000, ownIdentifier='x'):
        self.__applicationList=[]
        self.__physicalLayer=LayerPhy.LayerPhy(upperLayerCallbackFunction=self.layer2_incomingPDU, masterHost=masterHost, baseport=baseport)
        self.__ownIdentifier=ownIdentifier
        self.layer3_outputAvailable=False
        self.layer3_numberOfDataPacketsEmpty=0
        self.layer3_outputBlockingCondition=threading.Condition()
        self.layer3_outputDoneCondition=threading.Condition()
        # stockage des headers, souspaquets, list à traiter. Sont utilisés lors du traitement d'un paquet et sont vidées car c'est envoyé.
        self.headerlist=[]
        self.souspaquetlist=[]
        self.paquetlis[]

    def leaveNetwork(self):
        self.__physicalLayer.API_leave()

    # Do not change!
    def applicationAddCallback(self, applicationPort, callBack):
        self.__applicationList.append((applicationPort, callBack))

    # Do not change!
    def application_layer_incomingPDU(self, source, applicationPort, pdu):
        for (thisApplicationPort, thisApplication) in self.__applicationList:
            if thisApplicationPort==applicationPort:
                thisApplication(source, applicationPort, pdu)

    # Do not change!
    def application_layer_outgoingPDU(self, destination, applicationPort, pdu):
        self.layer4_outgoingPDU(destination, applicationPort, pdu)

    # Please change: This sends the first TOKEN to the ring
    def initiateToken(self):
        self.__physicalLayer.API_sendData(0, "TOKEN")

    # Please adapt!
    # Take care: The parameters of incoming (data packets arriving at the computer) and outgoing (data packets leaving from the computer)
    # should generally agree with one layer difference (i.e. here we treat the applicationPort, an identifier that sais which application
    # is asked to handle the traffic
    def layer4_incomingPDU(self, source, pdu):
        # traitement data des sous-paquets reçus
        # suppression des paquets lus / paquets dont nous sommes la destination
        
        print("%s Layer4_in: Received (%s) from %s " % (self.__ownIdentifier,pdu, source))
        self.application_layer_incomingPDU(source,10,pdu)


    # Please adapt
    def layer4_outgoingPDU(self, destination, applicationPort, pdu):
        # Création du header et des données
        
        print("%s Layer4_out: Sending message (%s) to %s " % (self.__ownIdentifier, pdu, destination))
        self.layer3_outgoingPDU(destination, pdu)

    # Please adapt!
    # The current situation is that in this layer, the network stack takes the decision to forcibly keep the packet because it thinkgs that it is destined to this computer
    # It also authorizes immediately that a new packet can be put onto the network.
    def layer3_incomingPDU(self, interface, pdu):
        
        # 1) On isole les paquets pour nous en créant des SousPaquet

        print("%s Layer3_in: Received (%s) on interface %d: " % (self.__ownIdentifier, pdu, interface))
        # Say, we treat destination here
        # Maybe we can give away one packet if we received one?
        self.layer4_incomingPDU("A", pdu)

        self.layer3_outputBlockingCondition.acquire()
        if self.layer3_outputAvailable:
            self.layer3_numberOfDataPacketsEmpty=1
            self.layer3_outputBlockingCondition.notify()
            self.layer3_outputBlockingCondition.release()
        else:
            self.layer3_outputBlockingCondition.release()

    # Please adapt
    def layer3_outgoingPDU(self, destination, pdu):
        # Compilation du paquet sous forme de string
        self.layer3_outputBlockingCondition.acquire()
        self.layer3_outputAvailable=True
        while self.layer3_numberOfDataPacketsEmpty<1:
            self.layer3_outputBlockingCondition.wait()
        print("%s Layer3_out: Sending out (%s) via interface %d " % (self.__ownIdentifier, pdu, 0))
        self.layer2_outgoingPDU(0, pdu)
        self.layer3_numberOfDataPacketsEmpty=self.layer3_numberOfDataPacketsEmpty-1
        self.layer3_outputBlockingCondition.release()

    # Please adapt
    def layer2_incomingPDU(self, interface, pdu):
        # Coup d'oeil aux headers
        # 1) Parsing du paquet (à faire : paquet_parse)

        # 1bis) Vérification getnbpaquet : si 0, on forward (layer2_outgoingPDU)

        # 2) Boucle qui regarde la liste des headers : boolean à vrai si un des mess est pour nous

        # 3) Si on n'a pas de message pour nous on passe direct a 2_outgoing, sinon on passe a 3_in pour traiter le paquet plus en détail
        
        #print("%s Layer2: Received (%s) on Interface %d:  " % (self.__ownIdentifier, pdu, interface))
        if interface == 0 : # same ring
            # Forward in 50% of the cases
            if random.randint(0,1):
                self.layer2_outgoingPDU(interface,pdu)
                print("%s Layer2_in: Received (%s) on Interface %d:  " % (self.__ownIdentifier, pdu, interface))
                print("%s Layer2_in: tirage (%s) -> layer2_out\n" % (self.__ownIdentifier, pdu))
            else:
                self.layer3_incomingPDU(interface,pdu)
                print("%s Layer2_in: Received (%s) on Interface %d:  " % (self.__ownIdentifier, pdu, interface))
                print("%s Layer2_in: tirage (%s) -> layer3_in\n" % (self.__ownIdentifier, pdu))
        else: # Another Ring, this is for routing, see later
            pass

    def layer2_outgoingPDU(self, interface, pdu):
        # Envoi du paquet
        print("%s Layer2: Sending out (%s) via interface %d " % (self.__ownIdentifier, pdu, interface))
        self.__physicalLayer.API_sendData(interface, pdu)

#le mess arrive en layer 2 in, et on a le choix : soit direct layer 2 out, soit traitements layer 3, 4 in, puis layer 4, 3, 2 out

