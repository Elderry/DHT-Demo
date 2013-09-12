'''
Created on 2013-9-8

@author: hp
'''
import random
import math
import numpy as np
import matplotlib.pyplot as plt

'''simulate throughput of each node by sending queries in normal distribution'''
if __name__ == '__main__':
    nodeNum = 100
    keyNum = 100 * nodeNum
    scale = 1024 * 2 * 2
    virNodeNum = 10
    nodelist = random.sample(range(0,scale),nodeNum * virNodeNum)
    nodelist.sort()
    key = []
    value = []
    mapped = [0 for n in range(keyNum)]
    for i in range(keyNum):
        x = int(math.fabs(random.normalvariate(5000, 1600)))
        key.append( x % keyNum)
        y = int(math.fabs(random.normalvariate(0, 100)))
        value.append( y % keyNum)
    for i in range(keyNum):
        if (key[i] % scale) > nodelist[nodeNum * virNodeNum -1]:
            mapped[i] = 0
        elif (key[i] % scale) < nodelist[0]:
            mapped[i] = nodeNum * virNodeNum -1
        else:
            for j in range(nodeNum * virNodeNum):
                if nodelist[j] >= (key[i] % scale):
                    mapped[i] = j
                    break
    for i in range(keyNum):
        mapped[i] /= virNodeNum
    valuelist = [[] for n in range(nodeNum)]
    for num in range(keyNum):
        tmp = random.randint(0, 9999)
        if len(valuelist[0]):
            for i in range(nodeNum): 
                last = valuelist[i][len(valuelist[i]) -1]
                if i == mapped[tmp]:
                    valuelist[i].append(value[tmp] + last)
                else:
                    valuelist[i].append(last)
        else:
            for i in range(nodeNum):
                if i == mapped[tmp]:
                    valuelist[i].append(value[tmp])
                else:
                    valuelist[i].append(0)
    for i in range(nodeNum):
        plt.plot(range(1,keyNum+1),valuelist[i])
    plt.ylabel(r'values')
    plt.xlabel(r'time')
    plt.ylim(0, 50000)
    plt.show()