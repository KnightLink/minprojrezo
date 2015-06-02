
import threading
import LayerPhy
import math
import random

class NetworkStack(object):

    TAILLE_HEADER = 12

    class Header :

        def __init__(self, vers, dest, debut_mess, src, taille) :
            
            # tailles :: vers : 1, dest : 2, debut_mess : 4, src : 2, taille : 3

            self.vers=str(vers)
            
            if len(str(dest)) == 2 :
                self.dest=str(dest)
            else :
                str_dest = ""
                for i in range (len(str(dest)),2) :
                    str_dest = str_dest + "0"
                str_dest = str_dest + str(dest)
                self.dest=str_dest

            if len(str(debut_mess)) == 4 : #le numéro du caractère ou commence les datas de ce messages
                self.debut_mess=str(debut_mess)
            else :
                str_deb_mess = ""
                for i in range (len(str(debut_mess)),4) :
                    str_deb_mess = str_deb_mess + "0"
                str_deb_mess = str_deb_mess +str(debut_mess)
                self.debut_mess=str_deb_mess
                
            if len(str(src)) == 2 :
                self.src=str(src)
            else :
                str_src = ""
                for i in range (len(str(src)),2) :
                    str_src = str_src + "0"
                str_src = str_src + str(src)
                self.dest=str_src

            if len(str(taille)) == 3 : #la taille des datas de ce message
                self.taille=str(taille)
            else :
                str_taille = ""
                for i in range (len(str(taille)),3) :
                    str_taille = str_taille + "0"
                str_taille = str_taille + str(taille)
                self.taille=str_taille

        def to_string_parse(self) : #renvoie le header en string
            return  self.vers+self.dest+self.debut_mess+self.src+self.taille+self.data

        def to_header_parse(string) : #crée un header à partir d'un string
            new_header = Header(string[0],string[1:2],string[3:6],string[7:8],string[9:11])
            return new_header

    class SousPaquet :
        def __init__(self, header, data) :
            self.header=header
            self.data=data

        def to_souspaquet_parse(header_string, data_string): #crée un sous paquet à partir de 2 strings
            header=Header.to_header_parse(header_string)
            return SousPaquet(header,data_string)

        def to_string_header_parse(self): #renvoie le sous_paquet en string
            return header.to_string_parse

    class Paquet :

        def __init__(self) :
            self.sous_paquets=[]

        def add_souspaquet(self, souspaquet):
            sous_paquets.append(souspaquet)

        def get_nb_paquets(self) : #donne le nombre de sous paquets dans le paquet
            if self.sous_paquets!=[]:
                return int(int(self.sous_paquets[0].header.debut_mess)/NetworkStack.TAILLE_HEADER)
            else :
                return 0
        
        def to_paquet_parse(string) : #renvoie un paquet à partir d'un string
            if string != "" :
                packet=NetworkStack.Paquet()
                nb_paquets = int(string[4:7])/NetworkStack.TAILLE_HEADER
                while string != "" :
                # exploration du string puis appels de to_souspaquet_parse à la suite,
                # puis append de tous les sous-paquets
                # à la suite dans le tableau sous_paquets
                    header = string
                    cur_debut_mess = int(header[3:6])
                    cur_fin_data = cur_debut_mes + int(header[9:11]) #debut du mess + taille du mess
                    data = header[cur_debut_mess:cur_fin_mess]
                    header = header[0:11]
                    sous_packet = to_souspaquet_parse(header,data)
                    packet.add_souspaquet(sous_paquet)
                    string = string[12:cur_debut_mess] + string[cur_fin_mess:]
                    #on enlève la partie qu'on vient d'ajouter à la liste
                                  
                if packet.get_nb_paquets() == nb_paquets : #on verifie quon a bien ajouté tous les messages dans la liste
                    return packet
                else :
                    print("Problème to_paquet_parse \n")
                    return NetworkStack.Paquet()
            else :
                return NetworkStack.Paquet()

        def to_string_parse(self) : #crée un string a partir du paquet
            prev_data = 0
            return_string=""
            
            for i in range (0,self.get_nb_paquets()-1) : #on ajoute tous les headers
                data = self.sous_packets[i].header.debut_mess
                #on met à jour les pointeurs des headers ici
                self.sous_packets[i].header.debut_mess = self.get_nb_paquets() * TAILLE_HEADER + prev_data+1
                prev_data = data
                return_string = return_string + self.sous_packets[i].header.to_string_parse()
                
            for i in range (0,self.get_nb_paquets()-1) : #on ajoute tous les datas
                return_string = return_string + self.sous_packets[i].data
                #data est déja un string
                
            return return_string
            

    def __init__(self, masterHost='127.0.0.1', baseport=10000, ownIdentifier='x'):
        self.__applicationList=[]
        self.__physicalLayer=LayerPhy.LayerPhy(upperLayerCallbackFunction=self.layer2_incomingPDU, masterHost=masterHost, baseport=baseport)
        self.__ownIdentifier=ownIdentifier
        self.layer3_outputAvailable=False
        self.layer3_numberOfDataPacketsEmpty=0
        self.layer3_outputBlockingCondition=threading.Condition()
        self.layer3_outputDoneCondition=threading.Condition()
        # stockage des headers, souspaquets, list à traiter. Sont utilisés lors du traitement d'un paquet et sont vidés car c'est envoyé.
        self.header_list=[]
        self.data_list=[]
        self.sous_paquet_list=[]
        self.paquet=NetworkStack.Paquet()
        self.layer4_packet_arrived=False
        self.layer4_outputBlockingCondition=threading.Condition()
        self.layer4_outputDoneCondition=threading.Condition()

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
    # Notre premier paquet est un paquet vide et pas un token
    def initiateToken(self):
        self.__physicalLayer.API_sendData(0, NetworkStack.Paquet().to_string_parse())

    # Please adapt!
    # Take care: The parameters of incoming (data packets arriving at the computer) and outgoing (data packets leaving from the computer)
    # should generally agree with one layer difference (i.e. here we treat the applicationPort, an identifier that says which application
    # is asked to handle the traffic
    def layer4_incomingPDU(self, source, pdu):
        
        for elt in self.paquet.sous_paquets : #on supprime les messages que nous avons nous-même envoyés
            if elt.header.src == self.__ownIdentifier :
                self.paquet.sous_paquets.pop(elt)

        # lecture des data des sous-paquets reçus, envoi des réponses et suppression des ces sous paquets du paquet

        for elt in self.paquet.sous_paquets :
            if elt.header.dest == self.__ownIdentifier :
                print("%s Layer4_in: Received (%s) from %s " % (self.__ownIdentifier, elt.data, elt.header.src))
                self.paquet.sous_paquets.pop(elt)

        #on informe outgoing que l'on a reçu un paquet
        self.layer4_outputBlockingCondition.acquire()
        self.layer4_packet_arrived=True
        self.layer4_outputBlockingCondition.notify()
        self.layer4_outputBlockingCondition.release()
        
        self.application_layer_incomingPDU(source,10,pdu)


    # Please adapt
    def layer4_outgoingPDU(self, destination, applicationPort, pdu):

        new_header=NetworkStack.Header(1, destination, NetworkStack.TAILLE_HEADER+1, self.__ownIdentifier, len(pdu))
        #ajout du message mis en paramètre pdu
        new_sous_packet = NetworkStack.SousPaquet(new_header, pdu)

        #des que l'on est informé que l'on a reçu un paquet, on ajoute le message à ce paquet
        while 1 :
            if  self.layer4_packet_arrived==True :
                self.layer4_outputBlockingCondition.acquire()
                self.layer4_packet_arrived=False
                self.layer4_outputBlockingCondition.notify()
                self.layer4_outputBlockingCondition.release()
                break
        
        self.sous_paquet_list.append(new_sous_packet)
        
        print("%s Layer4_out: Sending message (%s) to %s " % (self.__ownIdentifier, pdu, destination))
        self.layer3_outgoingPDU(destination, pdu)

    # Please adapt!
    # The current situation is that in this layer, the network stack takes the decision to forcibly keep the packet
    # because it thinks that it is destined to this computer
    # It also authorizes immediately that a new packet can be put onto the network.
    
    def layer3_incomingPDU(self, interface, pdu):
        # On isole les paquets pour nous en ajoutant les SousPaquets a la liste
        for i in range (0,self.paquet.get_nb_paquets()) :
            if self.paquet.sous_paquets[i].header.dest == self.__ownIdentifier :
                self.sous_paquet_list.append(self.paquet.sous_paquets[i])

        # Création du header et des données
        for elt in self.sous_paquet_list :
            self.header_list.append(elt.header)
            self.data_list.append(elt.data)
                
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
        self.paquet.sous_paquets=[]
        for elt in self.sous_paquet_list :
            self.paquet.sous_paquets.append(elt)
        pdu=self.paquet.to_string_parse()
        
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
        # Parsing du paquet (à faire : paquet_parse)
        paquet = NetworkStack.Paquet.to_paquet_parse(pdu)
        self.paquet=paquet
        # Vérification getnbpaquet : si 0, on forward (layer2_outgoingPDU)
        if paquet.get_nb_paquets() == 0 :
            print("%s a reçu un paquet vide\n" % (self.__ownIdentifier))
            #on informe outgoing que l'on a reçu un paquet
            self.layer4_outputBlockingCondition.acquire()
            self.layer4_packet_arrived=True
            self.layer4_outputBlockingCondition.notify()
            self.layer4_outputBlockingCondition.release()

            #self.layer2_outgoingPDU(interface,pdu)
            
        else :
            # Boucle qui regarde la liste des headers : boolean à vrai si un des mess est pour nous
            print("%s a reçu un paquet non-vide\n" % (self.__ownIdentifier))

            have_message = False
            for i in range (0,paquet.get_nb_paquets()) :
                if paquet.sous_paquets[i].header.dest == self.__ownIdentifier :
                    have_message = True

            # Si on n'a pas de message pour nous on passe direct a 2_outgoing, sinon on passe a 3_in pour traiter le paquet plus en détail
            if have_message == True :
                self.layer3_incomingPDU(interface, pdu)
            else :
                if have_message == False :
                    #on informe outgoing que l'on a reçu un paquet
                    self.layer4_outputBlockingCondition.acquire()
                    self.layer4_packet_arrived=True
                    self.layer4_outputBlockingCondition.notify()
                    self.layer4_outputBlockingCondition.release()
                    self.layer2_outgoingPDU(interface, pdu)
            
            #print("%s Layer2: Received (%s) on Interface %d:  " % (self.__ownIdentifier, pdu, interface))
            #if interface == 0 : # same ring
            #else: # Another Ring, this is for routing, see later
            #    pass

    def layer2_outgoingPDU(self, interface, pdu):
        # Réinitialisation des attributs
        self.header_list=[]
        self.data_list=[]
        self.sous_paquet_list=[]
        self.paquet=NetworkStack.Paquet()

        # Envoi du paquet
        print("%s Layer2: Sending out (%s) via interface %d " % (self.__ownIdentifier, pdu, interface))
        self.__physicalLayer.API_sendData(interface, pdu)
