
from PhyNetwork import PhyNetwork
from Computer import Computer
import time


if __name__ == '__main__':
    # We try to be the master first
    print("Initiating PhyMaster")
    network=PhyNetwork(baseport=10000, numberOfNodesPerRing=2)
    print("Initiating PhyMaster done")


    computer1=Computer(ownIdentifier="A", sendDestinations=["C"], masterHost='127.0.0.1', baseport=10000)
    computer2=Computer(ownIdentifier="B", sendDestinations=["A"], masterHost='127.0.0.1', baseport=10000)
    computer3=Computer(ownIdentifier="C", sendDestinations=["B"], masterHost='127.0.0.1', baseport=10000)
    #computer4=Computer(ownIdentifier="D", sendDestinations=["A","C"], masterHost='127.0.0.1', baseport=10000)
    #computer5=Computer(ownIdentifier="R", sendDestinations=["A","C"], masterHost='127.0.0.1', baseport=10000)
    time.sleep(2)

    computer1.initiateToken()
