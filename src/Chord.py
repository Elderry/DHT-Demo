'''
Entry point here
'''

from argparse import ArgumentParser
from twisted.internet import protocol, reactor
from threading import Thread
from pickle import dumps
from pickle import loads
from random import seed
from random import randint

class Node:

    ID = 0
    IP = 'localhost'
    port = 8000

    # Means there are about 2^scale nodes here.
    scale = 10

    nickname = 'default'

    # Number of successors or predecessors
    segementSize = 2

    successors = [[0, 'localhost', 8000], [0, 'localhost', 8000]]
    predecessors = [[0, 'localhost', 8000], [0, 'localhost', 8000]]

class Send(protocol.Protocol):
    
    def __init__(self, SendFactory):
        self.factory = SendFactory
    
    def connectionMade(self):
        self.transport.write(dumps(self.factory.query))
        
    def dataReceived(self, rawData):

        data = loads(rawData)
        queryType = data[0]
        print('Received a query, type is ' + str(data[0]) + '.')
        react(self.transport, data)

class SendFactory(protocol.ClientFactory):
    
    def __init__(self, query):
        self.query = query
        
    def buildProtocol(self, addr):
        return Send(self)

class Listen(protocol.Protocol):
    
    def dataReceived(self, rawData):
        data = loads(rawData)
        queryType = data[0]
        print('Received a query, type is ' + str(data[0]))
        
        react(self.transport, data)
        
class ListenFactory(protocol.ServerFactory):
    
    def buildProtocol(self, addr):
        return Listen()
    
class Control(Thread):

    def run(self):
        while True:
            raw = raw_input('Please input your command:\n')
            command = raw.split(' ')
            
            if command[0] == 'show':
                if command[1] == 'nickname':
                    print(Node.nickname)
                if command[1] == 'neighbors':
                    print('Predecessors: ')
                    print(str(Node.predecessors))
                    print('Successors: ')
                    print(str(Node.successors))

def react(transport, query):
    
    queryType = query[0]
    
    # Someone wants to join
    if queryType == 5:
        nickname = query[3]
        query = [51, Node.scale]
        
        # Acknowledge of joining
        transport.write(dumps(query))
        print(nickname + ' is now online.')
        
    # Acknowledge of joining
    elif queryType == 51:
        Node.scale = query[1]
        seed(Node.nickname)
        Node.ID = randint(1, Node.scale)
        print('Joining query has been approved.')
        print('Scale of this network: ' + str(Node.scale) + '.')
        print(Node.nickname + '\'s ID: ' + str(Node.ID) + '.')
        
        # Ask for predessor(s) and successor(s).
        query = [8, Node.ID, Node.IP, Node.port]
        transport.write(dumps(query))
        
    # Ask for predessor(s) and successor(s).
    elif queryType == 8:
        print('Node with ID: ' + str(query[1]) + ' arrived.')
        print('Going to update segement.')
        updateNeighbors(query[1], query[2], query[3])
    
    # Ask for flushing predessor(s) and successor(s).
    elif queryType == 81:
        print('Ready to flush segement.')
        Node.predecessors = query[1]
        Node.successors = query[2]
        
def updateNeighbors(askerID, askerIP, askerPort):
    
    # If already updated, return
    if askerID in Node.predecessors or askerID in Node.successors or askerID == Node.ID:
        return
    
    # If true, means nodeIDs number is less than segementSize*2+1.
    fewNodes = False
    for i in range(Node.segementSize - 1, 0, -1):
        if Node.predecessors[i][0] == Node.successors[i][0]:
            fewNodes = True
            break
        
    if fewNodes:
        
        # Collect every node's ID.
        nodeIDs = []
        for predecessor in Node.predecessors:
            if not predecessor[0] in nodeIDs:
                nodeIDs.append(predecessor[0])
        for successor in Node.successors:
            if not successor[0] in nodeIDs:
                nodeIDs.append(successor[0])
                
        # Inform everyone the novice
        for i in nodeIDs:
            if not i == Node.ID:
                query = [8, askerID, askerIP, askerPort]
                target = []
                for node in Node.predecessors:
                    if node[0] == i:
                        target = node
                        break
                for node in Node.predecessors:
                    if node[0] == i:
                        target = node
                        break
                reactor.connectTCP(target[1], target[0], SendFactory(query))
            
        if not Node.ID in nodeIDs:
            nodeIDs.append(Node.ID)
        nodeIDs.append(askerID)
        nodeIDs.sort()
        
        # Update itself
        neighborsIDs = fewNodesNeighbors(nodeIDs, Node.ID)
        Node.predecessors = completeAddressesByIDs(neighborsIDs[0], askerID, askerIP, askerPort)
        Node.successors = completeAddressesByIDs(neighborsIDs[1], askerID, askerIP, askerPort)
        
        # Flush asker
        neighborsIDs = fewNodesNeighbors(nodeIDs, askerID)
        predecessors = completeAddressesByIDs(neighborsIDs[0], askerID, askerIP, askerPort)
        successors = completeAddressesByIDs(neighborsIDs[1], askerID, askerIP, askerPort)
        query = [81, predecessors, successors]
        reactor.connectTCP(askerIP, askerPort, SendFactory(query))
        
    else:
        found = False
        # Check if the novice is among predecessors.
        for i in range(Node.segementSize - 1):

            # Find your place!
            if AIsBetweenBAndC(askerID, Node.predecessors[i + 1], Node.predecessors[i]):
                found = True
                
                # Inform neighbor(s) to update their own.
                query = [8, askerID, askerIP, askerPort]
                for indexUpdateQuery in range(Node.segementSize - 1):
                    rightIndex = i - indexUpdateQuery
                    leftIndex = i + 1 + indexUpdateQuery
                    
                    # The right side.
                    if rightIndex > 0:
                        target = Node.predecessors[rightIndex]
                    # Need to send update query to successor(s).
                    else:
                        rightIndex = -rightIndex - 1
                        target = Node.successors[rightIndex]
                    reactor.connectTCP(target[1], target[2], SendFactory(query))
                    # The left side.
                    if leftIndex < Node.segementSize:
                        target = Node.predecessors[leftIndex]
                        reactor.connectTCP(target[1], target[2], SendFactory(query))

                # Update myself
                for indexNeedUpdate in range(Node.segementSize - 1, i + 1, -1):
                    Node.predecessors[indexNeedUpdate] = Node.predecessors[indexNeedUpdate - 1]
                Node.predecessors[i + 1] = [askerID, askerIP, askerPort]
                    
        # If the novice is near this node.
        if AIsBetweenBAndC(Node.predecessors[0], Node.successors[0]):
            found = True
            onLeft = AIsBetweenBAndC(askerID, Node.predecessors[0], Node.ID)

            for indexNeedUpdate in range(Node.segementSize - 1):
                query = [8, askerID, askerIP, askerPort]
                target = Node.successors[indexNeedUpdate]
                reactor.connectTCP(target[1], target[2], SendFactory(query))
                target = Node.predecessors[indexNeedUpdate]
                reactor.connectTCP(target[1], target[2], SendFactory(query))
            indexNeedUpdate = Node.segementSize - 1
            if onLeft:
                target = Node.successors[indexNeedUpdate]
            else:
                target = Node.predecessors[indexNeedUpdate]
            reactor.connectTCP(target[1], target[2], SendFactory(query))
            
            if onLeft:
                predecessors = list(Node.predecessors)
                predecessors[0] = [Node.ID, Node.IP, Node.port]
            else:
                successors = list(Node.successors)
                successors[0] = [Node.ID, Node.IP, Node.port]
            flushQuery = [81, predecessors, successors]
            reactor.connectTCP(askerIP, askerPort, SendFactory(flushQuery))

            # Update myself    
            for indexNeedUpdate in range(Node.segementSize - 1, 0, -1):
                if onLeft:
                    Node.predecessors[indexNeedUpdate] = Node.predecessors[indexNeedUpdate - 1]
                    Node.predecessors[0] = [askerID, askerIP, askerPort]
                else:
                    Node.successors[indexNeedUpdate] = Node.successors[indexNeedUpdate - 1]
                    Node.successors[0] = [askerID, askerIP, askerPort]
                
        # Check if the novice is among successors.
        for i in range(Node.segementSize - 1):

            # Find your place!
            if AIsBetweenBAndC(askerID, Node.successors[i], Node.successors[i + 1]):
                found = True
                
                # Inform neighbor(s) to update their own.
                query = [8, askerID, askerIP, askerPort]
                for indexUpdateQuery in range(Node.segementSize - 1):
                    leftIndex = i - indexUpdateQuery
                    rightIndex = i + 1 + indexUpdateQuery
                    
                    # The right side.
                    if leftIndex > 0:
                        target = Node.successors[leftIndex]
                    # Need to send update query to successor(s).
                    else:
                        leftIndex = -leftIndex - 1
                        target = Node.predecessors[leftIndex]
                    reactor.connectTCP(target[1], target[2], SendFactory(query))
                    # The left side.
                    if rightIndex < Node.segementSize:
                        target = Node.successors[rightIndex]
                        reactor.connectTCP(target[1], target[2], SendFactory(query))
                    
                # Update myself
                for indexNeedUpdate in range(Node.segementSize - 1, i + 1, -1):
                    Node.successors[indexNeedUpdate] = Node.successors[indexNeedUpdate - 1]
                Node.successors[i + 1] = [askerID, askerIP, askerPort]
        
        # If this node does not need to update itself.
        if not found:
            target = Node.predecessors[-1]
            reactor.connectTCP(target[1], target[2], SendFactory(query))
            target = Node.successors[-1]
            reactor.connectTCP(target[1], target[2], SendFactory(query))
        
def AIsBetweenBAndC(a, b, c):
    if c < b:
        c += Node.scale
    if a < c and a > b:
        return True
    else:
        return c
    
# When there are few nodes, calculate the segement of center.
def fewNodesNeighbors(nodes, center):
    indexOfThisNode = nodes.index(center)
    iterator = indexOfThisNode
    predecessors = []
    successors = []
    for i in range(Node.segementSize):
        iterator += 1
        if iterator >= Node.segementSize:
            iterator = 0
        successors.append(nodes[iterator])
    iterator = indexOfThisNode
    for i in range(Node.segementSize):
        iterator -= 1
        if iterator < 0:
            iterator = Node.segementSize - 1
        predecessors.append(nodes[iterator])
    return [predecessors, successors]
        
def getAddressByID(ID):
    for node in Node.predecessors:
        if node[0] == ID:
            return [node[1], node[2]]
    for node in Node.successors:
        if node[0] == ID:
            return [node[1], node[2]]

def completeAddressesByIDs(IDs, askerID=None, askerIP=None, askerPort=None):
    result = []
    for ID in IDs:
        address = getAddressByID(ID)
        # ID is asker's ID
        if address==None:
            result.append([askerID, askerIP, askerPort])
        else:
            result.append([ID, address[0], address[1]])
    return result
        
def main():

        print('Setup argument parser')
        parser = ArgumentParser()
        parser.add_argument('nickname', help='Identifier in fact')
        parser.add_argument('-s', '--scale', nargs=1, type=int, default=10)
        parser.add_argument('-i', '--initial', action='store_true', default=False)
        parser.add_argument('--IP', nargs=1, default='localhost')
        parser.add_argument('-p', '--port', nargs=1, type=int, default=[8000])
        
        print('Process arguments.')
        args = parser.parse_args()
        
        print('Node ' + args.nickname + ' is starting.')
        Node.nickname = args.nickname
        Node.scale = 2 ** args.scale
        Node.IP = args.IP
        Node.port = args.port[0]
        
        Control().start()
        
        reactor.listenTCP(Node.port, ListenFactory())
        print('Ready to listen at port ' + str(Node.port))
        
        if not args.initial:
            query = [5, Node.IP, Node.port, Node.nickname]
            reactor.connectTCP('localhost', 8000, SendFactory(query))

        reactor.run()

main()
