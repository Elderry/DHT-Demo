'''
Created on 2013-9-6

@author: hp
'''

import pygame
import sys
import math
import thread
from twisted.internet import protocol, reactor
from pickle import loads

class Draw(protocol.Protocol):
    def dataReceived(self, rawData):
        data=loads(rawData)
        query = data[0]
        if query == 12:
            nid = data[1]
            e = pygame.event.Event(pygame.USEREVENT,nid=nid, query=query)
            pygame.event.post(e)
        elif query == 13:
            nid = data[2]
            nextid = data[1]
            e = pygame.event.Event(pygame.USEREVENT,nid=nid, query=query, nextid=int(nextid))
            pygame.event.post(e)

class DrawFactory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return Draw()

def paint():
    nodeNum = 2 ** 16
    nodelist = []
    r = 300
    pygame.init()
    screen = pygame.display.set_mode([640, 640])
    pygame.display.set_caption('chord demo')
    screen.fill((255,255,255))
    pygame.draw.circle(screen, (128,128,128), [320, 320], r, 1)
    myfont = pygame.font.SysFont("Comic Sans MS", 10)
    clock = pygame.time.Clock()
    nodelist.append(0)
    for i in range(nodeNum):
        if i in nodelist:
            pygame.draw.circle(screen,(0,255,0),(int(320 + r * math.cos(i * 2 * math.pi/nodeNum)),int(320 + r * math.sin(i * 2 * math.pi/nodeNum))),5,0)     
            screen.blit(myfont.render(str(i),1,(255,0,0)),(int(320 + (r-20) * math.cos(i * 2 * math.pi/nodeNum)),int(320 + (r-20) * math.sin(i * 2 * math.pi/nodeNum))))
    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:  
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    screen.fill((255,255,255))
                    pygame.draw.circle(screen, (128,128,128), [320, 320], r, 1)
                    for i in range(nodeNum):
                        if i in nodelist:
                            pygame.draw.circle(screen,(0,255,0),(int(320 + r * math.cos(i * 2 * math.pi/nodeNum)),int(320 + r * math.sin(i * 2 * math.pi/nodeNum))),5,0)
                            screen.blit(myfont.render(str(i),1,(255,0,0)),(int(320 + (r-20) * math.cos(i * 2 * math.pi/nodeNum)),int(320 + (r-20) * math.sin(i * 2 * math.pi/nodeNum))))
            elif event.type==pygame.USEREVENT:
                nid = event.nid
                query = event.query
                if query == 12:
                    nodelist.append(nid)
                    pygame.draw.circle(screen,(0,255,0),(int(320 + r * math.cos(nid * 2 * math.pi/nodeNum)),int(320 + r * math.sin(nid * 2 * math.pi/nodeNum))),5,0)
                    screen.blit(myfont.render(str(nid),1,(255,0,0)),(int(320 + (r-20) * math.cos(nid * 2 * math.pi/nodeNum)),int(320 + (r-20) * math.sin(nid * 2 * math.pi/nodeNum))))
                elif query == 13:
                    nextid = event.nextid
                    if(nid not in nodelist):
                        pygame.draw.circle(screen,(0,0,255),(int(320 + r * math.cos(nid * 2 * math.pi/nodeNum)),int(320 + r * math.sin(nid * 2 * math.pi/nodeNum))),3,0)
                    x1 = int(320 + r * math.cos(nid * 2 * math.pi/nodeNum))
                    y1 = int(320 + r * math.sin(nid * 2 * math.pi/nodeNum))
                    x2 = int(320 + r * math.cos(nextid * 2 * math.pi/nodeNum))
                    y2 = int(320 + r * math.sin(nextid * 2 * math.pi/nodeNum))
                    pygame.draw.line(screen,(0,0,255),(x1,y1),(x2,y2))
                    lx = math.cos(math.pi/6)*(x2 - x1) - (y2 - y1) /2
                    ly = math.cos(math.pi/6)*(y2 - y1) + (x2 - x1) /2
                    l = math.sqrt(lx * lx + ly * ly)
                    x3 = lx/l * 10
                    y3 = ly/l * 10
                    pygame.draw.line(screen,(0,0,255),(x2,y2),(x2-x3,y2-y3))
                    lx = math.cos(math.pi/6)*(x2 - x1) + (y2 - y1) /2
                    ly = math.cos(math.pi/6)*(y2 - y1) - (x2 - x1) /2
                    l = math.sqrt(lx * lx + ly * ly)
                    x4 = lx/l * 10
                    y4 = ly/l * 10
                    pygame.draw.line(screen,(0,0,255),(x2,y2),(x2-x4,y2-y4))
                else:
                    pass
        pygame.display.update()

if __name__ == '__main__':
    thread.start_new_thread(paint,())
    reactor.listenTCP(9000, DrawFactory())
    reactor.run()
    