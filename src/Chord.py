from argparse import ArgumentParser
from twisted.internet import protocol, reactor
from threading import Thread
from pickle import dumps
from pickle import loads
from time import sleep
from math import log
from math import ceil
import hashlib, uuid

class Node:

    ID = 0
    IP = 'localhost'
    port = 8000

    # Means there are about <scale> nodes here.
    scale = 0
    # 2 ** scaleOrder = scale
    scaleOrder = 0

    nickname = 'default'

    # Number of successors or predecessors.
    neighborNum = 2

    successors = [[ID, IP, port, 0]] * neighborNum
    predecessors = [[ID, IP, port, 0]] * neighborNum
    
    knowSomeNeighbors = False
    
    shortcuts = None
    shortcutNum = 0
    # In seconds.
    shortcutInterval = 5
    
    # In seconds.
    throbInterval = 1
    neighborDeathInterval = 10000
    
    running = False

class Chord(protocol.Protocol):
    
    def __init__(self, SendFactory):
        self.factory = SendFactory
    
    def connectionMade(self):

        query = self.factory.query
        if not query == None:
            queryType = query[0]
            self.transport.write(dumps(self.factory.query))
            # Close used connection.
            if not queryType == 3 and not queryType == 5:
                self.transport.loseConnection()
        
    def dataReceived(self, rawData):

        data = loads(rawData)

        react(self.transport, data)

class ChordFactory(protocol.ClientFactory):
    
    def __init__(self, query=None):
        self.query = query
        
    def buildProtocol(self, addr):
        return Chord(self)

class Control(Thread):

    def run(self):
        while Node.running:
            raw = raw_input('Please input your command:\n')
            command = raw.split(' ')
            commandType = command[0]
             
            if commandType == 'show':
                variable = command[1]
                if variable == 'nickname':
                    print(Node.nickname)
                elif variable == 'neighbors':
                    print('Predecessors: ')
                    print(str(Node.predecessors))
                    print('Successors: ')
                    print(str(Node.successors))
                elif variable == 'ID':
                    print(Node.ID)
                elif variable == 'address':
                    print(str([Node.IP, Node.port]))
                elif variable == 'shortcuts':
                    print(str(Node.shortcuts))
                elif variable == 'shortcutNum':
                    print(str(Node.shortcutNum))
 
            elif commandType == 'exit':
                reactor.stop()
                Node.running = False
                 
            elif commandType == 'query':
                queryBody = command[1]
                executorID = long(hashlib.sha1(queryBody).hexdigest(), 16) % Node.scale
                print('Node ' + str(executorID) + ' is responsible for query: ' + str(queryBody))
                query = [1, executorID, Node.IP, Node.port, queryBody, 0]
                reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
                 
            elif commandType == 'test':
                testType = command[1]
                if testType == 9:
                    ID = int(command[2])
                    query = [-testType, ID, Node.ID, Node.port]
                    reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
'''
        output = open("sample.txt","a")
        output.write("\n")
        output.close()
        sleep(20)
        for i in range(10):
            queryBody = str(uuid.uuid1())
            executorID = long(hashlib.sha1(queryBody).hexdigest(), 16) % Node.scale
            sleep(3)
            query = [1, executorID, Node.IP, Node.port, queryBody, 0]
            reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
        print('Control thread is ending.')
        '''

class Throb(Thread):
    
    def run(self):
        counter = 0
        shortcutCounter = 0
        while Node.running:
            sleep(1)
            
            # Chord Throb, <Node.throbInterval> seconds a time.
            counter += 1
            if counter == Node.throbInterval:
                query = [2, Node.ID]
                neighborsIDs = collectNodesIDs(False)
                for neighborID in neighborsIDs:
                    address = getAddressByID(neighborID)
                    reactor.connectTCP(address[0], address[1], ChordFactory(query))
                counter = 0
                
            growBuddies()
                
            # Kill idles
            expurgateNeighbors()
            expurgateShortcuts()

        print('Throbbing thread is ending.')
            
def react(transport, query):
    
    queryType = query[0]
    
    # print('Query received with type: ' + str(queryType))
    
    # Common query.
    if queryType == 1:
        ID = query[1]
        times = query[5] + 1
        if AIsBetweenBAndC(ID, Node.predecessors[0][0], Node.ID):
            # Execute query here.
            senderIP = query[2]
            senderPort = query[3]
            query = [11, Node.ID, times]
            reactor.connectTCP(senderIP, senderPort, ChordFactory(query))
        else:
            target = getTargetByID(ID)[1]
            targetIP = target[1]
            targetPort = target[2]
            query[5] = times
            reactor.connectTCP(targetIP, targetPort, ChordFactory(query))
            
    elif queryType == 11:
        print('Query executed by ' + str(query[1]) + ' through ' + str(query[2]) + ' nodes')
        '''
        output = open("sample.txt","a")
        output.write(str(query[2])+",")
        output.close()
        '''
        
    elif queryType == 2:
        ID = query[1]
        updateAge(ID)
        
    # Ask for neighbor(s).
    elif queryType == 3:

        needPredecessors = query[1]
        numNeeded = query[2]

        if needPredecessors:
            replyNeighbors = Node.predecessors[:numNeeded]
        else:
            replyNeighbors = Node.successors[:numNeeded]

        replyQuery = [300, needPredecessors, numNeeded, replyNeighbors]
        transport.write(dumps(replyQuery))
        
    elif queryType == 300:
        
        needPredecessors = query[1]
        numNeeded = query[2]
        newNeighbors = query[3]
        
        if needPredecessors:
            for i in range(Node.neighborNum - numNeeded, Node.neighborNum):
                Node.predecessors[i] = newNeighbors[i - Node.neighborNum + numNeeded]
        else:
            for i in range(Node.neighborNum - numNeeded, Node.neighborNum):
                Node.successors[i] = newNeighbors[i - Node.neighborNum + numNeeded]
    
    # Someone wants to join.
    elif queryType == 5:
        nickname = query[3]
        query = [500, Node.scale]
        
        # Acknowledge of joining
        transport.write(dumps(query))
        print(nickname + ' is now online.')
        
    # Acknowledge of joining
    elif queryType == 500:
        Node.scale = query[1]
        Node.ID = long(hashlib.sha1(Node.nickname).hexdigest(), 16) % Node.scale
        print('Joining query has been approved.')
        print('Scale of this network: ' + str(Node.scale) + '.')
        print(Node.nickname + '\'s ID: ' + str(Node.ID) + '.')
        
        # Ask for predessor(s) and successor(s).
        query = [8, Node.ID, Node.IP, Node.port]
        transport.write(dumps(query))
        
    # Ask for predessor(s) and successor(s).
    elif queryType == 8:
        print('Node with ID: ' + str(query[1]) + ' arrived.')
        print('Going to update neighbor(s).')
        updateNeighbors(query[1], query[2], query[3])
    
    # Ask for flushing predessor(s) and successor(s).
    elif queryType == 6:
        
        if not Node.knowSomeNeighbors:
            print('Ready to flush neighbor(s).')
            Node.predecessors = query[1]
            Node.successors = query[2]
            Node.knowSomeNeighbors = True
            
            askToUpdateShortcuts()
                
    # Ask who is responsible for a specific ID.
    elif queryType == 9:

        specificID = query[1]
        result = getTargetByID(specificID)
        found = result[0]
        target = result[1]
        targetIP = target[1]
        targetPort = target[2]
        if found:
            askerIP = query[2]
            askerPort = query[3]
            targetID = target[0]
            query = [10, specificID, targetID, targetIP, targetPort]
            reactor.connectTCP(askerIP, askerPort, ChordFactory(query))
        else:
            reactor.connectTCP(targetIP, targetPort, ChordFactory(query))
    
    # Reply of the ID which is responsible for a specific ID.        
    elif queryType == 10:

        specificID = query[1]
        ID = query[2]
        IP = query[3]
        port = query[4]
        i = getIndexBySpecificID(specificID)
        Node.shortcuts[i] = [ID, IP, port, 0]
        
    # Ask someone which is responsible for a specific ID to update its shortcuts.
    elif queryType == 12:

        specificID = query[1]
        result = getTargetByID(specificID, clockwise=False)
        found = result[0]
        target = result[1]
        targetID = target[0]
        if found and targetID == Node.ID:
            power = query[2]
            i = getIndexByPower(power)
            askerID = query[3]
            # Really need to update.
            if AIsBetweenBAndC(specificID, Node.shortcuts[i][0], askerID, False):
                askerIP = query[4]
                askerPort = query[5]
                Node.shortcuts[i] = [askerID, askerIP, askerPort, 0]
        else:
            targetIP = target[1]
            targetPort = target[2]
            reactor.connectTCP(targetIP, targetPort, ChordFactory(query))
        
def expurgateShortcuts():        
    
    for shortcut in Node.shortcuts:
        if shortcut[3] > Node.neighborDeathInterval:
            shortcut[0] = -1
            i = Node.shortcuts.index(shortcut)
            specificID = getSpecificIDByIndex(i)
            query = [9, specificID, Node.IP, Node.port]
            reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
            
def getSpecificIDByIndex(i):
    specificID = Node.ID + 2 ** (Node.scaleOrder + i - Node.shortcutNum)
    if specificID >= Node.scale:
        specificID -= Node.scale
    return specificID

def getIndexByPower(power):
    i = power + Node.shortcutNum - Node.scaleOrder
    return i
        
def getIndexBySpecificID(ID):
    ID -= Node.ID
    if ID < 0:
        ID += Node.scale
    # Strange problem here, ID must be surrounded by parentheses.
    i = int(log(int(ID), 2)) + Node.shortcutNum - Node.scaleOrder
    return i

def askToUpdateShortcuts():

    # Ask who are my shortcuts.
    for i in range(0, Node.shortcutNum):
        specificID = getSpecificIDByIndex(i)
        query = [9, specificID, Node.IP, Node.port]
        reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
        
    # Tell others to update their shortcuts.
    for i in range(0, Node.shortcutNum):
        power = Node.scaleOrder - 1 - i
        IDNeeded = Node.ID - 2 ** power
        if IDNeeded < 0:
            IDNeeded += Node.scale
        query = [12, IDNeeded, power, Node.ID, Node.IP, Node.port]
        reactor.connectTCP(Node.IP, Node.port, ChordFactory(query))
        
def getTargetByID(ID, clockwise=True):

    # First try to find among neighbors.
    if AIsBetweenBAndC(ID, Node.predecessors[0][0], Node.ID, clockwise):
        if clockwise:
            return [True, [Node.ID, Node.IP, Node.port, 0]]
        else:
            return [True, Node.predecessors[0]]
    if AIsBetweenBAndC(ID, Node.ID, Node.successors[0][0], clockwise):
        if clockwise:
            return [True, Node.successors[0]]
        else:
            return [True, [Node.ID, Node.IP, Node.port, 0]]
    for i in range(Node.neighborNum - 1):
        if AIsBetweenBAndC(ID, Node.successors[i][0], Node.successors[i + 1][0], clockwise):
            if clockwise:
                return [True, Node.successors[i + 1]]
            else:
                return [True, Node.successors[i]]
    for i in range(Node.neighborNum - 1):
        if AIsBetweenBAndC(ID, Node.predecessors[i + 1][0], Node.predecessors[i][0], clockwise):
            if clockwise:
                return [True, Node.predecessors[i]]
            else:
                return [True, Node.predecessors[i + 1]]
    
    # Right edge of neighbors and shortcuts.
    A = AIsBetweenBAndC(ID, Node.successors[-1][0], Node.shortcuts[0][0], clockwise)
    B = not Node.successors[-1][0] == Node.shortcuts[0][0]
    C = AIsBetweenBAndC(Node.successors[-1][0], Node.ID, Node.shortcuts[0][0])
    if A and B and C:
        if clockwise:
            found = ID == Node.shortcuts[0][0]
            if found:
                return [found, Node.shortcuts[0]]
            else:
                return [found, Node.successors[-1]]
        else:
            found = ID == Node.successors[-1][0]
            if found:
                return [found, Node.successors[-1]]
            else:
                return [found, Node.shortcuts[0]]
            
    # Try to find among shortcuts.
    for i in range(Node.shortcutNum - 1):
        if Node.shortcuts[i][0] == Node.shortcuts[i + 1][0]:
            continue
        if AIsBetweenBAndC(ID, Node.shortcuts[i][0], Node.shortcuts[i + 1][0], clockwise):
            if clockwise:
                found = ID == Node.shortcuts[i + 1][0]
                if found:
                    return [found, Node.shortcuts[i + 1]]
                else:
                    return [found, Node.shortcuts[i]]
            else:
                found = ID == Node.shortcuts[i][0]
                if found:
                    return [found, Node.shortcuts[i]]
                else:
                    return [found, Node.shortcuts[i + 1]]
                
    # Left edge of neighbors and shortcuts.
    A = AIsBetweenBAndC(ID, Node.shortcuts[-1][0], Node.predecessors[-1][0], clockwise)
    B = not Node.shortcuts[-1][0] == Node.predecessors[-1][0]
    C = AIsBetweenBAndC(Node.predecessors[-1][0], Node.shortcuts[-1][0], Node.ID)
    if A and B and C:
        if clockwise:
            found = ID == Node.predecessors[-1][0]
            if found:
                return [found, Node.predecessors[-1]]
            else:
                return [found, Node.shortcuts[-1]]
        else:
            found = ID == Node.shortcuts[-1][0]
            if found:
                return [found, Node.shortcuts[-1]]
            else:
                return [found, Node.predecessors[-1]]
                
def updateNeighbors(askerID, askerIP, askerPort):
    
    # If already absorbed, return.
    absorbed = checkIfAbsorbed(askerID)
    if absorbed:
        return

    query = [8, askerID, askerIP, askerPort]

    nodeIDs = collectNodesIDs()
    fewNodes = False
    if len(nodeIDs) < Node.neighborNum * 2 + 1:
        fewNodes = True
    
    if fewNodes:
        
        # Inform everyone the novice
        for ID in nodeIDs:
            if not ID == Node.ID:
                address = getAddressByID(ID)
                reactor.connectTCP(address[0], address[1], ChordFactory(query))
            
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
        flushQuery = [6, predecessors, successors]
        reactor.connectTCP(askerIP, askerPort, ChordFactory(flushQuery))
        
    else:
        found = False
        # Check if the novice is among predecessors.
        for ID in range(Node.neighborNum - 1):

            # Find your place!
            if AIsBetweenBAndC(askerID, Node.predecessors[ID + 1][0], Node.predecessors[ID][0]):
                found = True
                
                # Inform neighbor(s) to update their own.
                for indexUpdateQuery in range(Node.neighborNum - 1):
                    rightIndex = ID - indexUpdateQuery
                    leftIndex = ID + 1 + indexUpdateQuery
                    
                    # The right side.
                    if rightIndex > 0:
                        target = Node.predecessors[rightIndex]
                    # Need to send update query to successor(s).
                    else:
                        rightIndex = -rightIndex - 1
                        target = Node.successors[rightIndex]
                    reactor.connectTCP(target[1], target[2], ChordFactory(query))
                    # The left side.
                    if leftIndex < Node.neighborNum:
                        target = Node.predecessors[leftIndex]
                        reactor.connectTCP(target[1], target[2], ChordFactory(query))

                # Update myself
                for indexNeedUpdate in range(Node.neighborNum - 1, ID + 1, -1):
                    Node.predecessors[indexNeedUpdate] = Node.predecessors[indexNeedUpdate - 1]
                Node.predecessors[ID + 1] = [askerID, askerIP, askerPort, 0]
                    
        # If the novice is near this node.
        if AIsBetweenBAndC(askerID, Node.predecessors[0][0], Node.successors[0][0]):
            found = True
            onLeft = AIsBetweenBAndC(askerID, Node.predecessors[0][0], Node.ID)

            for indexNeedUpdate in range(Node.neighborNum - 1):
                target = Node.successors[indexNeedUpdate]
                reactor.connectTCP(target[1], target[2], ChordFactory(query))
                target = Node.predecessors[indexNeedUpdate]
                reactor.connectTCP(target[1], target[2], ChordFactory(query))
            indexNeedUpdate = Node.neighborNum - 1
            if onLeft:
                target = Node.successors[indexNeedUpdate]
            else:
                target = Node.predecessors[indexNeedUpdate]
            reactor.connectTCP(target[1], target[2], ChordFactory(query))
            
            predecessors = list(Node.predecessors)
            successors = list(Node.successors)
            if onLeft:
                for i in range(Node.neighborNum - 2, -1, -1):
                    successors[i + 1] = successors[i]
                successors[0] = [Node.ID, Node.IP, Node.port, 0]
            else:
                for i in range(Node.neighborNum - 2, -1, -1):
                    predecessors[i + 1] = predecessors[i]
                predecessors[0] = [Node.ID, Node.IP, Node.port, 0]
            flushQuery = [6, predecessors, successors]
            reactor.connectTCP(askerIP, askerPort, ChordFactory(flushQuery))

            # Update myself    
            for indexNeedUpdate in range(Node.neighborNum - 1, 0, -1):
                if onLeft:
                    Node.predecessors[indexNeedUpdate] = Node.predecessors[indexNeedUpdate - 1]
                    Node.predecessors[0] = [askerID, askerIP, askerPort, 0]
                else:
                    Node.successors[indexNeedUpdate] = Node.successors[indexNeedUpdate - 1]
                    Node.successors[0] = [askerID, askerIP, askerPort, 0]
                
        # Check if the novice is among successors.
        for ID in range(Node.neighborNum - 1):

            # Find your place!
            if AIsBetweenBAndC(askerID, Node.successors[ID][0], Node.successors[ID + 1][0]):
                found = True
                
                # Inform neighbor(s) to update their own.
                for indexUpdateQuery in range(Node.neighborNum - 1):
                    leftIndex = ID - indexUpdateQuery
                    rightIndex = ID + 1 + indexUpdateQuery
                    
                    # The right side.
                    if leftIndex > 0:
                        target = Node.successors[leftIndex]
                    # Need to send update query to successor(s).
                    else:
                        leftIndex = -leftIndex - 1
                        target = Node.predecessors[leftIndex]
                    reactor.connectTCP(target[1], target[2], ChordFactory(query))
                    # The left side.
                    if rightIndex < Node.neighborNum:
                        target = Node.successors[rightIndex]
                        reactor.connectTCP(target[1], target[2], ChordFactory(query))
                    
                # Update myself
                for indexNeedUpdate in range(Node.neighborNum - 1, ID + 1, -1):
                    Node.successors[indexNeedUpdate] = Node.successors[indexNeedUpdate - 1]
                Node.successors[ID + 1] = [askerID, askerIP, askerPort, 0]
        
        # If this node does not need to update itself.
        if not found:
            target = getTargetByID(askerID)[1]
            reactor.connectTCP(target[1], target[2], ChordFactory(query))
        
def growBuddies():

    for neighbor in Node.predecessors:
        ID = neighbor[0]
        if not ID == Node.ID and not ID == -1:
            neighbor[3] += 1
    for neighbor in Node.successors:
        ID = neighbor[0]
        if not ID == Node.ID and not ID == -1:
            neighbor[3] += 1
    for shortcut in Node.shortcuts:
        ID = shortcut[0]
        if not ID == Node.ID and not ID == -1:
            shortcut[3] += 1

# IF rightClose is true, means if a equals to c, return true.
def AIsBetweenBAndC(a, b, c, rightClose=True):
    # At edge
    if c <= b:
        if a < c:
            return True
        if a > b:
            return True
    else:
        if a < c and a > b:
            return True
    if a == c and rightClose:
        return True
    if a == b and not rightClose:
        return True
    return False

# When there are few nodes, calculate the neighbor(s) of center.
def fewNodesNeighbors(nodes, center):
    indexOfThisNode = nodes.index(center)
    iterator = indexOfThisNode
    predecessors = []
    successors = []
    for i in range(Node.neighborNum):
        iterator += 1
        if iterator >= len(nodes):
            iterator = 0
        successors.append(nodes[iterator])
    iterator = indexOfThisNode
    for i in range(Node.neighborNum):
        iterator -= 1
        if iterator < 0:
            iterator = len(nodes) - 1
        predecessors.append(nodes[iterator])
    return [predecessors, successors]
        
def getAddressByID(ID):
    for node in Node.predecessors:
        if node[0] == ID:
            return [node[1], node[2]]
    for node in Node.successors:
        if node[0] == ID:
            return [node[1], node[2]]
    if ID == Node.ID:
        return [Node.IP, Node.port]
    
def getNeighborByID(ID):
    for node in Node.predecessors:
        if node[0] == ID:
            return node
    for node in Node.successors:
        if node[0] == ID:
            return node
    if ID == Node.ID:
        return [ID, Node.IP, Node.port, 0]

def completeAddressesByIDs(IDs, askerID=None, askerIP=None, askerPort=None):
    result = []
    for ID in IDs:
        neighbor = getNeighborByID(ID)
        # ID is asker's ID
        if neighbor == None:
            result.append(list([askerID, askerIP, askerPort, 0]))
        else:
            result.append(list(neighbor))
    return result
        
def checkIfAbsorbed(askerID):
    
    for predecessor in Node.predecessors:
        if askerID == predecessor[0]:
            return True
    for successor in Node.successors:
        if askerID == successor[0]:
            return True
    if askerID == Node.ID:
        return True
    return False

# Collect every node's ID.
def collectNodesIDs(includeSelf=True):
    nodeIDs = []
    for predecessor in Node.predecessors:
        if not predecessor[0] in nodeIDs and not predecessor[0] == -1:
            nodeIDs.append(predecessor[0])
    for successor in Node.successors:
        if not successor[0] in nodeIDs and not successor[0] == -1:
            nodeIDs.append(successor[0])
    if not Node.ID in nodeIDs and includeSelf:
        nodeIDs.append(Node.ID)
    if not includeSelf:
        for ID in nodeIDs:
            if ID == Node.ID:
                nodeIDs.pop(nodeIDs.index(ID))
    return nodeIDs

def updateAge(ID):

    for predecessor in Node.predecessors:
        if predecessor[0] == ID:
            predecessor[3] = 0
    for successor in Node.successors:
        if successor[0] == ID:
            successor[3] = 0
        
def expurgateNeighbors():

    lastAlivePredecessor = permuteNeighbors(Node.predecessors)
    lastAliveSuccessor = permuteNeighbors(Node.successors)

    predecessorNeeded = Node.neighborNum - 1 - lastAlivePredecessor
    successorNeeded = Node.neighborNum - 1 - lastAliveSuccessor
        
    # This node is dead.
    if predecessorNeeded >= Node.neighborNum or successorNeeded >= Node.neighborNum:
        print('This node can no longer live because too many neighbors dead.')
        Node.running = False
        reactor.stop()
        exit()
    
    if predecessorNeeded > 0:
        query = [3, True, predecessorNeeded]
        target = Node.predecessors[lastAlivePredecessor]
        reactor.connectTCP(target[1], target[2], ChordFactory(query))
    if successorNeeded > 0:
        query = [3, False, successorNeeded]
        target = Node.successors[lastAliveSuccessor]
        reactor.connectTCP(target[1], target[2], ChordFactory(query))

# Return the index of last alive neighbor.
def permuteNeighbors(neighbors):
    deadNeighborIndex = getDeadNeighbor(neighbors)
    lastAliveIndex = Node.neighborNum - 1
    while not deadNeighborIndex == -1:
        lastAliveIndex -= 1
        for i in range(deadNeighborIndex, Node.neighborNum - 1):
            if neighbors[i + 1][0] == -1:
                neighbors[i][0] = -1
                break
            neighbors[i] = list(neighbors[i + 1])
            if i == Node.neighborNum - 2:
                neighbors[i + 1][0] = -1
        deadNeighborIndex = getDeadNeighbor(neighbors)
    return lastAliveIndex

# -1 means all neighbors are healthy
def getDeadNeighbor(neighbors):
    for i in range(Node.neighborNum):
        if neighbors[i][0] == -1:
            break
        if neighbors[i][3] > Node.neighborDeathInterval:
            neighbors[i][0] = -1
            return i
    return -1

def main():

        print('Setup argument parser')
        parser = ArgumentParser()
        parser.add_argument('nickname', help='Identifier in fact')
        parser.add_argument('-s', '--scale', nargs=1, type=int, default=[10])
        parser.add_argument('-i', '--initial', action='store_true', default=False)
        parser.add_argument('--IP', nargs=1, default='localhost')
        parser.add_argument('-p', '--port', nargs=1, type=int, default=[8000])
        
        print('Process arguments.')
        args = parser.parse_args()
        
        print('Node ' + args.nickname + ' is starting.')
        Node.nickname = args.nickname
        Node.scaleOrder = args.scale[0]
        Node.scale = 2 ** Node.scaleOrder
        Node.IP = args.IP
        Node.port = args.port[0]
        Node.shortcutNum = Node.scaleOrder - 1 - int(ceil(log(Node.neighborNum, 2)))
        Node.shortcuts = [[Node.ID, Node.IP, Node.port, 0]] * Node.shortcutNum
        
        reactor.listenTCP(Node.port, ChordFactory())
        print('Ready to listen at port ' + str(Node.port))
        
        if not args.initial:
            query = [5, Node.IP, Node.port, Node.nickname]
            reactor.connectTCP('localhost', 8000, ChordFactory(query))

        Node.running = True

        Control().start()
        
        Throb().start()

        reactor.run()
        
        print('Main thread is ending.')

main()
