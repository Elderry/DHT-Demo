'''
Created on 2013-9-6

@author: hp
'''

import pygame
import sys
import math
import thread
import hashlib
from twisted.internet import protocol, reactor
from pickle import loads
from pickle import dumps

class Draw(protocol.Protocol):

    def __init__(self, DrawFactory):
        self.factory = DrawFactory
        
    def connectionMade(self):

        query = self.factory.query
        if not query == None:
            self.transport.write(dumps(self.factory.query))
            # Close used connection.
            self.transport.loseConnection()

    def dataReceived(self, rawData):
        data = loads(rawData)
        query = data[0]
        if query == 12:
            nid = data[1]
            nip = data[2]
            nport = data[3]
            e = pygame.event.Event(pygame.USEREVENT, nid=nid, query=query , nip=nip, nport=nport)
            pygame.event.post(e)
        elif query == 13:
            nid = data[2]
            nextid = data[1]
            e = pygame.event.Event(pygame.USEREVENT, nid=nid, query=query, nextid=int(nextid))
            pygame.event.post(e)

class DrawFactory(protocol.ClientFactory):

    def __init__(self, query=None):
        self.query = query
        
    def buildProtocol(self, addr):
        return Draw(self)

def paint():
    nodeNum = 2 ** 16
    nodelist = {'nid':[], 'nip':[], 'nport':[]}
    rectlist = []
    getInput = False
    targetId = 0;
    queryString = ''
    r = 300
    pygame.init()
    screen = pygame.display.set_mode([640, 680])
    pygame.display.set_caption('chord demo')
    screen.fill((255, 255, 255))
    rect = pygame.draw.circle(screen, (128, 128, 128), [320, 320], r, 1)
    myfont = pygame.font.SysFont("Comic Sans MS", 10)
    font = pygame.font.SysFont(None, 30)
    clock = pygame.time.Clock()
    nodelist['nid'].append(0)
    nodelist['nip'].append('127.0.0.1')
    nodelist['nport'].append(8470)
    rectlist.append(rect)
    for i in range(nodeNum):
        if i in nodelist['nid']:
            pygame.draw.circle(screen, (0, 255, 0), (int(320 + r * math.cos(i * 2 * math.pi / nodeNum)), int(320 + r * math.sin(i * 2 * math.pi / nodeNum))), 5, 0)     
            screen.blit(myfont.render(str(i), 1, (255, 0, 0)), (int(320 + (r - 20) * math.cos(i * 2 * math.pi / nodeNum)), int(320 + (r - 20) * math.sin(i * 2 * math.pi / nodeNum))))
    targetRect = (20, 630, 30, 30)
    queryRect = (70, 630, 550, 30)
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(rectlist)):
                    if rectlist[i].collidepoint(pygame.mouse.get_pos()):
                        getInput = True
                        targetId = nodelist['nid'][i]
                        screen.fill((255, 255, 255), targetRect)
                        screen.fill((255, 255, 255), queryRect)
                        teargetText = font.render(str(targetId), 12, (255, 0, 0))
                        screen.blit(teargetText, targetRect)                        
                        queryString = ''
            elif event.type == pygame.KEYDOWN:
                if getInput:
                    if event.key == pygame.K_ESCAPE:
                        queryString = ''
                        screen.fill((255, 255, 255), queryRect)
                    elif event.key == pygame.K_KP_ENTER:
                        getInput = False
                        executorID = long(hashlib.sha1(queryString).hexdigest(), 16) % nodeNum
                        pygame.draw.circle(screen, (0, 255, 255), (int(320 + r * math.cos(executorID * 2 * math.pi / nodeNum)), int(320 + r * math.sin(executorID * 2 * math.pi / nodeNum))), 3, 0)
                        screen.blit(myfont.render(str(executorID), 1, (255, 0, 0)), (int(320 + (r - 20) * math.cos(executorID * 2 * math.pi / nodeNum)), int(320 + (r - 20) * math.sin(executorID * 2 * math.pi / nodeNum))))
                        i = nodelist['nid'].index(targetId)
                        query = [1, executorID, nodelist['nip'][i], nodelist['nport'][i], queryString, 0]
                        reactor.connectTCP(nodelist['nip'][i], nodelist['nport'][i], DrawFactory(queryString))
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        if len(queryString) > 0:
                            queryString = queryString[:-1]
                            queryText = font.render(queryString, 12, (255, 0, 0))
                            screen.fill((255, 255, 255), queryRect)
                            screen.blit(queryText, queryRect)
                    elif event.key <= 127:
                        screen.fill((255, 255, 255), queryRect)
                        queryString += chr(event.key)
                        queryText = font.render(queryString, 12, (255, 0, 0))
                        screen.blit(queryText, queryRect)
                else:
                    if event.key == pygame.K_SPACE:
                        screen.fill((255, 255, 255))
                        pygame.draw.circle(screen, (128, 128, 128), [320, 320], r, 1)
                        for i in range(nodeNum):
                            if i in nodelist['nid']:
                                pygame.draw.circle(screen, (0, 255, 0), (int(320 + r * math.cos(i * 2 * math.pi / nodeNum)), int(320 + r * math.sin(i * 2 * math.pi / nodeNum))), 5, 0)
                                screen.blit(myfont.render(str(i), 1, (255, 0, 0)), (int(320 + (r - 20) * math.cos(i * 2 * math.pi / nodeNum)), int(320 + (r - 20) * math.sin(i * 2 * math.pi / nodeNum))))
            elif event.type == pygame.USEREVENT:
                nid = event.nid
                query = event.query
                nip = event.nip
                nport = event.nport
                if query == 12:
                    nodelist['nid'].append(nid)
                    nodelist['nip'].append(nip)
                    nodelist['nport'].append(nport)
                    pygame.draw.circle(screen, (0, 255, 0), (int(320 + r * math.cos(nid * 2 * math.pi / nodeNum)), int(320 + r * math.sin(nid * 2 * math.pi / nodeNum))), 5, 0)
                    screen.blit(myfont.render(str(nid), 1, (255, 0, 0)), (int(320 + (r - 20) * math.cos(nid * 2 * math.pi / nodeNum)), int(320 + (r - 20) * math.sin(nid * 2 * math.pi / nodeNum))))
                elif query == 13:
                    nextid = event.nextid
                    if(nid not in nodelist['nid']):
                        pygame.draw.circle(screen, (0, 0, 255), (int(320 + r * math.cos(nid * 2 * math.pi / nodeNum)), int(320 + r * math.sin(nid * 2 * math.pi / nodeNum))), 3, 0)
                    x1 = int(320 + r * math.cos(nid * 2 * math.pi / nodeNum))
                    y1 = int(320 + r * math.sin(nid * 2 * math.pi / nodeNum))
                    x2 = int(320 + r * math.cos(nextid * 2 * math.pi / nodeNum))
                    y2 = int(320 + r * math.sin(nextid * 2 * math.pi / nodeNum))
                    pygame.draw.line(screen, (0, 0, 255), (x1, y1), (x2, y2))
                    lx = math.cos(math.pi / 6) * (x2 - x1) - (y2 - y1) / 2
                    ly = math.cos(math.pi / 6) * (y2 - y1) + (x2 - x1) / 2
                    l = math.sqrt(lx * lx + ly * ly)
                    x3 = lx / l * 20
                    y3 = ly / l * 20
                    pygame.draw.line(screen, (0, 0, 255), (x2, y2), (x2 - x3, y2 - y3))
                    lx = math.cos(math.pi / 6) * (x2 - x1) + (y2 - y1) / 2
                    ly = math.cos(math.pi / 6) * (y2 - y1) - (x2 - x1) / 2
                    l = math.sqrt(lx * lx + ly * ly)
                    x4 = lx / l * 20
                    y4 = ly / l * 20
                    pygame.draw.line(screen, (0, 0, 255), (x2, y2), (x2 - x4, y2 - y4))
                else:
                    pass
        pygame.display.update()

if __name__ == '__main__':
    thread.start_new_thread(paint, ())
    reactor.listenTCP(9000, DrawFactory())
    reactor.run()
    
