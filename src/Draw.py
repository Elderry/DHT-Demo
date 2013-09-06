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
        nid = data[1]
        nextid = data[2]
        e = pygame.event.Event(pygame.USEREVENT,nid=int(nid), query=int(query), nextid=int(nextid))
        pygame.event.post(e)

class DrawFactory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return Draw()

def paint():
    nodeNum = 2 ** 6
    nodelist = []
    r = 300
    pygame.init()
    screen = pygame.display.set_mode([640, 640])
    pygame.display.set_caption('chord demo')
    screen.fill((255,255,255))
    pygame.draw.circle(screen, (128,128,128), [320, 320], r, 1)
    myfont = pygame.font.SysFont("Comic Sans MS", 10)
    clock = pygame.time.Clock()
    for i in range(nodeNum):
        pygame.draw.circle(screen,(0,0,0),(int(320 + r * math.cos(i * 2 * math.pi/nodeNum)),int(320 + r * math.sin(i * 2 * math.pi/nodeNum))),3,0)
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
                        else:
                            pygame.draw.circle(screen,(0,0,0),(int(320 + r * math.cos(i * 2 * math.pi/nodeNum)),int(320 + r * math.sin(i * 2 * math.pi/nodeNum))),3,0)
                        screen.blit(myfont.render(str(i),1,(255,0,0)),(int(320 + (r-20) * math.cos(i * 2 * math.pi/nodeNum)),int(320 + (r-20) * math.sin(i * 2 * math.pi/nodeNum))))
            elif event.type==pygame.USEREVENT:
                nid = event.nid
                query = event.query
                nextid = event.nextid
                if query == 12:
                    nodelist.append(nid)
                    pygame.draw.circle(screen,(0,255,0),(int(320 + r * math.cos(nid * 2 * math.pi/nodeNum)),int(320 + r * math.sin(nid * 2 * math.pi/nodeNum))),5,0)
                elif type == 13:
                    if(nid not in nodelist):
                        pygame.draw.circle(screen,(0,0,255),(int(320 + r * math.cos(nid * 2 * math.pi/nodeNum)),int(320 + r * math.sin(nid * 2 * math.pi/nodeNum))),3,0)
                    pygame.draw.line(screen,(0,0,255),(int(320 + r * math.cos(id * 2 * math.pi/nodeNum)),int(320 + r * math.sin(id * 2 * math.pi/nodeNum))),(int(320 + r * math.cos(nextid * 2 * math.pi/nodeNum)),int(320 + r * math.sin(nextid * 2 * math.pi/nodeNum))))
                else:
                    pass
        pygame.display.update()

if __name__ == '__main__':
    thread.start_new_thread(paint,())
    reactor.listenTCP(9000, DrawFactory())
    reactor.run()
    