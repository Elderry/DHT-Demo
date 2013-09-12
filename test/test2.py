'''
Created on 2013-8-28

@author: hp
'''

from __future__ import division
import random
import hashlib
import string
import matplotlib.pyplot as plt

'''calculate probability density function(PDF)'''
if __name__ == '__main__':
    nodeNum = 5000
    nodelist = random.sample(range(0,2 ** 13),nodeNum)
    nodelist.sort()
    counterlist = [0 for n in range(nodeNum)]
    for k in range(50 * nodeNum):
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
        sa = []
        '''get key in random'''
        for i in range(1024):
            sa.append(random.choice(seed))
        salt = string.join(sa)
        key = long(hashlib.sha1(salt).hexdigest(), 16) % (2 ** 13)
        '''calculate key number of a node'''
        if key > nodelist[nodeNum - 1]:
            counterlist[0] += 1
        elif key < nodelist[0]:
            counterlist[nodeNum -1] += 1
        else:
            for i in range(nodeNum):
                if nodelist[i] >= key:
                    counterlist[i] += 1
                    break
    x = []
    y = []
    counterlist.sort()
    for item in counterlist:
        if item not in x:
            x.append(item)
            y.append(counterlist.count(item) / nodeNum)
    plt.plot(x,y,'ro-')
    plt.ylim(0,max(y) + 0.005)
    plt.ylabel(r'PDF')
    plt.xlabel(r'keys per node')
    plt.show()
    